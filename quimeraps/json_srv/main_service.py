"""main_service module."""

from werkzeug import serving, wrappers

from pyreportjasper import report, config as jasper_config  # type: ignore [import]
import ghostscript  # type: ignore [import]
from quimeraps.json_srv import data as data_module
from quimeraps.json_srv import logging
from quimeraps import __VERSION__, DATA_DIR

from jsonrpc import JSONRPCResponseManager, dispatcher  # type: ignore [import]
import os
import tempfile
import locale
import sys
import json

from typing import Dict, List, Optional, Union, Any

CONN: "data_module.SQLiteClass"

LOGGER = logging.getLogger(__name__)


class JsonClass:
    """JsonClass class."""

    def run(self):
        """Start sjon service."""
        global CONN
        LOGGER.info("QuimeraPS service v.%s starts." % (__VERSION__))
        CONN = data_module.SQLiteClass()
        serving.run_simple("0.0.0.0", 4000, self.service)

    @wrappers.Request.application  # type: ignore  [arg-type]
    def service(self, request) -> "wrappers.Response":
        """Json service."""
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        # data_request = request.data
        found_error = False
        try:
            data_response = wrappers.Response(response.json, mimetype="application/json")
            json_response = json.loads(data_response.response[0])
            if json_response["result"]["response"]["result"] == 1:
                found_error = True

        except Exception as error:
            data_response = wrappers.Response({"error": error}, mimetype="application/json")
            found_error = True
        # TODO: meterlo en historial data_request y data response.
        data_response.access_control_allow_origin = "*"
        if found_error:
            data_response.status_code = 400

        return data_response

    def __del__(self):
        """Delete proccess."""
        LOGGER.info("QuimeraPS service stops.")


@dispatcher.add_method
def requestDispatcher(**kwargs):
    """Dispatch print requests."""
    return {"response": processRequest(**kwargs)}


def processRequest(**kwargs) -> Dict[str, Any]:
    """Process print request."""
    is_error: bool = False
    data_or_str: Union[str, List[Any]] = ""

    if "type" in kwargs.keys():
        type_ = kwargs["type"]
        # LOGGER.warning("NEW %s!" % (type_))
        if type_ == "new_job":
            data_or_str = printerRequest(**kwargs["arguments"])
            is_error = data_or_str != ""
        elif type_ == "alive":
            data_or_str = aliveRequest()
        elif type_ == "data":
            data_or_str = dataRequest(**kwargs["arguments"])
        else:
            LOGGER.warning("Unknown request %s!" % (type_))

    else:
        is_error = True
        data_or_str = "type field is not defined"

    return {"result": 1 if is_error else 0, "data": data_or_str}


def aliveRequest() -> str:
    """Return a alive string."""
    return __VERSION__


def dataRequest(**kwargs) -> List[Any]:
    """Return data from database connection."""
    global CONN

    result: str = ""

    # table_name = kwargs['table'] if 'table' in kwargs.keys() else ""
    mode = kwargs["mode"]

    # fields = kwargs['fields'] if 'fields' in kwargs.keys() else ['*']
    # pk = kwargs['pk'] if 'pk' in kwargs.keys() else '1 = 1'
    # values = kwargs['values'] if 'values' in kwargs.keys() else []
    raw_text = kwargs["raw"] if "raw" in kwargs.keys() else ""
    with_response = (
        True if "with_response" in kwargs.keys() and kwargs["with_response"] == 1 else False
    )
    result = "ok"
    try:
        if mode == "raw":
            try:
                query_cursor = CONN.executeQuery(raw_text)
                # print("CALLING!", raw_text)
                if with_response:
                    result = query_cursor.fetchall()
                query_cursor.close()
            except Exception as error:
                result = str(error)
        else:
            result = "unknown mode (%s)" % mode
    except Exception as error:
        result = str(error)

    return [{"error": result}] if isinstance(result, str) else result


def printerRequest(**kwargs) -> str:
    """Print requests."""
    result = ""

    kwargs_names = kwargs.keys()
    for name in ["printer"]:
        if name not in kwargs_names:
            result = "%s field not specified" % name

    if "model" not in kwargs_names:
        kwargs["model"] = ""

    if "data" not in kwargs_names:
        kwargs["data"] = []

    if not result:
        if "cut" not in kwargs_names:
            kwargs["cut"] = False
        if "open_cash_drawer" not in kwargs_names:
            kwargs["open_cash_drawer"] = False

        try:
            result = launchPrinter(
                kwargs["printer"],
                kwargs["model"],
                kwargs["cut"],
                kwargs["open_cash_drawer"],
                kwargs["data"],
            )
        except Exception as error:
            result = str(error)

    return result


def resolvePrinter(printer_alias: str):
    """Resolve printer name using alias."""
    global CONN

    printer_cursor = CONN.executeQuery(
        "SELECT name,cut,cash_drawer FROM printers WHERE alias='%s'" % printer_alias
    )
    if printer_cursor.rowcount:
        result = printer_cursor.fetchone()
        printer_cursor.close()
        return result

    return None


def resolveModel(model_alias: str):
    """Resolve model file usign alias."""
    global CONN

    model_cursor = CONN.executeQuery(
        "SELECT name,copies FROM models WHERE alias='%s'" % model_alias
    )
    if model_cursor.rowcount:
        result = model_cursor.fetchone()
        model_cursor.close()

        return result

    return None


def launchPrinter(
    printer_alias: str, model_alias: str, cut: bool, open_cd: bool, data: List[Any], copies: int = 0
) -> str:
    """Print a request."""
    result = ""
    # resolver nombre impresora
    printer_data = resolvePrinter(printer_alias)
    if not printer_data:
        result = "Printer alias (%s) doesn't exists!" % printer_alias
        LOGGER.warning(result)

    # resolver nomber model
    if not result:
        model_data = resolveModel(model_alias)
        if not model_data:
            result = "Model alias (%s) doesn't exists!" % model_alias
            LOGGER.warning(result)

    if not result and not data:
        result = "Data (%s) is empty" % data
        LOGGER.warning(result)

    if not result:  # Si no hay fallo previo
        # crear request
        printer_name = printer_data[0]
        cut_command: Optional[str] = printer_data[1] if cut and printer_data[1] else None
        open_command: Optional[str] = printer_data[2] if open_cd and printer_data[2] else None
        model_name = model_data[0]
        num_copies = copies if copies else int(model_data[1]) if model_data[1] else 1

        reports_dir = os.path.join(os.path.abspath(DATA_DIR), "reports")
        if not os.path.exists(reports_dir):
            LOGGER.warning("Making reports folder (%s)" % reports_dir)
            os.mkdir(reports_dir)

        input_file = "%s.jrxml" % os.path.join(reports_dir, "%s" % model_name)

        if not os.path.exists(input_file):
            result = "Model (%s) doesn't exists!" % input_file
            LOGGER.warning(result)
        else:
            output_file = tempfile.mktemp()
            output_file_pdf = output_file + ".pdf"

            # generamos temporal con datos json
            temp_json_file = tempfile.mktemp(".json")
            file_ = open(temp_json_file, "w", encoding="UTF-8")
            file_.write(str({"query": {"registers": data}}))
            file_.close()

            if not os.path.exists(temp_json_file):
                result = "JSON file (%s) doesn't exists!" % temp_json_file
                LOGGER.warning(result)
            else:
                LOGGER.info(
                    "json :%s, jasper: %s, result: %s"
                    % (temp_json_file, input_file, output_file_pdf)
                )

                try:
                    config = jasper_config.Config()
                    config.input = input_file
                    config.output = output_file
                    config.dataFile = temp_json_file
                    config.locale = "es_ES"
                    config.dbType = "json"
                    config.jsonQuery = "query.registers"
                    config.params = {
                        "SUBREPORT_DIR": "%s%s"
                        % (
                            os.path.join(DATA_DIR, "subreports"),
                            "\\" if sys.platform.startswith("win") else "/",
                        )
                    }
                    LOGGER.info("Starting reports server %s" % config.input)
                    instance = report.Report(config, config.input)
                    LOGGER.info("Filling %s" % config.input)
                    LOGGER.warning("default %s" % instance.defaultLocale)

                    instance.fill()
                    instance.export_pdf()

                    for num in range(num_copies):
                        LOGGER.info(
                            "Sendign copy %s, printer: %s, model: %s"
                            % (num + 1, printer_name, model_name)
                        )
                        result = sendToPrinter(printer_name, output_file_pdf)

                        # lanza corte
                        if not result and cut_command:
                            temp_cut_file: str = tempfile.mktemp(".esc_command")
                            file_cut = open(temp_cut_file, "b")
                            file_cut.write(cut_command.encode())
                            file_cut.close()
                            result = sendToPrinter(printer_name, temp_cut_file)

                        if result:
                            break
                    # lanza cajon
                    if not result and open_command:
                        temp_open_file: str = tempfile.mktemp(".esc_command")
                        file_cut = open(temp_open_file, "b")
                        file_cut.write(open_command.encode())
                        file_cut.close()
                        result = sendToPrinter(printer_name, temp_open_file)
                except Exception as error:
                    result = "Error: %s" % str(error)
                    LOGGER.warning(result)
    LOGGER.info(result)
    return result


def sendToPrinter(printer: str, file_name):
    """Send document to printer."""
    result = ""
    LOGGER.debug("Sending to printer '%s' -> %s" % (printer, file_name))
    if sys.platform.startswith("win"):
        args = [
            "-dPrinted",
            "-dBATCH",
            "-dNOSAFER",
            "-dNOPAUSE",
            "-dNOPROMPT" "-q",
            "-dNumCopies#1",
            "-sDEVICE#mswinpr2",
            f'-sOutputFile#"%printer%{printer}"',
            f'"{file_name}"',
        ]

        try:
            encoding = locale.getpreferredencoding()
            args = [a.encode(encoding) for a in args]
            LOGGER.debug("Launching GS command with arguments %s" % args)
            LOGGER.debug(ghostscript.Ghostscript(*args))
            LOGGER.debug("STEP 10")
        except Exception as error:
            result = str(error)

    else:
        try:
            os.system("lp -d %s %s" % (printer, file_name))
        except Exception as error:
            result = str(error)

    return result
