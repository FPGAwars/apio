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

# ------------------
# -- CONSTANTS
# ------------------
CMD = "lint"  # -- Comand name
ALL = "all"  # -- Option
TOP_MODULE = "top_module"  # -- Option
NOSTYLE = "nostyle"  # -- Option
NOWARN = "nowarn"  # -- Option
WARN = "warn"  # -- Option
PROJECT_DIR = "project_dir"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-a",
    f"--{ALL}",
    is_flag=True,
    help="Enable all warnings, including code style warnings.",
)
@click.option(
    "-t", "--top-module", type=str, metavar="str", help="Set top module."
)
@click.option(f"--{NOSTYLE}", is_flag=True, help="Disable all style warnings.")
@click.option(
    f"--{NOWARN}",
    type=str,
    metavar="nowarn",
    help="Disable specific warning(s).",
)
@click.option(
    f"--{WARN}", type=str, metavar="warn", help="Enable specific warning(s)."
)
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the target directory for the project.",
)
def cli(ctx, **kwargs):
    # def cli(ctx, all, top, nostyle, nowarn, warn, project_dir):
    """Lint the verilog code."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    _all = kwargs[ALL]
    top_module = kwargs[TOP_MODULE]
    nostyle = kwargs[NOSTYLE]
    nowarn = kwargs[NOWARN]
    warn = kwargs[WARN]

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Lint the project with the given parameters
    exit_code = scons.lint(
        {
            "all": _all,
            "top": top_module,
            "nostyle": nostyle,
            "nowarn": nowarn,
            "warn": warn,
        }
    )
    ctx.exit(exit_code)
