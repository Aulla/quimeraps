"""Quimera Print Service Package."""

import os, sys

DATA_DIR = os.path.join(os.environ["ProgramFiles"] if sys.platform.startswith('win') else 'opt', 'quimeraPS') 
__VERSION__ = "0.9.2"




