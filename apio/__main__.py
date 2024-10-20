"""APIO ENTRY POINT"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

# --------------------------------------------
# -- Apio ENTRY POINT!!!
# --------------------------------------------

import string
import re
from typing import List
from click.core import Context
import click
from apio import util

# -- Maps group title to command names. Controls how the 'apio -h' help
# -- information is printed. Should include all commands and without
# -- duplicates.
COMMAND_GROUPS = {
    "Build commands": [
        "build",
        "upload",
        "clean",
    ],
    "Verification commands": [
        "verify",
        "lint",
        "sim",
        "test",
        "time",
        "report",
        "graph",
    ],
    "Setup commands": [
        "create",
        "modify",
        "drivers",
        "install",
        "uninstall",
    ],
    "Utility commands": [
        "boards",
        "examples",
        "raw",
        "system",
        "upgrade",
    ],
}


def select_commands_help(
    command_lines: List[str], command_names: List[str]
) -> List[str]:
    """
    Given a list of click generated help lines for all the commands,
    return a subset that includes only the commands in command_names.
    The result order is by command_names.
    - INPUTS:
      * command_lines: Click generated help lines for all the commands.
      * commands: A list of commands names to select.
    """

    result = []
    # We perform a search that preserves the order in command_names.
    for command_name in command_names:
        matching_line = None
        for command_line in command_lines:
            # Extract command name. This is the first word.
            # E.g.: "  build      Synthesize the bitstream."
            name = re.findall(r"^\s*(\S+)\s+.*$", command_line)[0]
            if name == command_name:
                matching_line = command_line
                break
        if matching_line is None:
            # A missing name is a programming error so ok to crash.
            raise ValueError(f"Missing help for command '{command_name}'")
        result.append(matching_line)

    # Sanity check.
    assert len(result) == len(command_names)

    # -- Return the list of comands with their descriptions
    return result


def reformat_apio_help(original_help: str) -> str:
    """Reformat the apio top level help text such that the commands are grouped
    by category.
    """

    # -- No command typed: show help
    # if ctx.invoked_subcommand is None:
    # -- The auto generated click help lines (apio --help)
    help_lines = original_help.split("\n")

    # -- Split the help lines into header and command groups.
    # -- We later split the command lines into command groups.
    index = help_lines.index("Commands:")
    header_lines = help_lines[:index]
    index += 1  # Skip the Commands: line.
    command_lines = help_lines[index:]

    # -- Header
    result = []
    result.extend(header_lines)

    # -- Print the help of the command groups while verifying that there
    # -- are no missing or duplicate commands.
    reported_commands = set()
    for group_title, command_names in COMMAND_GROUPS.items():
        # -- Assert no duplicates inter and intra groups.
        assert len(command_names) == len(set(command_names))
        assert reported_commands.isdisjoint(command_names)
        reported_commands.update(command_names)
        # -- Select the help lines of the commands in this group.
        group_help = select_commands_help(command_lines, command_names)
        # -- Append the group title and command lines.
        result.append(f"{group_title}:")
        result.extend(group_help)
        result.append("")

    # -- If this assertion fails, for a missing command in the groups
    # -- definitions.
    assert len(command_lines) == len(
        reported_commands
    ), f"{command_lines=}, {len(reported_commands)=}"

    return "\n".join(result)


# -----------------------------------------------------------------------------
# -- Main Click Class
# -- It is extended for including methods for getting and listing the commands
# -----------------------------------------------------------------------------
class ApioCLI(click.MultiCommand):
    """DOC:TODO"""

    def __init__(self, *args, **kwargs):

        # -- Get the full path to the commands folder
        # -- Ex. /home/obijuan/Develop/(...)/apio/commands
        # -- Every apio command (Ex. apio build, apio upload...) is a
        # -- separate .py file located in the commands folder
        self.commands_folder = util.get_path_in_apio_package("commands")

        self._cls = [None]
        super().__init__(*args, **kwargs)

    # -- Return  a list of all the available commands
    # @override
    def list_commands(self, ctx):
        # -- All the python files inside the apio/commands folder are commands,
        # -- except __init__.py
        # -- Create the list
        cmd_list = [
            element.stem  # -- Name without path and extension
            for element in self.commands_folder.iterdir()
            if (
                element.is_file()
                and element.suffix == ".py"
                and element.stem != "__init__"
            )
        ]

        cmd_list.sort()
        return cmd_list

    # -- Return the code function (cli) of the command name
    # -- This cli function is called whenever the name command
    # -- is issued
    # -- INPUT:
    # --   * cmd_name: Apio command name
    # @override
    def get_command(self, ctx, cmd_name: string):
        nnss = {}

        # -- Get the python filename asociated with the give command
        # -- Ex. "system" --> "/home/obijuan/.../apio/commands/system.py"
        filename = self.commands_folder / f"{cmd_name}.py"

        # -- Check if the file exists
        if filename.exists():
            # -- Open the python file
            with filename.open(encoding="utf8") as file:
                # -- Compile it!
                code = compile(file.read(), filename, "exec")

                # -- Get the function!
                # pylint: disable=W0123
                eval(code, nnss, nnss)

        # -- Return the function needed for executing the command
        return nnss.get("cli")

    # @override
    def get_help(self, ctx: Context) -> str:
        """Formats the help into a string and returns it.

        Calls :meth:`format_help` internally.
        """
        return reformat_apio_help(super().get_help(ctx))


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


@click.command(
    cls=ApioCLI,
    help=HELP,
    invoke_without_command=True,
    context_settings=context_settings(),
)
@click.pass_context
@click.version_option()
def cli(ctx: Context):
    """This function is executed when apio is invoked without
    any parameter. It prints the high level usage text of Apio.
    """

    # -- If no command was typed show top help. Equivalent to 'apio -h'.
    if ctx.invoked_subcommand is None:
        click.secho(ctx.get_help())

    # -- If there is a command, it is executed when this function is finished
    # -- Debug: print the command invoked
    # print(f"{ctx.invoked_subcommand}")
