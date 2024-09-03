# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO BUILD command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
# R0913: Too many arguments (11/5)
# pylint: disable=R0913
@click.command("build", context_settings=util.context_settings())
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
@options.top_module_option_gen()
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
    top_module: str,
):
    """Synthesize the bitstream."""

    # The bitstream is generated from the source files (verilog)
    # by means of the scons tool
    # https://www.scons.org/documentation.html

    # -- Create the scons object
    scons = SCons(project_dir)

    # R0801: Similar lines in 2 files
    # pylint: disable=R0801
    # -- Build the project with the given parameters
    exit_code = scons.build(
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
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build
