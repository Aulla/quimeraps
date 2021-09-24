import logging, sys, os, time

LOGGER = logging.getLogger(__name__)
PID_FILE = '/var/run/quimeraps.pid'
PID_LOCK_FILE = "%s.lock" % PID_FILE

def start_windows_service():
    from quimeraps.json_srv import main_service  
    instance = main_service.JsonClass()
    instance.run()

def restart_linux_proccess():
    stop_linux_proccess()
    time.sleep(2)
    start_linux_proccess()

def start_linux_proccess():

    import daemon
    import lockfile
    from quimeraps.json_srv import main_service

    
    if os.path.exists(PID_LOCK_FILE):
        LOGGER.warning("Daemon is already active.")
        return
    with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, pidfile=lockfile.FileLock(PID_FILE)):
        pid = os.getpid()
        file_ = open(PID_LOCK_FILE, 'w', encoding='UTF-8')
        file_.write(str(pid))
        file_.close()
        instance = main_service.JsonClass()
        instance.run()

def stop_linux_proccess():

    if os.path.exists(PID_LOCK_FILE):
        pid_ = open(PID_LOCK_FILE, 'r').readline()
        if pid_:
            os.system('kill %s' % pid_)
    
        time.sleep(2)
        if os.path.exists(PID_LOCK_FILE):
            os.remove(PID_LOCK_FILE)