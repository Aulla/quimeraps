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

    if sys.platform.startswith('win'): 
        daemon_functions.start_windows_service()
    else:
        mode = sys.argv[1] if len(sys.argv) > 1 else None
        if not mode:
            LOGGER.warning("Mode is not specified.")
        
        if os.geteuid() != 0:
            LOGGER.warning("This user is not super!.")
            return
        
        if mode == 'start':
            daemon_functions.start_linux_proccess()
        elif mode == 'stop':
            daemon_functions.stop_linux_proccess()
        elif mode == 'restart':
            daemon_functions.restart_linux_proccess()
            

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







