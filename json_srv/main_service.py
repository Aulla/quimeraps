"""main package."""

from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple


from . import data as data_module

from jsonrpc import JSONRPCResponseManager, dispatcher

import logging
from typing import Dict, List, Any

CONN = data_module.SQLiteClass()

LOGGER = logging.getLogger(__name__)

class JsonClass:
    """JsonClass class"""

    _enabled : bool = False

    def __init__(self):
        """Initialize."""

        self._enabled = False
        run_simple('0.0.0.0', 4000, self.service)
    

    @Request.application
    def service(self, request) -> None:
        """Json service."""

        response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
        data_request = request.data
        data_response = Response(response.json, mimetype='application/json')
        # TODO: meterlo en historial
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

    return 'hello'


def dataRequest(**kwargs) -> List[Any]:

    """Return data from SQLLITE."""
    result = ''

    table_name = kwargs['table']
    mode = kwargs['mode']
    
    
    fields = kwargs['fields'] if 'fields' in kwargs.keys() else ['*']
    pk = kwargs['pk'] if 'pk' in kwargs.keys() else '1 = 1'
    values = kwargs['values'] if 'values' in kwargs.keys() else []

 
    if mode == 'select':
        query_cursor = CONN.executeQuery("SELECT %s FROM %s WHERE %s" % (",".join(fields), table_name, pk))
        result = query_cursor.fetchall()
    elif mode == 'insert':
        # insert data into BD
        
        pass
    elif mode == 'delete':
        pass
        # delete field from BD
    else:
        result = 'unknown mode (%s)' % mode
    
    return result

def printerRequest(**kwargs) -> int:
    """Print requests."""
    error = ''

    kwargs_names = kwargs.keys()
    for name in ['printer', 'model', 'data']:
        if name not in kwargs_names:
            error = "%s field not specified" % name
            
    if not error:
        if 'cut' not in kwargs_names:
            kwargs['cut'] = False
        if 'open_cash_drawer' not in kwargs_names:
            kwargs['open_cash_drawer'] = False


    LOGGER.warning("Impresora: %s, modelo: %s, cut: %s, drawer: %s, data: %s" % (kwargs['printer'], kwargs['model'], kwargs['cut'], kwargs['open_cash_drawer'], kwargs['data']))
    # TODO: Recoger nombres mapeados y lanzar solicitud de impresión
    return error

    



    

    






