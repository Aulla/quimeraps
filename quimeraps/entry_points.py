import logging
from quimeraps.json_srv import daemon_functions
import sys
import os

LOGGER = logging.getLogger(__name__)

def startup_client():

    from PyQt6 import QtWidgets

    from quimeraps.client_gui import main_window
    app_ = QtWidgets.QApplication(sys.argv + [])
    window = main_window.MainWindow()
    sys.exit(app_.exec())


def startup_server():

    if not sys.platform.startswith('win'): 
        if os.geteuid() != 0:
            LOGGER.warning("This user is not super!.")
            return
        
    daemon_functions.start()

            

def install_daemon():
    """Install daemon."""

    if os.geteuid() != 0:
        LOGGER.warning("This user is not super!.")
        return

    mode = sys.argv[1] if len(sys.argv) > 1 else None

    if not mode:
        raise Exception("Mode ['install','remove'] is not specified.")



    if sys.platform.startswith('win'): # Windowzz
        if mode == 'install':
            daemon_functions.install_windows_service()
        elif mode == 'delete':
            daemon_functions.remove_windows_service()
        else:
            raise Exception("Unknown mode %s" % mode)
    else:
        
        
        if mode == 'install':
            daemon_functions.install_linux_daemon()
        elif mode == 'remove':
            daemon_functions.remove_linux_daemon()
        else:
            raise Exception("Unknown mode %s" % mode)







