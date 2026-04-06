import sys
import json
import signal
from json_srv import process_functions
from json_srv import data as data_module
from quimeraps.json_srv import logging

LOGGER = logging.getLogger(__name__)


class PrintTimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise PrintTimeoutError()


def _write_response(response_file, result):
    file_ = open(response_file, "w")
    json.dump(result, file_)
    file_.close()


def ejecutar_tarea():
    response_file = None
    timeout = process_functions.TIMEOUT
    try:
        mode = sys.argv[1]
        json_file = sys.argv[2]
        response_file = sys.argv[3]
        timeout = int(sys.argv[4]) if len(sys.argv) > 4 else process_functions.TIMEOUT
        # carga json desde data_file
        LOGGER.warning(
            "mode: %s, data_file: %s, data_target: %s"
            % (mode, json_file, response_file)
        )
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(timeout)
        json_file = open(
            json_file,
        )
        data = json.load(json_file)
        json_file.close()
        # LOGGER.warning("data: %s" % type(data))
        # process_functions.CONN = data_module.SQLiteClass()
        # Llamar a la función process_data del módulo json_srv
        result = None
        if mode == "print":
            result = process_functions.processPrintRequest(data)
        elif mode == "sync":
            result = process_functions.processSyncRequest(data)
        elif mode == "check_tmp":
            result = process_functions.processTmpCheckRequest(data)
        else:
            print("Modo no válido")
            sys.exit(1)

        if result is not None:
            _write_response(response_file, result)

        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)

        sys.exit(0)
    except PrintTimeoutError:
        LOGGER.error("Timeout reached")
        if response_file is not None:
            _write_response(
                response_file, process_functions.build_timeout_error(timeout)
            )
            sys.exit(0)
        sys.exit(1)
    except Exception as e:
        LOGGER.error(e)
        sys.exit(1)


if __name__ == "__main__":
    ejecutar_tarea()
