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
from click.core import Context
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The time command analyzes
and reports the timing of the design. It is useful to determine the
maximal clock rate that the FPGA can handle with this design. For more
detailed timing information, inspect the file 'hardware.rpt' that the
command generates.
The commands is typically used in the root directory
of the project that that contains the apio.ini file.

\b
Examples:
  apio time

[Note] The flags marked with (deprecated) are not recomanded.
Instead, use an apio.ini project config file and if neaded, add
to the project custom boards.json and fpga.json files.
"""


# R0801: Similar lines in 2 files
# pylint: disable=R0801
# R0913: Too many arguments (10/5)
# pylint: disable=R0913
@click.command(
    "time",
    short_help="Report design timing.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.verbose_yosys_option
@options.verbose_pnr_option
@options.top_module_option_gen()
@options.board_option_gen()
@options.fpga_option
@options.size_option
@options.type_option
@options.pack_option
def cli(
    ctx: Context,
    # Options
    project_dir: Path,
    verbose: bool,
    verbose_yosys: bool,
    verbose_pnr: bool,
    # Deprecated options
    top_module: str,
    board: str,
    fpga: str,
    size: str,
    type_: str,
    pack: str,
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
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
