import sqlite3
import logging
import os
from typing import Any

LOGGER = logging.getLogger(__name__)

class SQLiteClass:

    _connection : "sqlite3.Connection"

    def __init__(self):
        super().__init__() 
        self._connection = None
        self.connectToDB()

    
    def __del__(self):

        if self._connection:
            self._connection.close()

    def connectToDB(self):
        build_tables = False
        file_path = os.path.join(__file__.replace("data.py", ""), "..", 'quimera_ps.bd') 

        if not os.path.exists(file_path):
            build_tables = True
        LOGGER.warning("DB File %s" % file_path)
        self._connection = sqlite3.connect(file_path)

        if build_tables:
            LOGGER.warning("Generating File %s" % file_path)
            self.generateTables()

    def generateTables(self):
        LOGGER.warning("Making tables.")
        cursor = self._connection.cursor()
        cursor.execute("CREATE TABLE printers (alias TEXT, name TEXT, cut TEXT, cash_drawer TEXT)")
        cursor.execute("CREATE TABLE models (alias TEXT, name TEXT, copies INTEGER)")
        cursor.execute("CREATE TABLE history (client_id TEXT, timestamp DATETIME, data_request JSON, data_response JSON)")
    
    def executeQuery(self, query: str):
        return self._connection.cursor().execute(query)



    #def read(self, table_name, pk):




