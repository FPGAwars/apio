# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO TEST command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "test"  # -- Comand name
PROJECT_DIR = "project_dir"  # -- Option
TESTBENCH = "testbench"  # -- Option


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-t",
    f"--{TESTBENCH}",
    type=str,
    metavar="testbench",
    help="Test only this testbench file.",
)
def cli(ctx, **kwargs):
    # def cli(ctx, project_dir, testbench):
    """Launch the verilog testbench testing."""

    # -- Extract the arguments
    project_dir = kwargs[PROJECT_DIR]
    testbench = kwargs[TESTBENCH]

    # -- Create the scons object
    scons = SCons(project_dir)

    exit_code = scons.test({"testbench": testbench})
    ctx.exit(exit_code)
