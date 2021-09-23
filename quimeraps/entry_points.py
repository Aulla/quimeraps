from PyQt6 import QtWidgets

import logging
import sys
from typing import List

LOGGER = logging.getLogger(__name__)


def call_app(args : List[str] = []) -> "QtWidgets.QApplication":

    

    return QtWidgets.QApplication(args)


def startup_client():

    from quimeraps.client_gui import main_window

    args = sys.argv + []

    app_ = call_app(args)
    LOGGER.info("Inicializando.")

    window = main_window.MainWindow()
    sys.exit(app_.exec())


def startup_service():

    from quimeraps.json_srv import main_service

    main_service.JsonClass() 
    LOGGER.warning("\nBye!")



