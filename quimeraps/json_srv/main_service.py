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
from quimeraps.json_srv import logging, process_functions
from quimeraps import __VERSION__, DATA_DIR


CONN: "data_module.SQLiteClass"

LOGGER = logging.getLogger(__name__)


class JsonClass:
    """JsonClass class."""

    def run(self):
        """Start JSON service."""
        global CONN
        LOGGER.info("QuimeraPS service v.%s starts." % (__VERSION__))
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

        CONN = data_module.SQLiteClass()

        serving.run_simple(
            "0.0.0.0",
            4000,
            self.service,
            ssl_context=ssl_context_,
            processes=4,
        )

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
def helloQuimera(**kwargs):
    """Say hello."""
    return {"response": "Hello ! %s" % kwargs}


@dispatcher.add_method
def getQuimeraLog(**kwargs):
    """Get quimera log."""
    return {"response": process_functions.quimera_log()}


@dispatcher.add_method
def requestDispatcher(**kwargs):
    """Dispatch print requests."""
    return {"response": process_functions.print_proceso(kwargs)}


@dispatcher.add_method
def syncDispatcher(**kwargs):
    """Dispatch sync requests."""

    return {"response": process_functions.sync_proceso(kwargs)}
