"""Daemon functions module."""
import os

SERVICE_FILE_NAME = "/etc/systemd/system/quimeraps.service"
SERVICE_NAME = "QuimeraPrintService"


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
    # data.append("StartLimitIntervalSec=0")
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

    os.system("systemctl daemon-reload")
    os.system("systemctl enable %s" % SERVICE_FILE_NAME)


def remove_linux_daemon():
    """Remove daemon from systemd."""
    if os.path.exists(SERVICE_FILE_NAME):
        os.system("service quimeraps stop")
        os.system("systemctl disable %s" % SERVICE_FILE_NAME)
        os.remove(SERVICE_FILE_NAME)


def install_windows_daemon():
    """Install quimeraps as a service."""
    # TODO: recoger ruta correcta
    real_path = os.path.dirname(os.path.realpath(os.path.join(__file__, "..", "..", "..", "..")))
    command = 'sc.exe create %s binPath= "%s"' % (
        SERVICE_NAME,
        os.path.join(real_path, "Scripts", "quimeraps_server.exe"),
    )
    print("Comando", command)
    os.system(command)

    # TODO: hacer que sea automatico.
    # TODO: https://nssm.cc/.


def remove_windows_daemon() -> None:
    """Remove service from windows."""
    os.system("sc.exe delete %s" % (SERVICE_NAME))
