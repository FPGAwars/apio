# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Main implementation of APIO BOARDS command"""

import click

from apio.resources import Resources
from apio import util


@click.command("boards", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-l",
    "--list",
    "list_boards",
    is_flag=True,
    help="List all supported FPGA boards.",
)
@click.option(
    "-f", "--fpga", is_flag=True, help="List all supported FPGA chips."
)
def cli(ctx, list_boards: bool, fpga: bool):
    """Manage FPGA boards."""

    # -- Access to the apio resources
    resources = Resources()

    # -- Option 1: List boards
    if list_boards:
        resources.list_boards()

    # -- Option 2: List fpgas
    elif fpga:
        resources.list_fpgas()

    # -- No options: show help
    else:
        click.secho(ctx.get_help())
