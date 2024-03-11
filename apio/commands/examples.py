# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Main implementation of APIO EXAMPLES command"""

from pathlib import Path

import click

from apio.managers.examples import Examples
from apio import util


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# pylint: disable=W0622
@click.command("examples", context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-l", "--list", "_list", is_flag=True, help="List all available examples."
)
@click.option(
    "-d",
    "--dir",
    type=str,
    metavar="name",
    help="Copy the selected example directory.",
)
@click.option(
    "-f",
    "--files",
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
    "--sayno",
    is_flag=True,
    help="Automatically answer NO to all the questions.",
)
def cli(
    ctx, _list: bool, dir: str, files: str, project_dir: Path, sayno: bool
):
    """Manage verilog examples.\n
    Install with `apio install examples`"""

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
