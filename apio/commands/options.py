# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Common apio command options"""

from pathlib import Path
import click
from apio import cmd_util


# The design is based on the idea here https://stackoverflow.com/a/77732441.
# It contains shared command line options in two forms, dynamic option
# which can be customized for specific use cases and fixed static options
# with fixed attributes. Options that are too specific to a single command
# not not listed here and defined instead in the command itself.
# Both type of options are listed in an alphabetical order.


# ----------------------------------
# -- Customizeable option generators
# ----------------------------------


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def all_option_gen(*, help: str):
    """Generate an --all option with given help text."""
    return click.option(
        "all_",  # Var name. Deconflicting from Python'g builtin 'all'.
        "-a",
        "--all",
        is_flag=True,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def force_option_gen(*, help: str):
    """Generate a --force option with given help text."""
    return click.option(
        "force",  # Var name
        "-f",
        "--force",
        is_flag=True,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def list_option_gen(*, help: str):
    """Generate a --list option with given help text."""
    return click.option(
        "list_",  # Var name. Deconflicting from python builtin 'list'.
        "-l",
        "--list",
        is_flag=True,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def board_option_gen(
    *, deprecated: bool = False, required=False, help: str = "Set the board."
):
    """Generate a --board option with given help text."""
    return click.option(
        "board",  # Var name.
        "-b",
        "--board",
        type=str,
        required=required,
        metavar="str",
        deprecated=deprecated,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def top_module_option_gen(
    *,
    deprecated: bool = False,
    help: str = "Set the top level module name.",
):
    """Generate a --top-module option with given help text."""
    return click.option(
        "top_module",  # Var name.
        "-t",
        "--top-module",
        type=str,
        metavar="name",
        deprecated=deprecated,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def fpga_option_gen(
    *,
    deprecated: bool = False,
    help: str = "Set the FPGA.",
):
    """Generate a --fpga option with given help text."""
    return click.option(
        "fpga",  # Var name.
        "--fpga",
        type=str,
        metavar="str",
        deprecated=deprecated,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def size_option_gen(
    *,
    deprecated: bool = False,
    help: str = "Set the FPGA size (1k/8k).",
):
    """Generate a --size option with given help text."""
    return click.option(
        "size",  # Var name
        "--size",
        type=str,
        metavar="str",
        deprecated=deprecated,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def type_option_gen(
    *,
    deprecated: bool = False,
    help: str = "Set the FPGA type (hx/lp).",
):
    """Generate a --type option with given help text."""
    return click.option(
        "type_",  # Var name. Deconflicting from Python's builtin 'type'.
        "--type",
        type=str,
        metavar="str",
        deprecated=deprecated,
        help=help,
        cls=cmd_util.ApioOption,
    )


# W0622: Redefining built-in 'help'
# pylint: disable=W0622
def pack_option_gen(
    *,
    deprecated: bool = False,
    help: str = "Set the FPGA package.",
):
    """Generate a --pack option with given help text."""
    return click.option(
        "pack",  # Var name
        "--pack",
        type=str,
        metavar="str",
        deprecated=deprecated,
        help=help,
        cls=cmd_util.ApioOption,
    )


# ---------------------------
# -- Static options
# ---------------------------


ftdi_id = click.option(
    "ftdi_id",  # Var name.
    "--ftdi-id",
    type=str,
    metavar="ftdi-id",
    help="Set the FTDI id.",
)


# -- NOTE: Not using -p to avoid conflict with --project-dir.
platform_option = click.option(
    "platform",  # Var name.
    "--platform",
    type=str,
    help=("(Advanced, for developers) Platform id override."),
    cls=cmd_util.ApioOption,
)


project_dir_option = click.option(
    "project_dir",  # Var name.
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the root directory for the project.",
    cls=cmd_util.ApioOption,
)


sayno = click.option(
    "sayno",  # Var name.
    "-n",
    "--sayno",
    is_flag=True,
    help="Automatically answer NO to all the questions.",
    cls=cmd_util.ApioOption,
)

sayyes = click.option(
    "sayyes",  # Var name.
    "-y",
    "--sayyes",
    is_flag=True,
    help="Automatically answer YES to all the questions.",
    cls=cmd_util.ApioOption,
)

serial_port_option = click.option(
    "serial_port",  # Var name.
    "--serial-port",
    type=str,
    metavar="serial-port",
    help="Set the serial port.",
    cls=cmd_util.ApioOption,
)


verbose_option = click.option(
    "verbose",  # Var name.
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed output.",
    cls=cmd_util.ApioOption,
)


verbose_pnr_option = click.option(
    "verbose_pnr",  # Var name.
    "--verbose-pnr",
    is_flag=True,
    help="Show detailed pnr output.",
    cls=cmd_util.ApioOption,
)


verbose_yosys_option = click.option(
    "verbose_yosys",  # Var name.
    "--verbose-yosys",
    is_flag=True,
    help="Show detailed yosys output.",
    cls=cmd_util.ApioOption,
)
