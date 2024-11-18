# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio modify' command"""

from pathlib import Path
from varname import nameof
import click
from apio.managers.project import Project
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The modify command modifies selected fields in an existing
apio.ini project file. The commands is typically used in
the root directory of the project that contains the apio.ini file.

\b
Examples:
  apio modify --board icezum
  apio modify --board icezum --top-module MyModule
  apio create --top-module MyModule

At least one of the flags --board and --top-module must be specified.

[Hint] Use the command 'apio examples -l' to see a list of
the supported boards.
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    "modify",
    short_help="Modify the apio.ini project file.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.board_option_gen(help="Set the board.")
@options.top_module_option_gen(help="Set the top level module name.")
@options.project_dir_option
def cli(
    cmd_ctx: click.core.Context,
    # Options
    board: str,
    top_module: str,
    project_dir: Path,
):
    """Modify the project file."""

    # At least one of these options are required.
    cmd_util.check_at_least_one_param(cmd_ctx, nameof(board, top_module))

    # Create an apio context.
    apio_ctx = ApioContext(project_dir=project_dir, project_scope=True)

    # Create the apio.ini file
    ok = Project.modify_ini_file(apio_ctx, board, top_module)

    exit_code = 0 if ok else 1
    cmd_ctx.exit(exit_code)
