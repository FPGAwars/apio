# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Common APIO command options"""

from pathlib import Path
import click

# APIO command options in alphabetial order.
# The design is based on the idea here https://stackoverflow.com/a/77732441.
#
# Each option is defined by two values:
# 1. (UPPER CASE) The python key for the option value.
# 2. (lower_case) The click decoration that defines the option.

# -- Board
BOARD = "board"
board = click.option(
    "-b",
    "--board",
    BOARD,
    type=str,
    metavar="str",
    help="Set the board.",
)

# -- FPGA model.
FPGA = "fpga"
fpga = click.option(
    "--fpga", FPGA, type=str, metavar="str", help="Set the FPGA."
)

# -- FPGA package.
PACK = "pack"
pack = click.option(
    "--pack", PACK, type=str, metavar="str", help="Set the FPGA package."
)

# -- Project dir
PROJECT_DIR = "project_dir"
project_dir = click.option(
    "-p",
    "--project-dir",
    PROJECT_DIR,
    type=Path,
    metavar="str",
    help="Set the target directory for the project.",
)

# -- FPGA size.
SIZE = "size"
size = click.option(
    "--size", SIZE, type=str, metavar="str", help="Set the FPGA type (1k/8k)."
)

# -- Top Verilog module.
TOP_MODULE = "top_module"
top_module = click.option(
    "--top-module",
    TOP_MODULE,
    type=str,
    metavar="str",
    help="Set the top level module (w/o .v ending) for build.",
)

# -- FPGA type.
TYPE = "type"
type_ = click.option(
    "--type", TYPE, type=str, metavar="str", help="Set the FPGA type (hx/lp)."
)

# -- Verbose.
VERBOSE = "verbose"
verbose = click.option(
    "-v",
    "--verbose",
    VERBOSE,
    is_flag=True,
    help="Show the entire output of the command.",
)

# -- Verbose place and route.
VERBOSE_PNR = "verbose_pnr"
verbose_pnr = click.option(
    "--verbose-pnr",
    VERBOSE_PNR,
    is_flag=True,
    help="Show the pnr output of the command.",
)

# -- Verbose Yosys.
VERBOSE_YOSYS = "verbose_yosys"
verbose_yosys = click.option(
    "--verbose-yosys",
    VERBOSE_YOSYS,
    is_flag=True,
    help="Show the yosys output of the command.",
)
