from PyQt6 import QtWidgets
from quimeraps.client_gui import main_window
import sys, logging

from typing import List

LOGGER = logging.getLogger(__name__)

def call_app(args : List[str] = []) -> "QtWidgets.QApplication":

    return QtWidgets.QApplication(args)

def startup() -> int:

    args = sys.argv + []

    app_ = call_app(args)
    LOGGER.info("Inicializando.")

    window = main_window.MainWindow()
    sys.exit(app_.exec())



if __name__ == "__main__":

    startup()