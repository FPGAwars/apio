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

# R0801: Similar lines in 2 files
# pylint: disable=R0801
# ------------------
# -- CONSTANTS
# ------------------
CMD = "build"  # -- Comand name
BOARD = "board"  # -- Option
FPGA = "fpga"  # -- Option
PACK = "pack"  # -- Option
TYPE = "type"  # -- Option
SIZE = "size"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option
VERBOSE = "verbose"  # -- Option
VERBOSE_YOSYS = "verbose_yosys"  # -- Option
VERBOSE_PNR = "verbose_pnr"  # -- Option
TOP_MODULE = "top_module"  # -- Option


# pylint: disable=R0801
# R0801: Similar lines in 2 files
@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-b", f"--{BOARD}", type=str, metavar="str", help="Set the board."
)
@click.option(f"--{FPGA}", type=str, metavar="str", help="Set the FPGA.")
@click.option(
    f"--{SIZE}", type=str, metavar="str", help="Set the FPGA type (1k/8k)."
)
@click.option(
    f"--{TYPE}", type=str, metavar="str", help="Set the FPGA type (hx/lp)."
)
@click.option(
    f"--{PACK}", type=str, metavar="str", help="Set the FPGA package."
)
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="str",
    help="Set the target directory for the project.",
)
@click.option(
    "-v",
    f"--{VERBOSE}",
    is_flag=True,
    help="Show the entire output of the command.",
)
@click.option(
    "--verbose-yosys",
    is_flag=True,
    help="Show the yosys output of the command.",
)
@click.option(
    "--verbose-pnr", is_flag=True, help="Show the pnr output of the command."
)
@click.option(
    "--top-module",
    type=str,
    metavar="str",
    help="Set the top level module (w/o .v ending) for build.",
)
def cli(ctx, **kwargs):
    """Synthesize the bitstream."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    board = kwargs[BOARD]
    fpga = kwargs[FPGA]
    pack = kwargs[PACK]
    _type = kwargs[TYPE]
    size = kwargs[SIZE]
    verbose = kwargs[VERBOSE]
    verbose_yosys = kwargs[VERBOSE_YOSYS]
    verbose_pnr = kwargs[VERBOSE_PNR]
    top_module = kwargs[TOP_MODULE]

    # The bitstream is generated from the source files (verilog)
    # by means of the scons tool
    # https://www.scons.org/documentation.html

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Build the project with the given parameters
    exit_code = scons.build(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": _type,
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
