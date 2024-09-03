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
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
@click.command("clean", context_settings=util.context_settings())
@click.pass_context
@options.project_dir_option
@options.board_option_gen()
@options.verbose_option
def cli(
    ctx,
    # Options
    project_dir: Path,
    board: str,
    verbose: bool,
):
    """Clean the previous generated files."""

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Build the project with the given parameters
    exit_code = scons.clean({"board": board, "verbose": {"all": verbose}})

    # -- Done!
    ctx.exit(exit_code)
