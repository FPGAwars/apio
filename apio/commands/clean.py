# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO CLEAN command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The clean command deletes the temporary files that were generated
in the project directory by previous apio commands.
The commands is typically used in the root directory
of the project that that contains the apio.ini file.

\b
Example:
  apio clean

[Note] The flags marked with (deprecated) are not recomanded.
Instead, use an apio.ini project config file and if neaded, add
to the project custom boards.json and fpga.json files.

[Hint] If you are using a git repository, add a .gitignore file with
the temporary apio file names.
"""


@click.command(
    "clean",
    short_help="Clean the apio generated files.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.board_option_gen()
def cli(
    ctx: Context,
    # Options
    project_dir: Path,
    verbose: bool,
    # Deprecated options.
    board: str,
):
    """Implements the apio clean command. It deletes temporary files generated
    by apio commands.
    """

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Build the project with the given parameters
    exit_code = scons.clean({"board": board, "verbose": {"all": verbose}})

    # -- Done!
    ctx.exit(exit_code)
