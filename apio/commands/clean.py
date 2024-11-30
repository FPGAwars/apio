# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio clean' command"""

import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The clean command deletes the temporary files that were generated
in the project directory by previous apio commands.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Example:
  apio clean

[Hint] If you are using a git repository, add a .gitignore file with
the temporary apio file names.
"""


@click.command(
    "clean",
    short_help="Delete the apio generated files.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.board_option_gen(deprecated=True)
def cli(
    _: click.core.Context,
    # Options
    project_dir: Path,
    # Deprecated options.
    board: str,
):
    """Implements the apio clean command. It deletes temporary files generated
    by apio commands.
    """

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=True)

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Build the project with the given parameters
    exit_code = scons.clean({"board": board})

    # -- Done!
    sys.exit(exit_code)
