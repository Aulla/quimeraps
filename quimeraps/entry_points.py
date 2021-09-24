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

    if not mode or mode not in ['install', 'remove']:
        raise Exception("Mode ['install','remove'] is not specified.")

    func_name = "%s_%s_daemon" % (mode, 'windows' if sys.platform.startswith('win') else 'linux')

    func = getattr(daemon_functions, func_name, None)

    if func_name is None:
        raise Exception('Unknown function %s' % func_name)
    else:
        func()






