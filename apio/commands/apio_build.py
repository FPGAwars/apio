# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio build' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.utils import cmd_util
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.common.proto.apio_pb2 import Verbosity
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)

# ------------ apio build

# -- Text in the rich-text format of the python rich library.
APIO_BUILD_HELP = """
The command 'apio build' processes the project’s synthesis source files and \
generates a bitstream file, which can then be uploaded to your FPGA.

Examples:[code]
  apio build                   # Typical usage
  apio build -e debug          # Set the apio.ini env.
  apio build -v                # Verbose info (all)
  apio build --verbose-synth   # Verbose synthesis info
  apio build --verbose-pnr     # Verbose place and route info[/code]

NOTES:
* The files are sorted in a deterministic lexicographic order.
* You can specify the name of the top module in apio.ini.
* The build command ignores testbench files (*_tb.v, and *_tb.sv).
* It is unnecessary to run 'apio build' before 'apio upload'.
* To force a rebuild from scratch use the command 'apio clean' first.
"""


@click.command(
    name="build",
    cls=cmd_util.ApioCommand,
    short_help="Synthesize the bitstream.",
    help=APIO_BUILD_HELP,
)
@click.pass_context
@options.env_option_gen()
@options.project_dir_option
@options.verbose_option
@options.verbose_synth_option
@options.verbose_pnr_option
def cli(
    _: click.Context,
    # Options
    env: Optional[str],
    project_dir: Optional[Path],
    verbose: bool,
    verbose_synth: bool,
    verbose_pnr: bool,
):
    """Implements the apio build command. It invokes the toolchain
    to synthesize the source files into a bitstream file.
    """

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.PROJECT_REQUIRED,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        env_arg=env,
    )

    # -- Create the scons manager.
    scons = SConsManager(apio_ctx)

    # -- Build the project with the given parameters
    exit_code = scons.build(
        Verbosity(all=verbose, synth=verbose_synth, pnr=verbose_pnr)
    )

    # -- Done!
    sys.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build
