# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Helper functions for apio scons plugins.
"""

import os
import click
import debugpy


def maybe_wait_for_remote_debugger():
    """A rendezvous point for a remote debger. If the environment variable
    'APIO_SCONS_DEBUGGER' is set, the function will block until a remote
    debugger (e.g. from Visual Studio Code) is attached.
    """
    if os.getenv("APIO_SCONS_DEBUGGER") is not None:
        click.secho("Env var 'APIO_SCONS_DEBUGGER' was detected.")
        port = 5678
        click.secho(
            f"Apio SCons for remote debugger on port localhost:{port}."
        )
        debugpy.listen(port)
        click.secho(
            "Attach Visual Studio Code python remote python debugger "
            f"to port {port}.",
            fg="magenta",
            color=True,
        )
        # -- Block until the debugger connetcs.
        debugpy.wait_for_client()
        # -- Here the remote debugger is attached and the program continues.
        click.secho(
            "Remote debugger is attached, program continues...",
            fg="green",
            color=True,
        )
