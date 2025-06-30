# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Functions to workaround the rich library bugs when stdout is piped out
on windows."""

import sys
import platform
import rich.console


def fix_windows_stdout_encoding() -> bool:
    """Called on the apio process (parent) to fix its output encoding.
    Safe to call on non windows platforms. Returns True if fixed."""
    # -- This takes care of the table graphic box.
    # -- See https://github.com/Textualize/rich/issues/3625
    if (
        platform.system().lower() == "windows"
        and sys.stdout.encoding != "utf-8"
    ):
        sys.stdout.reconfigure(encoding="utf-8")
        return True
    # -- Else.
    return False


def apply_workaround():
    """Called on the scons (child) process side, when running on windows,
    to apply the the workaround for the rich library."""

    # For accessing rich.console._windows_console_features
    # pylint: disable=protected-access

    # -- This takes care of the table graphic box.
    # -- See https://github.com/Textualize/rich/issues/3625
    # sys.stdout.reconfigure(encoding=params.stdout_encoding)

    # This enables the colors.
    # See https://github.com/Textualize/rich/issues/3082

    # -- Make sure that _windows_console_features is initialized with cached
    # -- values.
    rich.console.get_windows_console_features()
    assert rich.console._windows_console_features is not None

    # -- Apply the patch.
    rich.console._windows_console_features.vt = True
    rich.console._windows_console_features.truecolor = True
