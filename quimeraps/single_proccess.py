import os
import sys
import json
from quimeraps.json_srv import process_functions


def ejecutar_tarea():
    # Obtener la ruta del archivo JSON
    mode = sys.argv[2]
    data_file = sys.argv[1]
    data_target = sys.argv[3]
    # carga json desde data_file
    json_file = open(
        data_file,
    )
    data = json.load(json_file)
    json_file.close()

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
        file_ = open(data_target, "w")
        json.dump(result, file_)
        file_.close()

    sys.exit(0)


if __name__ == "__main__":
    ejecutar_tarea()
