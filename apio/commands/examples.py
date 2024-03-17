# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO EXAMPLES command"""

from pathlib import Path
import click
from apio.managers.examples import Examples
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "examples"  # -- Comand name
LIST = "list"  # -- Option
DIR = "dir"  # -- Option
FILES = "files"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option
SAYNO = "sayno"  # -- Option


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# pylint: disable=W0622
@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-l", f"--{LIST}", is_flag=True, help="List all available examples."
)
@click.option(
    "-d",
    f"--{DIR}",
    type=str,
    metavar="name",
    help="Copy the selected example directory.",
)
@click.option(
    "-f",
    f"--{FILES}",
    type=str,
    metavar="name",
    help="Copy the selected example files.",
)
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="project_dir",
    help="Set the target directory for the project.",
)
@click.option(
    "-n",
    f"--{SAYNO}",
    is_flag=True,
    help="Automatically answer NO to all the questions.",
)
def cli(ctx, **kwargs):
    """Manage verilog examples.\n
    Install with `apio install examples`"""

    # -- Extract the arguments
    _list = kwargs[LIST]
    dir = kwargs[DIR]
    files = kwargs[FILES]
    project_dir = kwargs[PROJECT_DIR]
    sayno = kwargs[SAYNO]

    # -- Access to the Drivers
    examples = Examples()

    # -- Option: List all the available examples
    if _list:
        exit_code = examples.list_examples()

    # -- Option: Copy the directory
    elif dir:
        exit_code = examples.copy_example_dir(dir, project_dir, sayno)

    # -- Option: Copy only the example files (not the initial folders)
    elif files:
        exit_code = examples.copy_example_files(files, project_dir, sayno)

    # -- no options: Show help!
    else:
        click.secho(ctx.get_help())
        click.secho(examples.examples_of_use_cad())
        exit_code = 0

    ctx.exit(exit_code)
