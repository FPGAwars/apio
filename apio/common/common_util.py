# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utilities that are available for both the apio (parent) process and the
scons (child) process."""

import os
import debugpy
from apio.common.styles import EMPH3, SUCCESS


def maybe_wait_for_remote_debugger(env_var_name: str):
    """A rendezvous point for a remote debugger. If the environment variable
    of given name is set, the function will block until a remote
    debugger (e.g. from Visual Studio Code) is attached.
    """
    if os.getenv(env_var_name) is not None:
        # NOTE: This function may be called before apio_console.py is
        # initialized, so we use print() instead of cout().
        print(f"Env var '{env_var_name}' was detected.")
        port = 5678
        print(f"Apio SCons for remote debugger on port localhost:{port}.")
        debugpy.listen(port)
        print(
            "Attach Visual Studio Code python remote python debugger "
            f"to port {port}.",
            style=EMPH3,
        )
        # -- Block until the debugger connects.
        debugpy.wait_for_client()
        # -- Here the remote debugger is attached and the program continues.
        print(
            "Remote debugger is attached, program continues...",
            style=SUCCESS,
        )
