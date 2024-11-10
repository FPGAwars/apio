# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio' time' command"""

from pathlib import Path
import click
from click.core import Context
from apio.managers.scons import SCons
from apio import cmd_util
from apio.commands import options
from apio.resources import Resources


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The time command has been deprecated. Please use the 'apio report' command
instead.
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
    ctx: Context,
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
        "The apio 'time' command is deprecated. "
        "Please use the 'report' command instead.",
        fg="yellow",
    )

    # -- Create the scons object
    resources = Resources(project_dir=project_dir, project_scope=True)
    scons = SCons(resources)

    # Run scons
    exit_code = scons.time(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": type_,
            "pack": pack,
            "verbose": {
                "all": verbose,
                "yosys": verbose_yosys,
                "pnr": verbose_pnr,
            },
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
