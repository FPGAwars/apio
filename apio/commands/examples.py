# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio examples' command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.examples import Examples
from apio import util
from apio.commands import options

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
dir_option = click.option(
    "dir_",  # Var name. Deconflicting with python builtin 'dir'.
    "-d",
    "--dir",
    type=str,
    metavar="name",
    help="Copy the selected example directory.",
    cls=util.ApioOption,
)

files_option = click.option(
    "files",  # Var name.
    "-f",
    "--files",
    type=str,
    metavar="name",
    help="Copy the selected example files.",
    cls=util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The examples command allows to list the project examples provided by api
and to copy them to a local directory. Each examples is identified by
board/name where board is the board id and name is the example name.

\b
Examples:
  apio examples --list            # List all examples
  apio examples -f icezum/leds    # Fetch example files
  apio examples -s icezum/leds    # Fetch example directory
  apio examples -d icezum         # Fetch all board examples
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    "examples",
    short_help="List and fetch apio examples.",
    help=HELP,
    cls=util.ApioCommand,
)
@click.pass_context
@options.list_option_gen(help="List all available examples.")
@dir_option
@files_option
@options.project_dir_option
@options.sayno
def cli(
    ctx: Context,
    # Options
    list_: bool,
    dir_: str,
    files: str,
    project_dir: Path,
    sayno: bool,
):
    """Manage verilog examples.\n
    Install with `apio install examples`"""

    # -- Access to the Drivers
    examples = Examples()

    # -- Option: List all the available examples
    if list_:
        exit_code = examples.list_examples()

    # -- Option: Copy the directory
    elif dir_:
        exit_code = examples.copy_example_dir(dir_, project_dir, sayno)

    # -- Option: Copy only the example files (not the initial folders)
    elif files:
        exit_code = examples.copy_example_files(files, project_dir, sayno)

    # -- no options: Show help!
    else:
        click.secho(ctx.get_help())
        exit_code = 0

    ctx.exit(exit_code)
