#!venv/bin/python
"""Run apio for debugging"""
# ------------------------------------------------
# -- Run apio for debugging
# -- It is not part of apio (it is not installed).
# --  It is just a launcher for the developers
#-------------------------------------------------

import sys

from click.testing import CliRunner

# -- Import the apio entry point
from apio.__main__ import cli as apio

# -- Read the arguments
cmds = sys.argv[1:]

#-- Execute "apio cmds"
result = CliRunner().invoke(apio, cmds)

#-- Print the command output on the console
print(result.output)
