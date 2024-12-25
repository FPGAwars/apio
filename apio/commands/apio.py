"""Apio top level click command."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2


import click
from apio.cmd_util import ApioSubgroup, ApioGroup

# -- Import sub commands.
from apio.commands import (
    apio_boards,
    apio_build,
    apio_clean,
    apio_create,
    apio_drivers,
    apio_examples,
    apio_format,
    apio_fpgas,
    apio_graph,
    apio_lint,
    apio_packages,
    apio_raw,
    apio_report,
    apio_sim,
    apio_system,
    apio_test,
    apio_upgrade,
    apio_upload,
)


# -- The subcommands of this command, grouped by category.
SUBGROUPS = [
    ApioSubgroup(
        "Build commands",
        [
            apio_build.cli,
            apio_upload.cli,
            apio_clean.cli,
        ],
    ),
    ApioSubgroup(
        "Verification commands",
        [
            apio_lint.cli,
            apio_format.cli,
            apio_sim.cli,
            apio_test.cli,
            apio_report.cli,
            apio_graph.cli,
        ],
    ),
    ApioSubgroup(
        "Setup commands",
        [
            apio_create.cli,
            apio_packages.cli,
            apio_drivers.cli,
        ],
    ),
    ApioSubgroup(
        "Utility commands",
        [
            apio_boards.cli,
            apio_fpgas.cli,
            apio_examples.cli,
            apio_system.cli,
            apio_raw.cli,
            apio_upgrade.cli,
        ],
    ),
]


def context_settings():
    """Return a common Click command settings that adds
    the alias -h to --help. This applies also to all the sub
    commands such as apio build.
    """
    # Per https://click.palletsprojects.com/en/8.1.x/documentation/
    #     #help-parameter-customization
    return {"help_option_names": ["-h", "--help"]}


# ---------------------------
# -- Top click command node.
# ---------------------------

HELP = """
Work with FPGAs with ease.

Apio is a user friendly command-line
suite that supports all the aspect of FPGA firmware developement
from linting, building and simulating to unit testing, to progreamming
the FPGA board.

Apio commands are typically invoked in the root directory of the FPGA
project where the project configuration file apio.ini and the project
source files are stored. For help on specific commands use the -h
flag (e.g. 'apio build -h').

For more information on the apio project see
https://github.com/FPGAwars/apio/wiki/Apio
"""


@click.group(
    name="apio",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    help=HELP,
    context_settings=context_settings(),
)
@click.version_option()
def cli():
    """The top level command group of apio commands"""

    # pass
