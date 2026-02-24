# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio lint' command"""
import sys
from typing import Optional
from pathlib import Path
import click
from apio.managers.scons_manager import SConsManager
from apio.utils import cmd_util
from apio.commands import options
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.common.proto.apio_pb2 import LintParams


# ------- apio lint

nosynth_option = click.option(
    "nosynth",  # Var name
    "--nosynth",
    is_flag=True,
    help="Do not define the SYNTHESIS macro.",
    cls=cmd_util.ApioOption,
)

novlt_option = click.option(
    "novlt",  # Var name
    "--novlt",
    is_flag=True,
    help="Disable warning suppression .vlt file.",
    cls=cmd_util.ApioOption,
)


# -- Text in the rich-text format of the python rich library.
APIO_LINT_HELP = """
The command 'apio lint' scans the project's source files and reports errors, \
inconsistencies, and style violations. The command uses the Verilator tool, \
which is included with the standard Apio installation.

If specified files are not specified, the top module of the project and \
its dependencies are linted.

Examples:[code]
  apio lint
  apio lint -t my_module
  apio lint file1.v file2.v
  apio lint --all
  apio lint --nosynth
  apio lint --novlt[/code]

By default, 'apio lint' injects the 'SYNTHESIS' macro to lint the \
synthesizable portion of the design. To lint code that is hidden by \
'SYNTHESIS', use the '--nosynth' option.

To customize the behavior of the 'verilator' linter, add the option \
'verilator-extra-option' in the project file 'apio.ini' with the extra \
options you would like to use.
"""


@click.command(
    name="lint",
    cls=cmd_util.ApioCommand,
    short_help="Lint the source code.",
    help=APIO_LINT_HELP,
)
@click.pass_context
@click.argument("files", nargs=-1, required=False)
@nosynth_option
@novlt_option
@options.top_module_option_gen(
    short_help="Restrict linting to this module and its dependencies."
)
@options.env_option_gen()
@options.project_dir_option
def cli(
    _: click.Context,
    *,
    # Args
    files,
    # Options
    nosynth: bool,
    novlt: bool,
    top_module: str,
    env: Optional[str],
    project_dir: Optional[Path],
):
    """Lint the source code."""

    # pylint: disable=too-many-arguments

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

    # -- Create the lint params
    lint_params = LintParams(
        top_module=top_module if top_module else None,
        nosynth=nosynth,
        novlt=novlt,
        file_names=files,
    )

    assert lint_params.IsInitialized(), lint_params

    # -- Lint the project with the given parameters
    exit_code = scons.lint(lint_params)
    sys.exit(exit_code)
