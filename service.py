"""Quimera Print Server Package."""

import sys
import logging
from json_srv import main_service


VERSION = "0.0.1"
LOGGER = logging.getLogger(__name__)

def startup() -> bool:
    """Initializa servers."""

    LOGGER.warning("Quimera-ps service v.%s" % (VERSION))
    main_service.JsonClass() 
    LOGGER.warning("\nBye!")

if __name__ == "__main__":
    startup()