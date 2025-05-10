# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio clean' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import cmd_util


# ----------- apio clean

# -- Text in the rich-text format of the python rich library.
APIO_CLEAN_HELP = """
The command 'apio clean' removes temporary files generated in the project \
directory by previous Apio commands.

Example:[code]
  apio clean[/code]
"""


@click.command(
    name="clean",
    cls=cmd_util.ApioCommand,
    short_help="Delete the apio generated files.",
    help=APIO_CLEAN_HELP,
)
@click.pass_context
@options.env_option
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    env: Optional[str],
    project_dir: Optional[Path],
):
    """Implements the apio clean command. It deletes temporary files generated
    by apio commands.
    """

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Build the project with the given parameters
    exit_code = scons.clean()

    # -- Done!
    sys.exit(exit_code)
