# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio lint' command"""
import sys
from pathlib import Path
import click
from apio.managers.scons import SCons
from apio.utils import util
from apio.utils import cmd_util
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.common.proto.apio_pb2 import LintParams


# ------- apio lint

all_option = click.option(
    "all_",  # Var name. Deconflicting from Python'g builtin 'all'.
    "-a",
    "--all",
    is_flag=True,
    help="Enable all warnings, including code style warnings.",
    cls=cmd_util.ApioOption,
)

nostyle_option = click.option(
    "nostyle",  # Var name
    "--nostyle",
    is_flag=True,
    help="Disable all style warnings.",
    cls=cmd_util.ApioOption,
)


nowarn_option = click.option(
    "nowarn",  # Var name
    "--nowarn",
    type=str,
    metavar="nowarn",
    help="Disable specific warning(s).",
    cls=cmd_util.ApioOption,
)

warn_option = click.option(
    "warn",  # Var name
    "--warn",
    type=str,
    metavar="warn",
    help="Enable specific warning(s).",
    cls=cmd_util.ApioOption,
)


# -- Text in the markdown format of the python rich library.
APIO_LINT_HELP = """
The command 'apio lint' scans the project's Verilog code and reports errors, \
inconsistencies, and style violations. The command uses the Verilator tool, \
which is included in the standard Apio installation.

Examples:[code]
  apio lint
  apio lint -t my_module
  apio lint --all[/code]
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    name="lint",
    cls=cmd_util.ApioCommand,
    short_help="Lint the verilog code.",
    help=APIO_LINT_HELP,
)
@click.pass_context
@nostyle_option
@nowarn_option
@warn_option
@all_option
@options.top_module_option_gen(
    help="Restrict linting to this module and its depedencies."
)
@options.project_dir_option
def cli(
    _: click.Context,
    # Options
    nostyle: bool,
    nowarn: str,
    warn: str,
    all_: bool,
    top_module: str,
    project_dir: Path,
):
    """Lint the verilog code."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_REQUIRED,
        project_dir_arg=project_dir,
    )

    # -- Create the scons manager.
    scons = SCons(apio_ctx)

    # -- Convert the comma seperated args values to python lists
    no_warns_list = util.split(nowarn, ",", strip=True, keep_empty=False)
    warns_list = util.split(warn, ",", strip=True, keep_empty=False)

    # -- Create the lint params
    lint_params = LintParams(
        top_module=top_module if top_module else None,
        verilator_all=all_,
        verilator_no_style=nostyle,
        verilator_no_warns=no_warns_list,
        verilator_warns=warns_list,
    )

    assert lint_params.IsInitialized(), lint_params

    # -- Lint the project with the given parameters
    exit_code = scons.lint(lint_params)
    sys.exit(exit_code)
