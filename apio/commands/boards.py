# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO BOARDS command"""

from pathlib import Path
import click
from apio.resources import Resources
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "boards"  # -- Comand name
PROJECT_DIR = "project_dir"  # -- Option
LIST = "list"  # -- Option
FPGA = "fpga"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="str",
    help="Set the target directory for the project.",
)
@click.option(
    "-l",
    f"--{LIST}",
    is_flag=True,
    help="List all supported FPGA boards.",
)
@click.option(
    "-f", f"--{FPGA}", is_flag=True, help="List all supported FPGA chips."
)
def cli(ctx, **kwargs):
    """Manage FPGA boards."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]  # -- str
    _list = kwargs[LIST]  # -- bool
    fpga = kwargs[FPGA]  # -- bool

    # -- Access to the apio resources
    resources = Resources(project_dir=project_dir)

    # -- Option 1: List boards
    if _list:
        resources.list_boards()

    # -- Option 2: List fpgas
    elif fpga:
        resources.list_fpgas()

    # -- No options: show help
    else:
        click.secho(ctx.get_help())
