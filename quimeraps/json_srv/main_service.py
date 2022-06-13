"""main_service module."""

import os
import tempfile
import locale
import sys
import json
import base64
from typing import Dict, List, Optional, Union, Any
from werkzeug import serving, wrappers

from pyreportjasper import report, config as jasper_config  # type: ignore [import]
import ghostscript  # type: ignore [import]
from jsonrpc import JSONRPCResponseManager, dispatcher  # type: ignore [import]
from quimeraps.json_srv import data as data_module
from quimeraps.json_srv import logging
from quimeraps import __VERSION__, DATA_DIR


CONN: "data_module.SQLiteClass"

LOGGER = logging.getLogger(__name__)


class JsonClass:
    """JsonClass class."""

    def run(self):
        """Start sjon service."""
        global CONN
        LOGGER.info("QuimeraPS service v.%s starts." % (__VERSION__))
        CONN = data_module.SQLiteClass()
        ssl_context_ = None
        cert_dir = os.path.join(os.path.abspath(DATA_DIR), "cert")

        if os.path.exists(cert_dir):
            cert_file = os.path.join(cert_dir, "ssl.cert")
            cert_key_file = os.path.join(cert_dir, "ssl.key")
            if os.path.exists(cert_key_file):
                ssl_context_ = (cert_file, cert_key_file)
            else:
                ssl_context_ = "adhoc"
        LOGGER.info(
            "Using SSL: %s, adhoc: %s, files: %s"
            % (ssl_context_ is not None, isinstance(ssl_context_, str), ssl_context_)
        )
        serving.run_simple("0.0.0.0", 4000, self.service, ssl_context=ssl_context_)

    @wrappers.Request.application  # type: ignore  [arg-type]
    def service(self, request) -> "wrappers.Response":
        """Json service."""
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        # data_request = request.data
        found_error = False
        json_response = {}
        try:
            data_response = wrappers.Response(
                response.json, mimetype="application/json"
            )
            json_response = json.loads(data_response.response[0])
            # LOGGER.warning("Request: %s, Response: %s" % (request.data, json_response))
            if "result" not in json_response:
                found_error = True
                LOGGER.warning(
                    "Error resolving request: %s,data_received: %s, dispatcher: %s, data_response: %s "
                    % (request, request.data, dispatcher, data_response.response[0])
                )
            elif json_response["result"]["response"]["result"] == 1:
                found_error = 1

        except Exception as error:
            data_response = wrappers.Response(
                {"error": error}, mimetype="application/json"
            )
            LOGGER.warning("Error %s" % str(error))
            found_error = True
        # TODO: meterlo en historial data_request y data response.
        data_response.access_control_allow_origin = "*"
        data_response.access_control_allow_methods = ["POST", "OPTIONS"]
        data_response.access_control_allow_headers = ["Content-Type"]
        if found_error:
            data_response.status_code = 400

        return data_response

    def __del__(self):
        """Delete proccess."""
        LOGGER.info("QuimeraPS service stops.")


@dispatcher.add_method
def requestDispatcher(**kwargs):
    """Dispatch print requests."""
    return {"response": processPrintRequest(**kwargs)}


@dispatcher.add_method
def syncDispatcher(**kwargs):
    """Dispatch sync requests."""

    return {"response": processSyncRequest(**kwargs)}


def processSyncRequest(**kwargs) -> Dict[str, Any]:
    """Process sync request."""

    group_name = kwargs["group_name"]
    result = processSync(group_name, kwargs["arguments"])
    return {"result": 1 if result else 0, "data": result}


def processSync(group_name, arguments) -> bool:
    """ Process sync"""
    result = ""
    try:
        sync_folder = os.path.join(os.path.abspath(DATA_DIR), group_name)
        if not os.path.exists(sync_folder):
            LOGGER.warning("Making folder %s" % sync_folder)
            os.mkdir(sync_folder)

        file_type = "%ss" % arguments["file_type"]

        type_folder = os.path.join(sync_folder, file_type)
        if not os.path.exists(type_folder):
            LOGGER.warning("Making folder %s" % type_folder)
            os.mkdir(type_folder)
        file_path = os.path.join(type_folder, arguments["file_name"])
        file_path_compiled = file_path.replace(".jrxml", ".jasper")
        if arguments["file_delete"] == "1":
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(file_path):
                result = (
                    "No se ha podido eliminar el fichero %s" % arguments["file_name"]
                )
            else:
                if file_type == "subreports":
                    if os.path.exists(file_path_compiled):
                        os.remove(file_path_compiled)
                    if os.path.exists(file_path_compiled):
                        result = (
                            "No se ha podido eliminar el fichero %s"
                            % file_path_compiled
                        )
        else:
            file = open(file_path, "wb")
            file.write(base64.decodebytes(arguments["file_data"].encode()))
            file.close()

            if file_type == "subreports" and file_path.endswith(".jrxml"):
                # compilamos el subreport.
                config = jasper_config.Config()
                config.output = file_path_compiled
                config.writeJasper = True
                instance = report.Report(config, file_path)
                instance.compile()

    except Exception as error:
        result = str(error)

    LOGGER.warning("devolviendo %s" % result)
    return result


def processPrintRequest(**kwargs) -> Dict[str, Any]:
    """Process print request."""
    is_error: bool = False
    data_or_str: Union[str, List[Any]] = ""
    return_base64: bool = "return_base64" in kwargs.keys() and kwargs[
        "return_base64"
    ] == 1

    if "type" in kwargs.keys():
        type_ = kwargs["type"]
        # LOGGER.warning("NEW %s!" % (type_))
        if type_ == "new_job":
            data_or_str = printerRequest(**kwargs["arguments"])
            is_error = not os.path.exists(data_or_str)
        elif type_ == "alive":
            data_or_str = aliveRequest()
        elif type_ == "data":
            data_or_str = dataRequest(**kwargs["arguments"])
        else:
            LOGGER.warning("Unknown request %s!" % (type_))

    else:
        is_error = True
        data_or_str = "type field is not defined"

    LOGGER.warning(
        "Result: %s, data: %s, base_64: %s"
        % ("Failed" if is_error else "Ok", data_or_str, return_base64)
    )
    return {
        "result": 1 if is_error else 0,
        "data": fileToBase64(data_or_str)
        if return_base64 and not is_error
        else data_or_str,
    }


def fileToBase64(file_name) -> str:
    """Return base64 file content."""

    file = open(file_name, "rb")
    result = base64.b64encode(file.read())
    file.close()
    return result.decode()


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
        True
        if "with_response" in kwargs.keys() and kwargs["with_response"] == 1
        else False
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

    only_pdf = "only_pdf" in kwargs_names and kwargs["only_pdf"] == 1
    group_name = kwargs["group_name"] if "group_name" in kwargs_names else None
    pdf_name = kwargs["pdf_name"] if "pdf_name" in kwargs_names else None

    if not only_pdf:
        for name in ["printer"]:
            if name not in kwargs_names:
                result = "%s field not specified" % name

    if "model" not in kwargs_names:
        kwargs["model"] = ""

    if "data" not in kwargs_names:
        kwargs["data"] = []

    if "report_name" not in kwargs_names:
        kwargs["report_name"] = ""

    if not result:
        if "cut" not in kwargs_names:
            kwargs["cut"] = False
        if "open_cash_drawer" not in kwargs_names:
            kwargs["open_cash_drawer"] = False

        try:
            result = launchPrinter(
                kwargs["printer"] if not only_pdf else "",
                kwargs["model"],
                kwargs["cut"],
                kwargs["open_cash_drawer"],
                kwargs["data"],
                pdf_name,
                only_pdf,
                group_name,
                kwargs["report_name"],
                kwargs["params"] if "params" in kwargs_names else {},
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
    printer_alias: str,
    model_alias: str,
    cut: bool,
    open_cd: bool,
    data: List[Any],
    pdf_name=None,
    only_pdf=False,
    group_name=None,
    model_name="",
    params: Dict = {},
) -> str:
    """Print a request."""
    result = ""
    # resolver nombre impresora
    printer_data = resolvePrinter(printer_alias)
    model_data = None
    if not printer_data and not only_pdf:
        result = "Printer alias (%s) doesn't exists!" % printer_alias
        LOGGER.warning(result)

    # resolver nomber model
    if not result and not model_name:
        model_data = resolveModel(model_alias)
        if not model_data:
            result = "Model alias (%s) doesn't exists!" % model_alias
            LOGGER.warning(result)

    if not result and not data:
        result = "Data (%s) is empty" % data
        LOGGER.warning(result)

    if not result:  # Si no hay fallo previo
        # crear request
        printer_name = printer_data[0] if not only_pdf else None
        cut_command: Optional[str] = printer_data[1] if cut and printer_data[
            1
        ] else None
        open_command: Optional[str] = printer_data[2] if open_cd and printer_data[
            2
        ] else None
        model_name = model_data[0] if not model_name and model_data else model_name
        num_copies = int(model_data[1]) if model_data and model_data[1] else 1

        reports_dir = os.path.join(
            os.path.abspath(DATA_DIR), group_name if group_name else "", "reports"
        )
        if not os.path.exists(reports_dir):
            LOGGER.warning("Making reports folder (%s)" % reports_dir)
            os.mkdir(reports_dir)

        input_file = "%s" % os.path.join(reports_dir, "%s" % model_name)
        if not input_file.lower().endswith(".jrxml"):
            input_file += ".jrxml"

        if not os.path.exists(input_file):
            result = "Model (%s) doesn't exists!" % input_file
            LOGGER.warning(result)
        else:

            output_file = (
                os.path.join(tempfile.gettempdir(), pdf_name)
                if pdf_name
                else tempfile.mktemp()
            )
            output_file_pdf = output_file + "%s" % (
                ".pdf" if not output_file.lower().endswith(".pdf") else ""
            )

            data_dumps = json.dumps({"query": {"registers": data}})
            # generamos temporal con datos json
            temp_json_file = tempfile.mktemp(".json")
            file_ = open(temp_json_file, "w", encoding="UTF-8")
            file_.write(data_dumps)
            file_.close()

            if not os.path.exists(temp_json_file):
                result = "JSON file (%s) doesn't exists!" % temp_json_file
                LOGGER.warning(result)
            else:

                LOGGER.info(
                    "json :%s, jasper: %s, result: %s"
                    % (temp_json_file, input_file, output_file_pdf)
                )

                resources_folder = os.path.join(
                    os.path.dirname(input_file), "..", "resources"
                )
                resource_files = None
                if os.path.exists(resources_folder):
                    resource_files = resources_folder
                try:
                    config = jasper_config.Config()
                    config.input = input_file
                    config.output = output_file
                    config.dataFile = temp_json_file
                    config.locale = (
                        params["REPORT_LOCALE"]
                        if "REPORT_LOCALE" in params.keys()
                        else "es_ES"
                    )
                    config.jsonLocale = (
                        params["JSON_LOCALE"]
                        if "JSON_LOCALE" in params.keys()
                        else "en_US"
                    )
                    config.dbType = "json"
                    config.jsonQuery = "query.registers"
                    config.resource = resource_files
                    config.params = {
                        "SUBREPORT_DIR": "%s%s"
                        % (
                            os.path.join(
                                os.path.abspath(DATA_DIR),
                                group_name if group_name else "",
                                "subreports",
                            ),
                            "\\" if sys.platform.startswith("win") else "/",
                        )
                    }
                    if params:
                        for param_key, param_value in params.items():
                            LOGGER.info(
                                "Adding param %s = %s" % (param_key, param_value)
                            )
                            if param_key in ["REPORT_LOCALE"]:
                                continue
                            config.params[param_key] = param_value

                    LOGGER.info("Starting reports server %s" % config.input)
                    instance = report.Report(config, config.input)
                    LOGGER.info("Filling %s" % config.input)
                    LOGGER.warning("Default locale %s" % instance.defaultLocale)
                    LOGGER.warning("Current locale %s" % instance.config.locale)
                    instance.fill()
                    instance.export_pdf()

                    if not only_pdf:
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
                    result = output_file_pdf
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
        except Exception as error:
            result = str(error)

    else:
        try:
            os.system("lp -d %s %s" % (printer, file_name))
        except Exception as error:
            result = str(error)

    return result
