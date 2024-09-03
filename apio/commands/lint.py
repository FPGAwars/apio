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
# R0913: Too many arguments (7/5)
# pylint: disable=R0913
@click.command("lint", context_settings=util.context_settings())
@click.pass_context
@options.all_option_gen(
    help="Enable all warnings, including code style warnings."
)
@options.top_module_option_gen()
@nostyle_option
@nowarn_option
@warn_option
@options.project_dir_option
def cli(
    ctx,
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
