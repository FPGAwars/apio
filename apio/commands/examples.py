# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio examples' command"""

import sys
from pathlib import Path
from varname import nameof
import click
from apio.managers.examples import Examples
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
dir_option = click.option(
    "fetch_dir",  # Var name.
    "-d",
    "--fetch-dir",
    type=str,
    metavar="name",
    help="Fetch the selected example directory.",
    cls=cmd_util.ApioOption,
)

files_option = click.option(
    "fetch_files",  # Var name.
    "-f",
    "--fetch-files",
    type=str,
    metavar="name",
    help="Fetch the selected example files.",
    cls=cmd_util.ApioOption,
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
  apio examples --list               # List all examples
  apio examples -l | grep -i icezum  # Filter examples.
  apio examples -f icezum/leds       # Fetch example files
  apio examples -d icezum/leds       # Fetch example directory
  apio examples -d icezum            # Fetch all board examples
"""

EPILOG = """
The format of 'name' is <board>[/<example>], where <board> is a board
name (e.g. 'icezum') and <example> is a name of an example of that
board (e.g. 'leds').
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "examples",
    short_help="List and fetch apio examples.",
    help=HELP,
    epilog=EPILOG,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.list_option_gen(help="List all available examples.")
@dir_option
@files_option
@options.project_dir_option
@options.sayno
def cli(
    cmd_ctx: click.core.Context,
    # Options
    list_: bool,
    fetch_dir: str,
    fetch_files: str,
    project_dir: Path,
    sayno: bool,
):
    """Manage verilog examples.\n
    Install with `apio packages --install examples`"""

    # Make sure these params are exclusive.
    cmd_util.check_exactly_one_param(
        cmd_ctx, nameof(list_, fetch_dir, fetch_files)
    )

    # -- Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the examples manager.
    examples = Examples(apio_ctx)

    # -- Option: Copy the directory
    if fetch_dir:
        exit_code = examples.copy_example_dir(fetch_dir, project_dir, sayno)
        sys.exit(exit_code)

    # -- Option: Copy only the example files (not the initial folders)
    if fetch_files:
        exit_code = examples.copy_example_files(
            fetch_files, project_dir, sayno
        )
        sys.exit(exit_code)

    # -- Option: List all the available examples
    assert list_
    exit_code = examples.list_examples()
    sys.exit(exit_code)
