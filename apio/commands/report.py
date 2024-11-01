# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio' report' command"""

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
The report command reports the utilization and timing of the design.
It is useful to analyzer utilization bottle neck and to verify that
the design can run at a desired clock speed.
The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio report
  epio report --verbose

"""


# pylint: disable=duplicate-code
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "report",
    short_help="Report design utilization and timing.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.top_module_option_gen(deprecated=True)
@options.board_option_gen(deprecated=True)
@options.fpga_option_gen(deprecated=True)
@options.size_option_gen(deprecated=True)
@options.type_option_gen(deprecated=True)
@options.pack_option_gen(deprecated=True)
def cli(
    ctx: Context,
    # Options
    project_dir: Path,
    verbose: bool,
    top_module: str,
    board: str,
    fpga: str,
    size: str,
    type_: str,
    pack: str,
):
    """Analyze the design and report timing."""

    # -- Create the scons object
    resources = Resources(project_dir=project_dir)
    scons = SCons(resources)

    # Run scons
    exit_code = scons.report(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": type_,
            "pack": pack,
            "verbose": {
                "all": False,
                "yosys": False,
                "pnr": verbose,
            },
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)
