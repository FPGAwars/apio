#!venv/bin/python
"""Run apio for debugging"""
# ------------------------------------------------
# -- Run apio for debugging
# -- It is not part of apio (it is not installed).
# --  It is just a launcher for the developers
#-------------------------------------------------

import sys

# -- Import the apio entry point
from apio.__main__ import cli as apio

#-- Run apio!
try:
    apio(None)

#-- Apio commands finish with this excepcion
except SystemExit:
    print("Apio command executed!")

#-- Exit!
sys.exit()
