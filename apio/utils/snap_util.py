# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Misc utility functions related to the linux Snap package manager."""

import os
import subprocess
from subprocess import CompletedProcess
import shutil

RAW_USB_PLUG = "raw-usb"
SERIAL_PORT_PLUG = "serial-port"

MANUAL_PLUGS = [RAW_USB_PLUG, SERIAL_PORT_PLUG]


def is_snap() -> bool:
    """Returns True if the current process is running under snap."""
    val = os.getenv("SNAP_NAME")
    return val is not None


def is_plug_connected(plug: str) -> bool:
    """Returns the given manual snap plug is connected. Should be called only
    if running under snap."""
    # -- Check the preconditions.
    assert is_snap(), "Not running under snap."
    assert plug in MANUAL_PLUGS, f"Unexpected snap plug: {plug}"
    assert shutil.which("snapctl"), "The command 'snapctl' is not available."
    # -- Query the plug state.
    result: CompletedProcess = subprocess.run(
        ["snapctl", "is-connected", plug], check=False
    )
    return result.returncode == 0
