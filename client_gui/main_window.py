from PyQt6 import QtWidgets, QtCore
import logging, requests, json
from typing import Any

LOGGER = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow):

    _status_label : "QtWidgets.QLabel"
    _status_server_ok : bool # indica si el servidor está activo
    _timer : "QtCore.QTimer"

    def __init__(self):
        super().__init__()
        self._status_server_ok = False
        self._timer = QtCore.QTimer()
        LOGGER.warning("Init main_window")
        self.setWindowTitle('QuimeraPS Control Panel')
        self._status_label = QtWidgets.QLabel("STATUS", self)
        self.show()
        # TODO: Lanza actualizador de estado.
        self.initStatusChecker()

        # TODO: Inicializa pestaña printer_alias
        # TODO: inicializa pestaña model_alias
        # TODO: inicializa conexión a BD.
        # TODO: Datos conexión jasper_server.
        # TODO: Historial.
    
    def __del__(self):
        """Destroy process."""

        self._timer.stop()


    def initStatusChecker(self):
        """Initialize status_checker"""
        self._timer.timeout.connect(self.askToServerAlive)
        self._timer.start(1000)
        LOGGER.warning("Status checker activated!")


    

    def askToServerAlive(self) -> None:
        """Ask to server if exists."""

        try:
            result = self.askToServer("alive")['response']
            print("***", result)
            self._status_server_ok = True if result['result'] == 0 and result['data'] == 'hello' else False
        except Exception:
            self._status_server_ok = False

        self.updateStatusLabel()

    def updateStatusLabel(self) -> None:
        """Update status label."""
        
        new_value = "Encendido" if self._status_server_ok else "Apagado"
        print("**", new_value)
        self._status_label.setText(new_value)



    def askToServer(self, name:str, params = {}) -> Any:
        """Ask to server something."""

        url = "http://localhost:4000"

        params['type'] = name

        payload = {
            "method" : "requestDispatcher",
            "params" : params,
            "jsonrpc" : "2.0",
            "id" : "manager_%s" % name 
        }

        return requests.post(url, json=payload).json()['result']
