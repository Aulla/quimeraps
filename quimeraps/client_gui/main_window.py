"""Main_window module."""
from PyQt5 import QtWidgets, QtCore, uic
import logging
import requests
import os
import sys

from typing import Any, List


LOGGER = logging.getLogger(__name__)
REFRESH_TIME = 1000
if sys.platform.startswith("win"):
    REFRESH_TIME = 5000


class MainWindow(QtWidgets.QMainWindow):
    """MainWindow class."""

    _status_label: "QtWidgets.QLabel"
    _version_label: "QtWidgets.QLabel"
    _status_server_ok: str  # indica si el servidor está activo
    _timer: "QtCore.QTimer"
    _main_widget: "QtWidgets.QMainWindow"
    _tab: "QtWidgets.QTabWidget"
    _view_impresoras: "QtWidgets.QTableWidget"
    _view_modelos: "QtWidgets.QTableWidget"
    _fields_printers: List[str] = ["Alias", "impresora", "Comando corte", "Comando apertura"]
    _fields_alias: List[str] = ["Alias", "modelo", "copias"]

    def __init__(self):
        """Initialize."""
        super().__init__()
        self._status_server_ok = False
        self._timer = QtCore.QTimer()
        LOGGER.warning("Init main_window")
        uic.loadUi(os.path.join(os.path.dirname(__file__), "main_window.ui"), self)
        self.setWindowTitle("QuimeraPS Control Panel")
        self._status_label = self.findChild(QtWidgets.QLabel, "status_label")
        self._version_label = self.findChild(QtWidgets.QLabel, "version_label")
        self._view_modelos = self.findChild(QtWidgets.QTableWidget, "view_modelos")
        self._view_impresoras = self.findChild(QtWidgets.QTableWidget, "view_impresoras")
        self._tab = self.findChild(QtWidgets.QTabWidget, "tab_widget")
        self._tab.currentChanged.connect(self.populateData)
        self.initStatusChecker()
        self.populateData(0)
        self.show()

    def populateData(self, idx: int) -> None:
        """Populate tables."""
        if idx == 0:
            self.populatePrintersTable()
        elif idx == 1:
            self.populateModelsTable()

    def populatePrintersTable(self) -> None:
        """Populate printers table."""
        if self._status_server_ok:
            LOGGER.debug("Populating printers")
            response = self.askToServer(
                "data",
                {
                    "type": "data",
                    "arguments": {
                        "mode": "raw",
                        "raw": "SELECT * FROM printers WHERE 1 = 1",
                        "with_response": 1,
                    },
                },
            )
            data = (
                response["response"]["data"]
                if "result" in response["response"].keys() and response["response"]["result"] == 0
                else []
            )
            self.populateTable("printers", data)

    def populateModelsTable(self) -> None:
        """Request table data to json server."""
        if self._status_server_ok:
            LOGGER.debug("Populating models")
            response = self.askToServer(
                "data",
                {
                    "type": "data",
                    "arguments": {
                        "mode": "raw",
                        "raw": "SELECT * FROM models WHERE 1 = 1",
                        "with_response": 1,
                    },
                },
            )
            data = (
                response["response"]["data"]
                if "result" in response["response"].keys() and response["response"]["result"] == 0
                else []
            )
            self.populateTable("models", data)

    def clearTable(self, table: "QtWidgets.QTableWidget") -> None:
        """Clear table rows."""
        while table.rowCount():
            table.removeRow(0)

        table.clear()
        table.setColumnCount(0)

    def populateTable(self, name: str, data=None) -> None:
        """Load table contents."""
        fields = []
        fields += self._fields_printers if name == "printers" else self._fields_alias
        table = self._view_impresoras if name == "printers" else self._view_modelos

        fields += ["Opciones"]
        # cabecera

        self.clearTable(table)

        table.setColumnCount(len(fields))
        table.setHorizontalHeaderLabels(fields)
        for col in range(len(fields)):
            table.horizontalHeader().setSectionResizeMode(
                col, QtWidgets.QHeaderView.ResizeToContents
            )

        idx_pk = 0

        row_num = -1
        for dato in data:
            row_num = table.rowCount()
            # print("insertando linea", row_num , "-->", dato)
            table.insertRow(row_num)
            for col_num, field_name in enumerate(fields):
                # print("* col_num", col_num)
                if col_num < len(fields) - 1:
                    value = str(dato[col_num])
                    # print("Campo", field_name, "->", value)
                    text_item = QtWidgets.QTableWidgetItem(value)
                    text_item.setTextAlignment(QtCore.Qt.AlignVCenter + QtCore.Qt.AlignRight)
                    text_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    table.setItem(row_num, col_num, text_item)
                else:
                    # print("Boton borrar", row_num)
                    lay = QtWidgets.QHBoxLayout()
                    button_delete = QtWidgets.QPushButton()
                    button_delete.setObjectName("delete_%s_%s" % (name, dato[idx_pk]))
                    button_delete.setText("Borrar")
                    button_delete.clicked.connect(self.proccessData)  # type: ignore [attr-defined]
                    lay.addWidget(button_delete)
                    if name == "printers":
                        button_test = QtWidgets.QPushButton()
                        button_test.setObjectName("test_%s" % (dato[idx_pk]))
                        button_test.setText("Test")
                        button_test.clicked.connect(  # type: ignore [attr-defined]
                            self.proccessTest
                        )
                        lay.addWidget(button_test)

                    options_widget = QtWidgets.QWidget()
                    lay.setContentsMargins(0, 0, 0, 0)
                    options_widget.setLayout(lay)
                    table.setCellWidget(row_num, col_num, options_widget)

        # registro limpio
        # print("Última", row_num)
        row_num += 1
        table.insertRow(row_num)
        for col_num, field_name in enumerate(fields):
            if col_num < len(fields) - 1:
                value = ""
                text_item = QtWidgets.QTableWidgetItem(value)
                text_item.setTextAlignment(QtCore.Qt.AlignVCenter + QtCore.Qt.AlignRight)
                table.setItem(row_num, col_num, text_item)
            else:
                # print("Botón crear!", row_num)
                button = QtWidgets.QPushButton()
                button.setObjectName("insert_%s_%s" % (name, ""))
                button.setText("Crear")
                button.clicked.connect(self.proccessData)  # type: ignore [attr-defined]
                table.setCellWidget(row_num, col_num, button)

    def proccessTest(self) -> None:
        """Proccess test button triggered."""
        sender = self.sender()
        mode, pk = sender.objectName().split("_")
        self.sendTest(pk)

    def sendTest(self, pk) -> None:
        """Send test query to json server."""
        table = self._view_impresoras
        printer_name = ""
        for row_num in range(table.rowCount()):
            if pk == table.item(row_num, 0).text():
                printer_name = table.item(row_num, 0).text()
                break

        json_data = [
            {
                "name": "ETHAN",
                "street": "Street 1",
                "city": "Fairfax",
                "phone": "+1 (415) 111-1111",
            },
            {
                "name": "CALEB",
                "street": "Street 2",
                "city": "San Francisco",
                "phone": "+1 (415) 222-2222",
            },
            {
                "name": "WILLIAM",
                "street": "Street 2",
                "city": "Paradise City",
                "phone": "+1 (415) 333-3333",
            },
        ]

        trama = {
            "type": "new_job",
            "arguments": {"printer": printer_name, "model": "test", "data": json_data},
        }
        LOGGER.warning("Sending %s" % (trama))
        try:
            response = self.askToServer("new_job", trama)
        except Exception as error:
            LOGGER.warning("Error: %s, consulta : %s" % (error, trama))
            response = error

        if isinstance(response, dict):
            if "response" in response.keys():
                response_text = response["response"]["data"]
        else:
            response_text = str(response)

        QtWidgets.QMessageBox.information(
            self, "QuimeraPS", response_text if response_text else "Test ok!"
        )

    def proccessData(self) -> None:
        """Resolve data, send a query and reload table."""
        sender = self.sender()
        mode, table, pk = sender.objectName().split("_")

        # print("EOOO", mode, table, pk)
        self.sendQuery(mode, table, pk)
        self.populateData(0 if table == "printers" else 1)

    def sendQuery(self, mode, table_name, pk="") -> None:
        """Send a query to json server."""
        # Buscamos la linea y cogemos valores

        table = self._view_impresoras if table_name == "printers" else self._view_modelos
        data = []
        # print("Recopilando datos view (%s)" %  pk)
        if mode == "delete":
            for row_num in range(table.rowCount()):

                if pk == table.item(row_num, 0).text():
                    # print("PK encontrada", pk)
                    for col_num in range(table.columnCount() - 1):
                        # print("Recolectando " , col_num)
                        data.append(table.item(row_num, col_num).text())
        else:
            row_num = table.rowCount() - 1
            for col_num in range(table.columnCount() - 1):
                # print("Recolectando " , col_num)
                data.append(table.item(row_num, col_num).text())

        if not data[0] and mode == "insert":
            LOGGER.warning("Alias vacio")
            return

        qry = ""

        if mode == "delete":
            qry = "DELETE FROM %s WHERE alias ='%s'" % (table_name, pk)
        elif mode == "insert":
            qry = "INSERT INTO %s VALUES (%s)" % (
                table_name,
                ", ".join(["'%s'" % dat for dat in data]),
            )

        if qry:
            trama = {"type": "data", "arguments": {"mode": "raw", "raw": qry, "with_response": 1}}
            # print("TRAMA!!", trama, qry)
            try:
                self.askToServer("data", trama)
            except Exception as error:
                LOGGER.warning("Error: %s, consulta : %s" % (error, trama))

            # print("RESPONSE", response)

    def initStatusChecker(self) -> None:
        """Initialize status_checker."""
        self._timer.timeout.connect(self.askToServerAlive)  # type: ignore [attr-defined]
        self._timer.start(REFRESH_TIME)
        LOGGER.warning("Status checker activated!")

    def askToServerAlive(self) -> None:
        """Ask to server if exists."""
        try:

            result = self.askToServer("alive")["response"]
            self._status_server_ok = result["data"] if result["result"] == 0 else ""
        except Exception:
            self._status_server_ok = ""
        self.updateStatusLabel()

    def updateStatusLabel(self) -> None:
        """Update status label."""
        new_value = "Apagado"
        version = ""

        if self._status_server_ok:
            new_value = "Encendido"
            version = "V %s " % self._status_server_ok

        else:
            self.clearTable(self._view_impresoras)
            self.clearTable(self._view_modelos)

        if new_value != self._status_label.text():  # Si cambia el texto refresco
            self.populateData(self._tab.currentIndex())

        self._status_label.setText(new_value)
        self._version_label.setText(version)

    def askToServer(self, name: str, params={}) -> Any:
        """Ask to server something."""
        url = "http://localhost:4000"

        params["type"] = name

        payload = {
            "method": "requestDispatcher",
            "params": params,
            "jsonrpc": "2.0",
            "id": "manager_%s" % name,
        }

        return requests.post(url, json=payload).json()["result"]
