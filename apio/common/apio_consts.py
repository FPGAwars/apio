# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""General apio constants. Used by both the apio process (parent) and the
scons process (child)"""

from pathlib import Path

# -- The build directory. This is a relative path from the project directory.
BUILD_DIR = Path("_build")

# -- Target name. This is the base file name for various build artifacts.
TARGET = str(BUILD_DIR / "hardware")
