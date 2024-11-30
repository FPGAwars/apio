# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio upgrade' command"""

import sys
import importlib.metadata
import click
from packaging import version
from apio.util import get_pypi_latest_version
from apio import cmd_util


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The upgrade command checks the version of the latest apio release
and provide upgrade directions if needed.

\b
Examples:
  apio upgrade
"""


@click.command(
    "upgrade",
    short_help="Check the latest Apio version.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
def cli(_: click.core.Context):
    """Check the latest Apio version."""

    # -- Get the current apio version from the python package installed
    # -- on the system
    current_version = importlib.metadata.version("apio")

    # -- Get the latest stable version published at Pypi
    latest_version = get_pypi_latest_version()

    # -- There was an error getting the version from pypi
    if latest_version is None:
        sys.exit(1)

    # -- Print information about apio (Debug)
    print(f"Local Apio version: {current_version}")
    print(f"Lastest Apio stable version (Pypi): {latest_version}")

    # -- Case 1: Using an old version.
    if version.parse(current_version) < version.parse(latest_version):
        click.secho(
            "You're not updated\nPlease execute "
            "`pip install -U apio` to upgrade.",
            fg="yellow",
        )
        return

    # -- Case 2: Using a dev version.
    if version.parse(current_version) > version.parse(latest_version):
        click.secho(
            "You are using a development version! (Not stable)\n"
            "Use it at your own risk",
            fg="yellow",
        )
        return

    # -- Case 3: Using the latest version.
    click.secho(
        f"You're up-to-date!\nApio {latest_version} is currently the "
        "latest stable version available.",
        fg="green",
    )
