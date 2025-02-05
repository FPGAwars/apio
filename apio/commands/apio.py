"""Apio top level click command."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2


import click
from apio.utils.cmd_util import ApioSubgroup, ApioGroup

# -- Import sub commands.
from apio.commands import (
    apio_api,
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
    apio_preferences,
    apio_raw,
    apio_report,
    apio_sim,
    apio_system,
    apio_test,
    apio_upgrade,
    apio_upload,
    apio_docs,
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
            apio_preferences.cli,
            apio_packages.cli,
            apio_drivers.cli,
        ],
    ),
    ApioSubgroup(
        "Utility commands",
        [
            apio_docs.cli,
            apio_boards.cli,
            apio_fpgas.cli,
            apio_examples.cli,
            apio_system.cli,
            apio_raw.cli,
            apio_api.cli,
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

# -- Text in the markdown format of the python rich library.
APIO_HELP = """
[b]WORK WITH FPGAs WITH EASE.[/b]

Apio is an easy to use and open-source command-line suite designed to \
streamline FPGA programming. It supports a wide range of tasks, including \
linting, building, simulation, unit testing, and programming FPGA boards.

An Apio project consists of a directory containing a configuration file \
named 'apio.ini', along with FPGA source files, testbenches, and pin \
definition files.

Apio commands are intuitive and perform their intended functionalities right \
out of the box. For example, the command apio upload automatically compiles \
the design in the current directory and uploads it to the FPGA board.

For detailed information about any Apio command, append the -h flag to view \
its help text. For example:

[code]apio build -h
apio drivers ftdi install -h[/code]

For more information about the Apio project, visit the official Apio Wiki \
https://github.com/FPGAwars/apio/wiki/Apio
"""


@click.group(
    name="apio",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    help=APIO_HELP,
    short_help="Work with FPGAs with ease",
    context_settings=context_settings(),
)
@click.version_option()
def cli():
    """The top level command group of apio commands"""

    # pass
