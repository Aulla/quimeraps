"""main package."""


from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple

from pyreportjasper.config import Config
from pyreportjasper.report import Report
import ghostscript
from quimeraps.json_srv import data as data_module
from quimeraps import __VERSION__, DATA_DIR

from jsonrpc import JSONRPCResponseManager, dispatcher
import os
import logging
import tempfile
import locale
import sys
        
from typing import Dict, List, Optional, Any

CONN = None

LOGGER = logging.getLogger(__name__)


class JsonClass:
    """JsonClass class"""

    def run(self):
        global CONN
        CONN = data_module.SQLiteClass()
        LOGGER.warning("Quimera-ps service v.%s" % (__VERSION__))
        run_simple('0.0.0.0', 4000, self.service)
    

    @Request.application
    def service(self, request) -> None:
        """Json service."""

        response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
        # data_request = request.data
        try:
            data_response = Response(response.json, mimetype='application/json')
        except Exception as error:
            data_response = Response({'error': error}, mimetype='application/json')
        # TODO: meterlo en historial data_request y data response.
        return data_response
    
    def __del__(self):
        LOGGER.warning('Bye!')


@dispatcher.add_method
def requestDispatcher( **kwargs):
    """Dispatch print requests."""

    return {'response' : processRequest(**kwargs)}


def  processRequest(**kwargs) -> Dict[str, Any]:
    """Process print request"""

    error = ''
    data = ''

    if "type" in kwargs.keys():
        type_ = kwargs['type']
        #LOGGER.warning("NEW %s!" % (type_))
        if type_ == 'new_job':
            error = printerRequest(**kwargs['arguments'])
        elif type_ == 'alive':
            data = aliveRequest()
        elif type_ == 'data':
            data = dataRequest(**kwargs['arguments'])
        else:
            LOGGER.warning("UNKNOWN %s!" % (type_))

    else:
        error = 'type field is not defined'

    
    return {'result' : 1 if error else 0, 'data' : error if error else data}

def aliveRequest() -> str:
    """Return a alive string."""

    return __VERSION__


def dataRequest(**kwargs) -> List[Any]:

    """Return data from SQLLITE."""
    result = ''

    # table_name = kwargs['table'] if 'table' in kwargs.keys() else ""
    mode = kwargs['mode']
    
    
    # fields = kwargs['fields'] if 'fields' in kwargs.keys() else ['*']
    # pk = kwargs['pk'] if 'pk' in kwargs.keys() else '1 = 1'
    # values = kwargs['values'] if 'values' in kwargs.keys() else []
    raw_text = kwargs['raw'] if 'raw' in kwargs.keys() else ''
    with_response = True if 'with_response' in kwargs.keys() and kwargs['with_response'] == 1 else False
    result = 'ok'
    try:
        if mode == 'raw':
            try:
                query_cursor = CONN.executeQuery(raw_text)
                # print("CALLING!", raw_text)
                if with_response:
                    result = query_cursor.fetchall()
                query_cursor.close()
            except Exception as error:
                result = {"error_sql" : error}
        else:
            result = 'unknown mode (%s)' % mode
    except Exception as error:
        result = error
    
    return result

def printerRequest(**kwargs) -> int:
    """Print requests."""
    error = ''

    kwargs_names = kwargs.keys()
    for name in ['printer']:
        if name not in kwargs_names:
            error = "%s field not specified" % name
    
    if 'model' not in kwargs_names:
        kwargs['model'] = ''
    
    if 'data' not in kwargs_names:
        kwargs['data'] = []
    
            
    if not error:
        if 'cut' not in kwargs_names:
            kwargs['cut'] = False
        if 'open_cash_drawer' not in kwargs_names:
            kwargs['open_cash_drawer'] = False

        error = launchPrinter(kwargs['printer'], kwargs['model'], kwargs['cut'],kwargs['open_cash_drawer'],  kwargs['data'])
    
    return error

def resolvePrinter(printer_alias: str):
    printer_cursor = CONN.executeQuery("SELECT name,cut,cash_drawer FROM printers WHERE alias='%s'" % printer_alias)
    if printer_cursor.rowcount:
        result = printer_cursor.fetchone()
        printer_cursor.close()
        return result
    return None

def resolveModel(model_alias: str):
    model_cursor = CONN.executeQuery("SELECT name,copies FROM models WHERE alias='%s'" % model_alias)
    if model_cursor.rowcount:
        result = model_cursor.fetchone()
        model_cursor.close()

        return result

    return None
    

def launchPrinter(printer_alias: str, model_alias: str, cut: bool, open_cd: bool, data:List[Any], copies: int = 0) -> str:
    """Print a request."""

    # LOGGER.warning("Impresora: %s, modelo: %s, cut: %s, drawer: %s, data: %s, copies: %s" % (printer_alias, model_alias, cut, open, data, copies))
    result = ''
    # resolver nombre impresora
    printer_data = resolvePrinter(printer_alias) 
    if not printer_data:
        return "Printer alias (%s) doesn't exists!" % printer_alias

    # resolver nomber model
    model_data = resolveModel(model_alias)
    if not model_data:
        return "Model alias (%s) doesn't exists!" % model_alias

    if not data:
        return 'Data (%s) is empty' % data
    # crear request
    printer_name = printer_data[0]
    cut_command : Optional[str] = printer_data[1] if cut and printer_data[1] else None
    open_command : Optional[str] = printer_data[2] if open_cd and printer_data[2] else None
    model_name = model_data[0]
    num_copies = copies if copies else int(model_data[1]) if model_data[1] else 1

    reports_dir = os.path.join(os.path.abspath(DATA_DIR), 'reports')
    if not os.path.exists(reports_dir):
        LOGGER.warning("Making reports folder (%s)" %reports_dir)
        os.mkdir(reports_dir)


    input_file = "%s.jrxml" % os.path.join(reports_dir, '%s' % model_name)

    if not os.path.exists(input_file):
        return "Model (%s) doesn't exists!" % input_file
    
    output_file = tempfile.mktemp()
    output_file_pdf = output_file +  '.pdf'

    # generamos temporal con datos json
    temp_json_file = tempfile.mktemp(".json")
    file_= open(temp_json_file, 'w', encoding="UTF-8")
    file_.write(str({"query": {"registers": data }}))
    file_.close()

    if not os.path.exists(temp_json_file):
        return "JSON file (%s) doesn't exists!" % temp_json_file

    LOGGER.warning("Fichero JSON = %s" % temp_json_file)
    LOGGER.warning("Fichero JASPER = %s" % input_file)
    LOGGER.warning("Fichero resultado = %s " % output_file_pdf )

    config = Config()
    config.input =  input_file
    config.output = output_file
    config.dataFile = temp_json_file 

    config.dbType = 'json'
    config.jsonQuery = 'query.registers'
    instance = Report(config, config.input)
    instance.fill()
    instance.export_pdf()



    try:
        for num in range(num_copies):
            LOGGER.warning("Sendign Nº %s, printer: %s, model: %s" % (num + 1, printer_name, model_name))
            result = sendToPrinter(printer_name, output_file_pdf)

            # lanza corte
            if not result and cut_command:
                temp_cut_file: str = tempfile.mktemp('.esc_command')
                file_cut = open(temp_cut_file, 'b')
                file_cut.write(cut_command.encode())
                file_cut.close()
                result = sendToPrinter(printer_name, temp_cut_file)

            if result:
                break
        # lanza cajon
        if not result and open_command:
            temp_open_file: str = tempfile.mktemp('.esc_command')
            file_cut = open(temp_open_file, 'b')
            file_cut.write(open_command.encode())
            file_cut.close()
            result = sendToPrinter(printer_name, temp_open_file)
    except Exception as error:
        LOGGER.warning("Error: %s" % error)
        result = str(error)


    return result

def sendToPrinter(printer: str , file_name):
    result = ''
    LOGGER.warning("SENDING TO PRINTER %s -> %s" % (printer, file_name))
    if sys.platform.startswith('win'):
        args = [
            "-dPrinted", "-dBATCH", "-dNOSAFER", "-dNOPAUSE", "-dNOPROMPT"
            "-q",
            "-dNumCopies#1",
            "-sDEVICE#mswinpr2",
            f'-sOutputFile#"%printer%{printer}"',
            f'"{file_name}"'
        ]

        try:
            encoding = locale.getpreferredencoding()
            args = [a.encode(encoding) for a in args]
            ghostscript.Ghostscript(*args)
        except Exception as error:
            result = error

    else:
        try:
            os.system('lp -d %s -n 2 %s' % (printer , file_name))        
        except Exception as error:
            result = error

    return result




    

    






