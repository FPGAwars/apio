# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO SIM command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
@click.command("sim", context_settings=util.context_settings())
@click.pass_context
@options.project_dir_option
@options.testbench
def cli(
    ctx,
    # Options
    project_dir: Path,
    testbench: str,
):
    """Simulate a single module."""

    # -- Create the scons object
    scons = SCons(project_dir)

    # -- Simulate the project with the given parameters
    exit_code = scons.sim({"testbench": testbench})

    # -- Done!
    ctx.exit(exit_code)
