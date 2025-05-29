"""main_service module."""

import os
import sys
from typing import Dict, List, Optional, Union, Any

import multiprocessing

from quimeraps.json_srv.utils import format_response, load_data

from quimeraps.json_srv import logging, process_functions
from quimeraps import __VERSION__, DATA_DIR
from fastapi import FastAPI
import gunicorn.app.base
import json

POOL = None

app = FastAPI()
LOGGER = logging.getLogger(__name__)


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


def pre_fork(server, worker):
    print(f"pre-fork server {server} worker {worker}", file=sys.stderr)


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return service


class JsonClass:
    """JsonClass class."""

    def run(self):
        """Start JSON service."""
        global POOL

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

        options = {
            "bind": "0.0.0.0:4000",
            "workers": number_of_workers(),
            "pre_fork": pre_fork,
            "timeout": process_functions.TIMEOUT,
        }

        try:

            StandaloneApplication(app, options).run()
        except KeyboardInterrupt:
            POOL.close()
            POOL.join()

    def __del__(self):
        """Delete proccess."""
        LOGGER.info("QuimeraPS service stops.")


def service(environ, start_response):
    """Simplest possible application object"""
    input: "gunicorn.http.body.Body" = environ["wsgi.input"]
    data_bytes = input.read()
    result = entry_points(json.loads(data_bytes))
    status = "200 OK" if "result" in result else "400 Bad Request"
    response_bytes = json.dumps(result).encode()

    response_headers = [
        ("Content-type", "text/plain"),
        ("Content-Length", str(len(response_bytes))),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Headers", "*"),
        ("Access-Control-Allow-Methods", "*"),
    ]

    start_response(status, response_headers)

    return iter([response_bytes])


def entry_points(data):

    meth = data["method"]
    params = data["params"]
    json_response = None
    try:
        if meth == "helloQuimera":
            json_response = helloQuimera(**params)
        elif meth == "getQuimeraLog":
            json_response = getQuimeraLog(**params)
        elif meth == "requestDispatcher":
            json_response = requestDispatcher(**params)
        elif meth == "syncDispatcher":
            json_response = syncDispatcher(**params)
        else:
            json_response = {"result": "Method not found"}
    except Exception as error:
        json_response = {"result": str(error)}

    if "response" not in json_response:
        LOGGER.warning("Error resolving request when %s : %s" % (meth, data))
        json_response = {"error": json_response}

    return {"result": json_response}


def helloQuimera(**kwargs):
    """Say hello."""
    return {"response": "Hello ! %s" % kwargs}


def getQuimeraLog(**kwargs):
    """Get quimera log."""
    return {"response": process_functions.quimera_log()}


def requestDispatcher(**kwargs):
    """Dispatch print requests."""
    return {"response": process_functions.print_proceso(kwargs)}


def syncDispatcher(**kwargs):
    """Dispatch sync requests."""

    return {"response": process_functions.sync_proceso(kwargs)}
