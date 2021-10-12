"""Logging module."""
import logging
from logging import handlers
import sys
import os

# https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout


def getLogger(name: str = None) -> "logging.Logger":
    """Return a custom logger."""
    log_file = (
        "/var/log/quimeraps.log"
        if not sys.platform.startswith("win")
        else os.path.join(os.environ["ProgramFiles"], "quimeraPS", "quimera.log")
    )

    log: "logging.Logger" = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    format: "logging.Formatter" = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler: "logging.StreamHandler" = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(format)
    log.addHandler(stream_handler)

    file_handler = handlers.RotatingFileHandler(log_file, maxBytes=(1048576 * 5), backupCount=7)
    file_handler.setFormatter(format)
    log.addHandler(file_handler)

    return log
