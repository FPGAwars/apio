# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO GRAPH command"""

from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


# ---------------------------
# -- COMMAND
# ---------------------------
@click.command("graph", context_settings=util.context_settings())
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.top_module_option_gen()
def cli(
    ctx,
    # Options
    project_dir: Path,
    verbose: bool,
    top_module: str,
):
    """Generate a a visual graph of the verilog code."""

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Graph the project with the given parameters
    exit_code = scons.graph(
        {
            "verbose": {"all": verbose, "yosys": False, "pnr": False},
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
