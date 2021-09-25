"""Daemon functions module."""
from quimeraps.json_srv import logging
import os

LOGGER = logging.getLogger(__name__)
SERVICE_FILE_NAME = "/etc/systemd/system/quimeraps.service"
SERVICE_NAME = "quimeraps"


def start():
    """Initialice an start json-rpc server instance."""
    from quimeraps.json_srv import main_service

    # TODO: crear log

    instance = main_service.JsonClass()
    instance.run()


def install_linux_daemon():
    """Install quimeraps as a daemon."""
    # https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6

    from quimeraps import __VERSION__

    if os.path.exists(SERVICE_FILE_NAME):
        os.system("service quimeraps stop")
        os.remove(SERVICE_FILE_NAME)

    data = []
    data.append("# Quimera print service v%s" % __VERSION__)
    data.append("[Unit]")
    data.append("Description=Quimera print service")
    # data.append('After=network.target')
    data.append("StartLimitIntervalSec=0")
    data.append("")
    data.append("[Service]")
    data.append("Type=simple")
    data.append("Restart=always")
    data.append("RestartSec=1")
    data.append("User=root")
    data.append("ExecStart=quimeraps_server")
    data.append("")
    data.append("[Install]")
    data.append("WantedBy=multi-user.target")

    file_ = open(SERVICE_FILE_NAME, "w", encoding="UTF-8")
    file_.writelines(["%s\n" % line for line in data])
    file_.close()

    LOGGER.warning("File %s created" % SERVICE_FILE_NAME)
    os.system("systemctl daemon-reload")
    os.system("systemctl enable %s" % SERVICE_FILE_NAME)
    # os.system('update-rc.d %s defaults' % SERVICE_NAME)
    # os.system("service quimeraps start")
    # TODO: inicializar servicio al arrancar


def remove_linux_daemon():
    """Remove daemon from systemd."""
    if os.path.exists(SERVICE_FILE_NAME):
        os.system("service quimeraps stop")
        os.system("systemctl disable %s" % SERVICE_FILE_NAME)
        os.remove(SERVICE_FILE_NAME)
        # os.system('update-rc.d -f %s remove' % SERVICE_NAME)


def install_windows_service():
    """Install quimeraps as a service."""
    # TODO: recoger ruta correcta
    real_path = os.path.dirname(os.path.realpath(__file__))
    os.system('sc.exe create %s binPath= "%s/quimeraps_server.exe"' % (SERVICE_NAME, real_path))


def remove_windows_service() -> None:
    """Remove service from windows."""
    os.system("sc.exe delete %s" % (SERVICE_NAME))
