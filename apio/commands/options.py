# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Common apio command options"""

from pathlib import Path
import click
from apio.utils import cmd_util


# The design is based on the idea here https://stackoverflow.com/a/77732441.
# It contains shared command line options in two forms, dynamic option
# which can be customized for specific use cases and fixed static options
# with fixed attributes. Options that are too specific to a single command
# not not listed here and defined instead in the command itself.
# Both type of options are listed in an alphabetical order.


# ----------------------------------
# -- Customizable option generators
# ----------------------------------


def env_option_gen(*, short_help: str = "Set the apio.ini env."):
    """Generate an --env option with given help text."""

    return click.option(
        "env",  # Var name.
        "-e",
        "--env",
        type=str,
        default=None,
        metavar="name",
        help=short_help,
        cls=cmd_util.ApioOption,
    )


def all_option_gen(*, short_help: str):
    """Generate an --all option with given help text."""

    return click.option(
        "all_",  # Var name. Deconflicting from Python'g builtin 'all'.
        "-a",
        "--all",
        is_flag=True,
        help=short_help,
        cls=cmd_util.ApioOption,
    )


def force_option_gen(*, short_help: str):
    """Generate a --force option with given help text."""

    return click.option(
        "force",  # Var name
        "-f",
        "--force",
        is_flag=True,
        help=short_help,
        cls=cmd_util.ApioOption,
    )


def list_option_gen(*, short_help: str):
    """Generate a --list option with given help text."""

    return click.option(
        "list_",  # Var name. Deconflicting from python builtin 'list'.
        "-l",
        "--list",
        is_flag=True,
        help=short_help,
        cls=cmd_util.ApioOption,
    )


def top_module_option_gen(
    *,
    short_help: str = "Set the top level module name.",
):
    """Generate a --top-module option with given help text."""

    return click.option(
        "top_module",  # Var name.
        "-t",
        "--top-module",
        type=str,
        metavar="name",
        # deprecated=deprecated,
        help=short_help,
        cls=cmd_util.ApioOption,
    )


def dst_option_gen(*, short_help: str):
    """Generate a --dst option with given help text."""

    dst_option = click.option(
        "dst",  # Var name.
        "-d",
        "--dst",
        type=Path,
        metavar="path",
        help=short_help,
        cls=cmd_util.ApioOption,
    )

    return dst_option


# ---------------------------
# -- Static options
# ---------------------------

docs_format_option = click.option(
    "docs",  # Var name.
    "-d",
    "--docs",
    is_flag=True,
    help="Format for Apio Docs.",
    cls=cmd_util.ApioOption,
)

project_dir_option = click.option(
    "project_dir",  # Var name.
    "-p",
    "--project-dir",
    type=Path,
    metavar="path",
    help="Set the root directory for the project.",
    cls=cmd_util.ApioOption,
)


verbose_option = click.option(
    "verbose",  # Var name.
    "-v",
    "--verbose",
    is_flag=True,
    help="Show detailed output.",
    cls=cmd_util.ApioOption,
)


verbose_pnr_option = click.option(
    "verbose_pnr",  # Var name.
    "--verbose-pnr",
    is_flag=True,
    help="Show detailed pnr stage output.",
    cls=cmd_util.ApioOption,
)


verbose_synth_option = click.option(
    "verbose_synth",  # Var name.
    "--verbose-synth",
    is_flag=True,
    help="Show detailed synth stage output.",
    cls=cmd_util.ApioOption,
)
