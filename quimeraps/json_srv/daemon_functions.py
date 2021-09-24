import logging, sys, os, time

LOGGER = logging.getLogger(__name__)
SERVICE_FILE_NAME = '/etc/systemd/system/quimeraps.service'
SERVICE_NAME='quimeraps'

def start():
    from quimeraps.json_srv import main_service  
    instance = main_service.JsonClass()
    instance.run()


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
    data.append('ExecStart=quimeraps_server')
    #data.append('')
    #data.append('[Install]')
    #data.append('WantedBy=multi-user.target')

    file_ = open(SERVICE_FILE_NAME, 'w', encoding='UTF-8')
    file_.writelines(['%s\n' % line for line in data])
    file_.close()

    LOGGER.warning("File %s created" % SERVICE_FILE_NAME)
    os.system('systemctl daemon-reload')
    #os.system('update-rc.d %s defaults' % SERVICE_NAME)
    #os.system("service quimeraps start")
    # TODO: inicializar servicio al arrancar

def remove_linux_daemon():
    if os.path.exists(SERVICE_FILE_NAME):
        os.system("service quimeraps stop")
        os.remove(SERVICE_FILE_NAME)
        #os.system('update-rc.d -f %s remove' % SERVICE_NAME)


def install_windows_service():
    # TODO: recoger ruta correcta
    real_path = os.path.dirname(os.path.realpath(__file__))
    os.system('sc.exe create %s binPath= "%s/quimeraps_server.exe"' % (SERVICE_NAME,real_path))

def remove_windows_service():
     os.system('sc.exe delete %s' % (SERVICE_NAME))