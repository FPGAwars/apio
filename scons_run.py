#!venv/bin/python
"""Run scons for debugging"""

# ---------------------------------------------------
# -- Run scons for debugging by apio developers.
# -- It is not part of apio and is not installed.
# ---------------------------------------------------

# Apio developers, you can run it directly from
# command line or via Visual Studio Code debug
# targets at .vscode/launch.json.

import sys
import SCons.Script

try:
    SCons.Script.main()

except SystemExit as e:
    print(f"Scons exit code: {e.code}")
