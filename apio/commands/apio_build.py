# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio build' command"""

import sys
from pathlib import Path
import click
from apio.utils import cmd_util
from apio.managers.scons import SCons
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.common.proto.apio_pb2 import Verbosity

# ------------ apio build

# -- Text in the rich-text format of the python rich library.
APIO_BUILD_HELP = """
The command 'apio build' processes the project’s source files and generates \
a bitstream file, which can then be uploaded to your FPGA.

The 'apio build' command compiles all .v files (e.g., my_module.v) in the \
project directory, except those whose names end with '_tb' \
(e.g., my_module_tb.v) which are assumed to be testbenches.

[NOTE] The files are compiled in the order they are found in the sub \
directories of the source tree. This provides a simple way to control the \
compilation order by naming subdirectories for the desired build order.

Examples:[code]
  apio build       # Build
  apio build -v    # Build with verbose info[/code]
"""


@click.command(
    name="build",
    cls=cmd_util.ApioCommand,
    short_help="Synthesize the bitstream.",
    help=APIO_BUILD_HELP,
)
@click.pass_context
@options.project_dir_option
@options.verbose_option
@options.verbose_synth_option
@options.verbose_pnr_option
def cli(
    _: click.Context,
    # Options
    project_dir: Path,
    verbose: bool,
    verbose_synth: bool,
    verbose_pnr: bool,
):
    """Implements the apio build command. It invokes the toolchain
    to synthesize the source files into a bitstream file.
    """

    # The bitstream is generated from the source files (verilog)
    # by means of the scons tool
    # https://www.scons.org/documentation.html

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED,
        project_dir_arg=project_dir,
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Build the project with the given parameters
    exit_code = scons.build(
        Verbosity(all=verbose, synth=verbose_synth, pnr=verbose_pnr)
    )

    # -- Done!
    sys.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build
