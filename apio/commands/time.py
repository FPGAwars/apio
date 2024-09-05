# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO time command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable=R0801
# R0913: Too many arguments (10/5)
# pylint: disable=R0913
@click.command("time", context_settings=util.context_settings())
@click.pass_context
@options.board_option_gen()
@options.fpga_option
@options.size_option
@options.type_option
@options.pack_option
@options.project_dir_option
@options.verbose_option
@options.verbose_yosys_option
@options.verbose_pnr_option
def cli(
    ctx,
    # Options
    board: str,
    fpga: str,
    size: str,
    type_: str,
    pack: str,
    project_dir: Path,
    verbose: bool,
    verbose_yosys: bool,
    verbose_pnr: bool,
):
    """Analyze the design and report timing."""

    # -- Create the scons object
    scons = SCons(project_dir)

    # Run scons
    exit_code = scons.time(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": type_,
            "pack": pack,
            "verbose": {
                "all": verbose,
                "yosys": verbose_yosys,
                "pnr": verbose_pnr,
            },
        }
    )

    # -- Done!
    ctx.exit(exit_code)
