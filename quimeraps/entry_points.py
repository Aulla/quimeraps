import logging
import sys

LOGGER = logging.getLogger(__name__)

def startup_client():

    from PyQt6 import QtWidgets

    from quimeraps.client_gui import main_window
    app_ = QtWidgets.QApplication(sys.argv + [])
    window = main_window.MainWindow()
    sys.exit(app_.exec())


def startup_server():
    from quimeraps.json_srv import daemon

    if sys.platform.startswith('win'): 
        daemon.start_windows_service()
    else:
        mode = sys.argv[1] if len(sys.argv) > 1 else None
        if not mode:
            LOGGER.warning("Mode is not specified.")
        
        if mode == 'start':
            daemon.start_linux_proccess()
        elif mode == 'stop':
            daemon.stop_linux_proccess()
        elif mode == 'restart':
            daemon.restart_linux_proccess()
            

def install_service():
    """Install daemon."""

    import os

    mode = sys.argv[1] if len(sys.argv) > 1 else None

    if not mode:
        raise Exception("Mode ['install','remove'] is not specified.")

    service_name = "QuimeraPS"

    if sys.platform.startswith('win'): # Windowzz
        if mode == 'install':
            real_path = os.path.dirname(os.path.realpath(__file__))
            os.system('sc.exe create %s binPath= "%s/quimeraps_server.exe"' % (service_name,real_path))
        elif mode == 'delete':
            os.system('sc.exe delete %s' % (service_name))
    else:
        LOGGER.warning("Option not implemented yet")


    
    LOGGER.warning("The service %s was %sed sucefully." % (service_name, mode))







