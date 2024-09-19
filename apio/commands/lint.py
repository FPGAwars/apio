# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO LINT command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
nostyle_option = click.option(
    "nostyle",  # Var name
    "--nostyle",
    is_flag=True,
    help="Disable all style warnings.",
)


nowarn_option = click.option(
    "nowarn",  # Var name
    "--nowarn",
    type=str,
    metavar="nowarn",
    help="Disable specific warning(s).",
)

warn_option = click.option(
    "warn",  # Var name
    "--warn",
    type=str,
    metavar="warn",
    help="Enable specific warning(s).",
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
of the project that that contains the apio.ini file.

\b
Examples:
  apio lint

[Note] The flags marked with (deprecated) are not recomanded for use.
"""


# R0913: Too many arguments (7/5)
# pylint: disable=R0913
@click.command(
    "lint",
    short_help="Lint the verilog code.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@options.all_option_gen(
    help="Enable all warnings, including code style warnings."
)
@nostyle_option
@nowarn_option
@warn_option
@options.project_dir_option
@options.top_module_option_gen()
def cli(
    ctx: Context,
    # Options
    all_: bool,
    top_module: str,
    nostyle: bool,
    nowarn: str,
    warn: str,
    project_dir: Path,
):
    """Lint the verilog code."""

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Lint the project with the given parameters
    exit_code = scons.lint(
        {
            "all": all_,
            "top": top_module,
            "nostyle": nostyle,
            "nowarn": nowarn,
            "warn": warn,
        }
    )
    ctx.exit(exit_code)
