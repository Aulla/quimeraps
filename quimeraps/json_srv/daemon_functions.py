import logging, sys, os, time

LOGGER = logging.getLogger(__name__)
PID_FILE = '/var/run/quimeraps.pid'
PID_LOCK_FILE = "%s.lock" % PID_FILE
SERVICE_FILE_NAME = '/etc/systemd/system/quimeraps.service'

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

def install_linux_daemon():
    from quimeraps import __VERSION__
    if os.path.exists(SERVICE_FILE_NAME):
        os.system("service quimeraps stop")
        os.remove(SERVICE_FILE_NAME)
    
    data = []
    data.append('# Quimera print service v%s' % __VERSION__)
    data.append('[Unit]')
    data.append('Description=Quimera print service')
    #data.append('After=network.target')
    data.append('StartLimitIntervalSec=0')
    data.append('')
    data.append('[Service]')
    data.append('Type=simple')
    data.append('Restart=always')
    data.append('RestartSec=1')
    data.append('User=root')
    data.append('ExecStart=quimeraps_server start')
    #data.append('')
    #data.append('[Install]')
    #data.append('WantedBy=multi-user.target')

    file_ = open(SERVICE_FILE_NAME, 'w', encoding='UTF-8')
    file_.writelines(['%s\n' % line for line in data])
    file_.close()

    LOGGER.warning("File %s created" % SERVICE_FILE_NAME)
    os.system('systemctl daemon-reload')
    #os.system("service quimeraps start")

def remove_linux_daemon():
    if os.path.exists(SERVICE_FILE_NAME):
        os.system("service quimeraps stop")
        os.remove(SERVICE_FILE_NAME)