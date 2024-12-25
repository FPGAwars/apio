"""Apio top level click command."""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2


import click

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

# -- Subcommands, grouped by categories.
SUBCOMMANDS = {
    "Build commands": [
        apio_build.cli,
        apio_upload.cli,
        apio_clean.cli,
    ],
    "Verification commands": [
        apio_lint.cli,
        apio_format.cli,
        apio_sim.cli,
        apio_test.cli,
        apio_report.cli,
        apio_graph.cli,
    ],
    "Setup commands": [
        apio_create.cli,
        apio_packages.cli,
        apio_drivers.cli,
    ],
    "Utility commands": [
        apio_boards.cli,
        apio_fpgas.cli,
        apio_examples.cli,
        apio_system.cli,
        apio_raw.cli,
        apio_upgrade.cli,
    ],
}


class ApioGroup(click.Group):
    """A customized click.Group class that allow to group subcommand by
    categories."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # @override
    def get_help(self, ctx: click.Context) -> str:
        """Formats the help into a string and returns it. We override the
        base class method to list the subcommands by categories.
        """

        # -- Get the default help text for this command.
        original_help = super().get_help(ctx)

        # -- The auto generated click help lines (apio --help)
        help_lines = original_help.split("\n")

        # -- Extract the header of the text help. We will generate ourselves
        # -- and append the command list.
        index = help_lines.index("Commands:")
        result_lines = help_lines[:index]

        # -- Get a flat list of all command names.
        cmd_names = [
            cmd.name for group in SUBCOMMANDS.values() for cmd in group
        ]

        # -- Find the length of the longerst name.
        max_name_len = max(len(name) for name in cmd_names)

        # -- Generate the subcommands short help, grouped by command category.
        for group_title, subcommands in SUBCOMMANDS.items():
            result_lines.append(f"{group_title}:")
            for cmd in subcommands:
                # -- We pad for field width and then apply color.
                styled_name = click.style(
                    f"{cmd.name:{max_name_len}}", fg="magenta"
                )
                result_lines.append(
                    f"  {ctx.command_path} {styled_name}  {cmd.short_help}"
                )
            result_lines.append("")

        return "\n".join(result_lines)


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
    help=HELP,
    context_settings=context_settings(),
)
@click.version_option()
def cli():
    """This function is invoked before each subcommand but there
    is nothing to do here."""

    # Nothing to do here.


# -- Register the sub commands.
for group in SUBCOMMANDS.values():
    for subcommand in group:
        cli.add_command(subcommand)
