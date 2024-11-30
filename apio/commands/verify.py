# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio verify' command"""

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
The command 'apio verify' has been deprecated. Please use the command
'apio lint' instead.
"""


@click.command(
    "verify",
    short_help="[Depreciated] Verify the verilog code.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.board_option_gen(deprecated=True)
def cli(
    _: click.core.Context,
    # Options
    project_dir: Path,
    verbose: bool,
    # Deprecated options
    board: str,
):
    """Implements the verify command."""

    click.secho(
        "The 'apio verify' command is deprecated. "
        "Please use the 'apio lint' command instead.",
        fg="yellow",
    )

    # -- Crete the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=True)

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Verify the project with the given parameters
    exit_code = scons.verify(
        {
            "board": board,
            "verbose_all": verbose,
        }
    )

    # -- Done!
    sys.exit(exit_code)
