"""Quimera Print Server Package."""
import sys
from quimeraps import entry_points

if __name__ == "__main__":
    entry_points.install_daemon()