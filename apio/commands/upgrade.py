# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import importlib.metadata
import click

from packaging import version
from apio.util import get_pypi_latest_version


@click.command("upgrade")
@click.pass_context
def cli(ctx):
    """Check the latest Apio version."""

    # -- Get the current apio version from the python package installed
    # -- on the system
    current_version = importlib.metadata.version("apio")

    # -- Get the latest stable version published at Pypi
    latest_version = get_pypi_latest_version()

    # -- There was an error getting the version from pypi
    if latest_version is None:
        ctx.exit(1)

    # -- Print information about apio (Debug)
    print(f"Local Apio version: {current_version}")
    print(f"Lastest Apio stable version (Pypi): {latest_version}")

    # -- Compare versions and inform the user
    # -- No real action are taken!
    if version.parse(current_version) < version.parse(latest_version):
        click.secho(
            "You're not updated\nPlease execute "
            "`pip install -U apio` to upgrade.",
            fg="yellow",
        )
    elif version.parse(current_version) > version.parse(latest_version):
        click.secho(
            "You are using a development version! (Not stable)\n"
            "Use it at your own risk",
            fg="yellow",
        )
    else:
        click.secho(
            f"You're up-to-date!\nApio {latest_version} is currently the "
            "latest stable version available.",
            fg="green",
        )
