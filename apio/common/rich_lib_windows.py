# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Functions to workaround the rich library bugs when stdout is piped out
on windows."""

import sys
import rich.console
from apio.common.proto.apio_pb2 import RichLibWindowsParams

# For accessing rich.console._windows_console_features
# pylint: disable=protected-access


def get_workaround_parametes() -> RichLibWindowsParams:
    """Called on the apio (parent) process side, when running on windows,
    to collect the parameters for the rich library workaround."""
    print("*** get_workaround_parametes()")
    result = RichLibWindowsParams(
        stdout_encoding=sys.stdout.encoding,
        vt=rich.console._windows_console_features.vt,
        truecolor=rich.console._windows_console_features.truecolor,
    )
    assert result.IsInitialized(), result
    return result


def apply_workaround(params: RichLibWindowsParams):
    """Called on the scons (child) process side, when running on windows,
    to apply the the workaround for the rich library."""
    print("*** apply_workaround()")
    assert params.IsInitialized, params

    # This takes care of the table graphic box.
    # https://github.com/Textualize/rich/issues/3625
    sys.stdout.reconfigure(encoding=params.stdout_encoding)

    # This enables the colors.
    # https://github.com/Textualize/rich/issues/3082
    assert rich.console._windows_console_features is not None
    rich.console._windows_console_features.vt = params.vt
    rich.console._windows_console_features.truecolor = params.truecolor
