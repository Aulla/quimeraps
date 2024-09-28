import sys
import json
from json_srv import process_functions
from json_srv import data as data_module
from quimeraps.json_srv import logging

LOGGER = logging.getLogger(__name__)


def ejecutar_tarea():
    try:
        mode = sys.argv[1]
        json_file = sys.argv[2]
        response_file = sys.argv[3]
        # carga json desde data_file
        LOGGER.warning(
            "mode: %s, data_file: %s, data_target: %s"
            % (mode, json_file, response_file)
        )
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
        else:
            print("Modo no válido")
            sys.exit(1)

        if result is not None:
            file_ = open(response_file, "w")
            json.dump(result, file_)
            file_.close()

        sys.exit(0)
    except Exception as e:
        LOGGER.error(e)
        sys.exit(1)


if __name__ == "__main__":
    ejecutar_tarea()
