"""Quimera Print Server Package."""

import sys
import logging
from quimeraps.json_srv import main_service

LOGGER = logging.getLogger(__name__)

def startup() -> bool:
    """Initializa servers."""

    main_service.JsonClass() 
    LOGGER.warning("\nBye!")

if __name__ == "__main__":
    startup()