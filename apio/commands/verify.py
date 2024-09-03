# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO VERIFY command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
@click.command("verify", context_settings=util.context_settings())
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
    """Verify project's verilog code."""

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Verify the project with the given parameters
    exit_code = scons.verify(
        {
            "board": board,
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
        }
    )

    # -- Done!
    ctx.exit(exit_code)
