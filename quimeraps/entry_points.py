from PyQt6 import QtWidgets

import logging
import sys
from typing import List
import os
import time

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


def startup_server():
    
    
    instance = None
    LOGGER.setLevel(logging.INFO)   

    if sys.platform.startswith('win'): 
        start_windows_service()
    else:
        mode = sys.argv[1] if len(sys.argv) > 1 else None
        if not mode:
            LOGGER.warning("Mode is not specified.")
        
        pid_file = '/var/run/quimeraps.pid'
        

        if mode == 'start':
            start_linux_proccess(pid_file)

        elif mode == 'stop':
            stop_linux_proccess(pid_file)
        elif mode == 'restart':
            stop_linux_proccess(pid_file)
            time.sleep(2)
            start_linux_proccess(pid_file)

def install_service():
    """Install daemon."""

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



def start_windows_service():
    from quimeraps.json_srv import main_service  
    instance = main_service.JsonClass()
    instance.run()

def start_linux_proccess(pid_file):

    import daemon
    import lockfile
    from quimeraps.json_srv import main_service

    pid_file_lock = '%s.lock' % pid_file

    
    if os.path.exists(pid_file_lock):
        LOGGER.warning("Daemon is already active.")
        return
    with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, pidfile=lockfile.FileLock(pid_file)):
        pid = os.getpid()
        file_ = open(pid_file_lock, 'w', encoding='UTF-8')
        file_.write(str(pid))
        file_.close()
        instance = main_service.JsonClass()
        instance.run()

def stop_linux_proccess(pid_file):
    pid_file_lock = '%s.lock' % pid_file

    if os.path.exists(pid_file_lock):
        pid_ = open(pid_file_lock, 'r').readline()
        if pid_:
            os.system('kill -9 %s' % pid_)

        os.remove(pid_file_lock)



