"""main package."""

from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

import logging
from typing import Dict, Any

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
        
        return Response(response.json, mimetype='application/json')



@dispatcher.add_method
def echo(echo = '') -> str:
    """Echo function."""
    
    return echo

@dispatcher.add_method
def requestDispatcher( **kwargs):
    """Dispatch print requests."""

    return {'response' : processRequest(**kwargs)}


def  processRequest(**kwargs) -> bool:
    """Process print request"""

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

        error = printerRequest(kwargs['printer'], kwargs['model'], kwargs['cut'], kwargs['open_cash_drawer'], kwargs['data'])
    
    return {'result' : 1 if error else 0, 'error' : error}

def printerRequest( printer : str, model : str , cut : bool, open_cash_drawer : bool, data: Dict[str , Any]) -> int:
    """Print requests."""
    error = ''
    LOGGER.warning("Impresora: %s, modelo: %s, cut: %s, drawer: %s, data: %s" % (printer, model, cut, open_cash_drawer, data))
    # TODO: Recoger nombres mapeados y lanzar solicitud de impresión
    return error

    



    

    






