# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio' report' command"""

import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons_manager import SConsManager
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.common.proto.apio_pb2 import Verbosity, ReportParams
from apio.utils import cmd_util

# ---------- apio report

# -- Text in the rich-text format of the python rich library.
APIO_REPORT_HELP = """
The command 'apio report' provides information on the utilization and timing \
of the design. It is useful for analyzing utilization bottlenecks and \
verifying that the design can operate at the desired clock speed.

By default, the command reports only the used resources. To also include \
unused resources, use the '--all' option. The '--verbose' option prints \
additional information and implies '--all'.

Examples:[code]
  apio report            # Print report.
  apio report --all      # Report also unused resources.
  apio report --verbose  # Print extra information.[/code]
"""


@click.command(
    name="report",
    cls=cmd_util.ApioCommand,
    short_help="Report design utilization and timing.",
    help=APIO_REPORT_HELP,
)
@click.pass_context
@options.all_option_gen(short_help="Show also unused resources.")
@options.env_option_gen()
@options.project_dir_option
@options.verbose_option
def cli(
    _: click.Context,
    *,
    # Options
    all_: bool,
    env: Optional[str],
    project_dir: Optional[Path],
    verbose: bool,
):
    """Analyze the design and report timing."""

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

    # Run scons with the report target.
    exit_code = scons.report(
        report_params=ReportParams(report_all=(all_ or verbose)),
        verbosity=Verbosity(pnr=verbose),
    )

    # -- Done!
    sys.exit(exit_code)
