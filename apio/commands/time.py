# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio' time' command"""

import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The command 'apio time' has been deprecated. Please use the command
'apio report' instead.
"""


# pylint: disable=duplicate-code
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "time",
    short_help="[Depreciated] Report design timing.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.verbose_yosys_option
@options.verbose_pnr_option
@options.top_module_option_gen(deprecated=False)
@options.board_option_gen(deprecated=False)
@options.fpga_option_gen(deprecated=False)
@options.size_option_gen(deprecated=False)
@options.type_option_gen(deprecated=False)
@options.pack_option_gen(deprecated=False)
def cli(
    _: click.core.Context,
    # Options
    project_dir: Path,
    verbose: bool,
    verbose_yosys: bool,
    verbose_pnr: bool,
    # Deprecated options
    top_module: str,
    board: str,
    fpga: str,
    size: str,
    type_: str,
    pack: str,
):
    """Analyze the design and report timing."""

    click.secho(
        "The 'apio time' command is deprecated. "
        "Please use the 'apio report' command instead.",
        fg="yellow",
    )

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=True)

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # Run scons
    exit_code = scons.time(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": type_,
            "pack": pack,
            "top-module": top_module,
            "verbose_all": verbose,
            "verbose_yosys": verbose_yosys,
            "verbose_pnr": verbose_pnr,
        }
    )

    # -- Done!
    sys.exit(exit_code)
