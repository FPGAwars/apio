# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import importlib.metadata
import click

from apio.util import get_pypi_latest_version


@click.command("upgrade")
@click.pass_context
def cli(ctx):
    """Check the latest Apio version."""

    current_version = importlib.metadata.version("apio")
    latest_version = get_pypi_latest_version()

    if latest_version is None:
        ctx.exit(1)

    if latest_version == current_version:
        click.secho(
            f"You're up-to-date!\nApio {latest_version} is currently the "
            "newest version available.",
            fg="green",
        )
    else:
        click.secho(
            "You're not updated\nPlease execute "
            "`pip install -U apio` to upgrade.",
            fg="yellow",
        )
