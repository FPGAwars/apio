# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio lint' command"""
import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
nostyle_option = click.option(
    "nostyle",  # Var name
    "--nostyle",
    is_flag=True,
    help="Disable all style warnings.",
    cls=cmd_util.ApioOption,
)


nowarn_option = click.option(
    "nowarn",  # Var name
    "--nowarn",
    type=str,
    metavar="nowarn",
    help="Disable specific warning(s).",
    cls=cmd_util.ApioOption,
)

warn_option = click.option(
    "warn",  # Var name
    "--warn",
    type=str,
    metavar="warn",
    help="Enable specific warning(s).",
    cls=cmd_util.ApioOption,
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The lint command scans the project's
verilog code and flags errors, inconsistencies, and style violations,
and is a useful tool for improving the code quality. The command uses
the verilator tool which is installed as park of the apio installation.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio lint
  apio lint -t my_module
  apio lint --all
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "lint",
    short_help="Lint the verilog code.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.top_module_option_gen(
    help="Restrict linting to this module and its depedencies."
)
@options.all_option_gen(
    help="Enable all warnings, including code style warnings."
)
@nostyle_option
@nowarn_option
@warn_option
@options.project_dir_option
def cli(
    _: click.core.Context,
    # Options
    top_module: str,
    all_: bool,
    nostyle: bool,
    nowarn: str,
    warn: str,
    project_dir: Path,
):
    """Lint the verilog code."""

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=True)

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Lint the project with the given parameters
    exit_code = scons.lint(
        {
            "all": all_,
            "top-module": top_module,
            "nostyle": nostyle,
            "nowarn": nowarn,
            "warn": warn,
        }
    )
    sys.exit(exit_code)
