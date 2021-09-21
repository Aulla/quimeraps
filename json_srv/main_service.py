"""main package."""

from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple


from . import data as data_module

from jsonrpc import JSONRPCResponseManager, dispatcher

import logging
from typing import Dict, List, Any

CONN = data_module.SQLiteClass()

LOGGER = logging.getLogger(__name__)
VERSION = "0.0.4"


class JsonClass:
    """JsonClass class"""

    _enabled : bool = False

    def __init__(self):
        """Initialize."""

        self._enabled = False
        LOGGER.warning("Quimera-ps service v.%s" % (VERSION))
        run_simple('0.0.0.0', 4000, self.service)
    

    @Request.application
    def service(self, request) -> None:
        """Json service."""

        response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
        data_request = request.data
        try:
            data_response = Response(response.json, mimetype='application/json')
        except Exception as error:
            data_response = Response({'error': error}, mimetype='application/json')
        # TODO: meterlo en historial data_request y data response.
        return data_response


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

    return VERSION


def dataRequest(**kwargs) -> List[Any]:

    """Return data from SQLLITE."""
    result = ''

    table_name = kwargs['table'] if 'table' in kwargs.keys() else ""
    mode = kwargs['mode']
    
    
    fields = kwargs['fields'] if 'fields' in kwargs.keys() else ['*']
    pk = kwargs['pk'] if 'pk' in kwargs.keys() else '1 = 1'
    values = kwargs['values'] if 'values' in kwargs.keys() else []
    raw_text = kwargs['raw'] if 'raw' in kwargs.keys() else ''
    with_response = True if 'with_response' in kwargs.keys() and kwargs['with_response'] == 1 else False
    result = 'ok'
    try:
        if mode == 'raw':
            try:
                query_cursor = CONN.executeQuery(raw_text)
                if with_response:
                    result = query_cursor.fetchall()
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


    LOGGER.warning("Impresora: %s, modelo: %s, cut: %s, drawer: %s, data: %s" % (kwargs['printer'], kwargs['model'], kwargs['cut'], kwargs['open_cash_drawer'], kwargs['data']))
    # TODO: Recoger nombres mapeados y lanzar solicitud de impresión
    return error

    



    

    






