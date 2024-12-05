# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio create' command"""

import sys
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
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = f"""
The create command creates the project file apio.ini from scratch.
The commands is typically used in the root directory
of the project where the apio.ini file is created.

\b
Examples:
  apio create --board icezum
  apio create --board icezum --top-module MyModule
  apio create --board icezum --sayyes

The flag --board is required. The flag --top-module is optional and has
the default '{DEFAULT_TOP_MODULE}'. If the file apio.ini already exists
the command asks for permision to delete it. If --sayyes is specified,
the file is deleted automatically.

[Note] this command creates just the '{APIO_INI}' file
rather than a full buildable project.
Some users use instead the examples command to copy a working
project for their board, and then modify it with with their design.

[Hint] Use the command 'apio examples -l' to see a list of
the supported boards.
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    "create",
    short_help="Create an apio.ini project file.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.board_option_gen(help="Set the board.", required=True)
@options.top_module_option_gen(help="Set the top level module name.")
@options.project_dir_option
@options.sayyes
def cli(
    _: click.core.Context,
    # Options
    board: str,
    top_module: str,
    project_dir: Path,
    sayyes: bool,
):
    """Create a project file."""

    # Board is annotated above as required so must exist.
    assert board is not None

    if not top_module:
        top_module = DEFAULT_TOP_MODULE

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=False)

    project_dir = util.get_project_dir(project_dir)

    # -- Map to canonical board id. This fails if the board is unknown.
    board_id = apio_ctx.lookup_board_id(board)

    # Create the apio.ini file
    ok = create_project_file(
        apio_ctx.project_dir,
        board_id,
        top_module,
        sayyes,
    )

    exit_code = 0 if ok else 1
    sys.exit(exit_code)
