# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Misc debug related utilities."""

# -- We keep the dependencies very minimal to make sure it can be
# -- used in any context.
import sys
import os


def debug_level() -> int:
    """Returns the current debug level, with 0 as 'off'."""

    # -- We get a fresh value so it can be adjusted dynamically when needed.
    level_str = os.environ.get("APIO_DEBUG", "0")

    # -- For windows benefit, remove optional quotes, same as
    # -- env_options.get() does.
    if (
        len(level_str) >= 2
        and level_str.startswith('"')
        and level_str.endswith('"')
    ):
        level_str = level_str[1:-1]

    try:
        level_int = int(level_str)

    except ValueError:
        # -- This module is intentionally not dependent on apio_console so
        # -- we use simple print and sys.exit() instead of calling fatal_error.
        print(f"Error: env value APIO_DEBUG [{level_str}] is not an int.")
        sys.exit(1)

    # -- All done. We don't validate the value, assuming the caller
    # -- knows how to use it.
    return level_int


def is_debug(level: int) -> bool:
    """Returns True if apio is in debug mode level 'level'  or higher. Use
    it to enable printing of debug information but not to modify the behavior
    of the code. Also, all apio tests should be performed with debug
    disabled. Important debug information should be at level 1 while
    less important or spammy should be at higher levels."""

    assert isinstance(level, int), type(level)
    assert 1 <= level <= 10, level

    return debug_level() >= level


def is_under_vscode_debugger() -> bool:
    """Returns true if running under VSCode debugger."""
    if os.environ.get("DEBUGPY_RUNNING"):
        return True
    return False
