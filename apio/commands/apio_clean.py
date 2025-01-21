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
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope


# ---------------------------
# -- COMMAND
# ---------------------------
APIO_CLEAN_HELP = """
The command 'apio clean' removes temporary files generated in the project
directory by previous Apio commands.

\b
Example:
  apio clean

"""


@click.command(
    name="clean",
    short_help="Delete the apio generated files.",
    help=APIO_CLEAN_HELP,
)
@click.pass_context
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    project_dir: Path,
):
    """Implements the apio clean command. It deletes temporary files generated
    by apio commands.
    """

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED,
        project_dir_arg=project_dir,
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Build the project with the given parameters
    exit_code = scons.clean()

    # -- Done!
    sys.exit(exit_code)
