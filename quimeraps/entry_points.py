"""Entry_points module."""
import sys
import os


def startup_client() -> None:
    """Startup client."""
    from PyQt5 import QtWidgets

    from quimeraps.client_gui import main_window

    app_ = QtWidgets.QApplication(sys.argv + [])
    window = main_window.MainWindow()  # noqa: F841
    sys.exit(app_.exec())


def startup_server() -> None:
    """Starup server."""
    from quimeraps.json_srv import logging
    from quimeraps.json_srv import daemon_functions

    LOGGER = logging.getLogger(__name__)

    if not sys.platform.startswith("win"):
        if os.geteuid() != 0:
            LOGGER.warning("This user is not super!.")
            return
    daemon_functions.start()


def install_daemon() -> None:
    """Install daemon."""
    if not sys.platform.startswith("win"):
        if os.geteuid() != 0:
            import logging

            LOGGER = logging.getLogger(__name__)
            LOGGER.warning("This user is not super!.")
            return

    from quimeraps.json_srv import daemon_functions

    mode = sys.argv[1] if len(sys.argv) > 1 else None

    if not mode or mode not in ["install", "remove"]:
        raise Exception("Mode ['install','remove'] is not specified.")

    func_name = "%s_%s_daemon" % (mode, "windows" if sys.platform.startswith("win") else "linux")

    func = getattr(daemon_functions, func_name, None)

    if func_name is None:
        raise Exception("Unknown function %s" % func_name)
    else:
        func()
