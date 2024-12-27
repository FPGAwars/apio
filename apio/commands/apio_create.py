# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio create' command"""

from pathlib import Path
import click
from apio.managers.project import (
    DEFAULT_TOP_MODULE,
    APIO_INI,
    create_project_file,
)
from apio import util
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope


board_option = click.option(
    "board",  # Var name.
    "-b",
    "--board",
    type=str,
    required=True,
    metavar="board_id",
    help="Set the board.",
    cls=cmd_util.ApioOption,
)

# ---------------------------
# -- COMMAND
# ---------------------------
HELP = f"""
The 'apio create' command creates a new apio.ini project file and may
be use when creating a new apio project.

\b
Examples:
  apio create --board alhambra-ii
  apio create --board alhambra-ii --top-module MyModule

The flag --board is required. The flag --top-module is optional and has
the default '{DEFAULT_TOP_MODULE}'. If the file apio.ini already exists
the command exists with an error message.

[Note] this command creates just the '{APIO_INI}' file
rather than a complete and buildable project.
Some users use instead the'apio examples' command to copy a working
project for their board, and then modify it with with their design.
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    name="create",
    short_help="Create an apio.ini project file.",
    help=HELP,
)
@click.pass_context
@board_option
@options.top_module_option_gen(help="Set the top level module name.")
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    board: str,
    top_module: str,
    project_dir: Path,
):
    """Create a project file."""

    # Board is annotated above as required so must exist.
    assert board is not None

    if not top_module:
        top_module = DEFAULT_TOP_MODULE

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Map to canonical board id. This fails if the board is unknown.
    board_id = apio_ctx.lookup_board_id(board)

    # -- Map the optional project dir argument to an actual project dir.
    project_dir = util.resolve_project_dir(project_dir, create_if_missing=True)

    # Create the apio.ini file. It exists with an error status if any error.
    create_project_file(
        project_dir,
        board_id,
        top_module,
    )
