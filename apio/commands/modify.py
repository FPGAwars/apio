# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO MODIFY command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.project import Project
from apio import util
from apio.commands import options


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
    context_settings=util.context_settings(),
)
@click.pass_context
@options.board_option_gen(help="Set the board.")
@options.top_module_option_gen(help="Set the top level module name.")
@options.project_dir_option
def cli(
    ctx: Context,
    # Options
    board: str,
    top_module: str,
    project_dir: Path,
):
    """Modify the project file."""

    if not (board or top_module):
        click.secho(
            "Error: at least one of --board or --top-module must be "
            "specified.\n"
            "Type 'apio modify -h' for help.",
            fg="red",
        )
        ctx.exit(0)

    # pylint: disable=fixme
    # TODO: Make the default Path(".") in get_project_dir and delete this.
    # It preserves the user provided relative path and is more friendly.
    if not project_dir:
        project_dir = Path(".")

    project_dir = util.get_project_dir(project_dir)

    # Create the apio.ini file
    ok = Project.modify_ini_file(project_dir, board, top_module)

    exit_code = 0 if ok else 1
    ctx.exit(exit_code)
