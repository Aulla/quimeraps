from PyQt6 import QtWidgets
import logging

LOGGER = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):

    _status_label : "QtWidgets.QLabel"

    def __init__(self):
        super().__init__()

        LOGGER.warning("Init main_window")
        self.setWindowTitle('QuimeraPS Control Panel')
        self._status_label = QtWidgets.QLabel("STAUS", self)
        self.show()
        # TODO: Lanza actualizador de estado.

        # TODO: Inicializa pestaña printer_alias
        # TODO: inicializa pestaña model_alias
        # TODO: inicializa conexión a BD.
        # TODO: Datos conexión jasper_server.
        # TODO: Historial.