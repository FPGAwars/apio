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
import click

from apio import util


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
        self.commands_folder = util.get_apio_full_path("commands")

        self._cls = [None]
        super().__init__(*args, **kwargs)

    # -- Return  a list of all the available commands
    def list_commands(self, ctx):
        # -- All the python files inside the apio/commands folder are commands,
        # -- except __init__.py
        # -- Create the list
        cmd_list = [
            element.stem  # -- Name without path and extension
            for element in self.commands_folder.iterdir()
            if element.is_file()
            and element.suffix == ".py"
            and element.stem != "__init__"
        ]

        cmd_list.sort()
        return cmd_list

    # -- Return the code function (cli) of the command name
    # -- This cli function is called whenever the name command
    # -- is issued
    # -- INPUT:
    # --   * cmd_name: Apio command name
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


def select_commands_help(command_lines, command_names):
    """
    Given a list of click generated help lines for all the commands,
    return a subset that includes only the commands in command_names.
    The result order is by command_lines which happens to be alphabetical.
    - INPUTS:
      * command_lines: Click generated help lines for all the commands.
      * commands: A list of commands names to select.
    """

    result = []
    for command_line in command_lines:
        # Extract command name. This is the first word.
        # E.g.: "  build      Synthesize the bitstream."
        command_name = re.findall(r"^\s*(\S+)\s+.*$", command_line)[0]
        if command_name in command_names:
            result.append(command_line)

    # -- Return the list of comands with their descriptions
    return result


# ---------------------------
# -- Top click command node.
# ---------------------------
@click.command(
    cls=ApioCLI,
    help=(
        "Work with FPGAs with ease. "
        "For more information see https://github.com/FPGAwars/apio/wiki/Apio"
    ),
    invoke_without_command=True,
    context_settings=util.context_settings(),
)
@click.pass_context
@click.version_option()
def cli(ctx):
    """This function is executed when apio is invoked without
    any parameter. It prints the high level usage text of Apio.
    """

    # -- No command typed: show help
    if ctx.invoked_subcommand is None:
        # -- The auto generated click help lines (apio --help)
        help_lines = ctx.get_help().split("\n")

        # -- Split the help lines into header and command groups.
        # -- We later split the command lines into command groups.
        index = help_lines.index("Commands:")
        header_lines = help_lines[:index]
        index += 1  # Skip the Commands: line.
        command_lines = help_lines[index:]

        # -- Select project commands:
        project_help = select_commands_help(
            command_lines,
            [
                "build",
                "clean",
                "sim",
                "test",
                "verify",
                "lint",
                "time",
                "upload",
                "graph",
            ],
        )
        # -- Select setup commands
        setup_help = select_commands_help(
            command_lines, ["drivers", "init", "install", "uninstall"]
        )

        # -- Select utility commands
        util_help = select_commands_help(
            command_lines,
            ["boards", "config", "examples", "raw", "system", "upgrade"],
        )

        # -- Sanity check, in case we mispelled or ommited a command name.
        num_selected = len(project_help) + len(setup_help) + len(util_help)
        assert len(command_lines) == num_selected

        # -- Print header
        click.secho("\n".join(header_lines))

        # -- Print project commands:
        click.secho("Project commands:")
        click.secho("\n".join(project_help))
        click.secho()

        # -- Print Setup commands:
        click.secho("Setup commands:")
        click.secho("\n".join(setup_help))
        click.secho()

        # -- Print utility commands:
        click.secho("Utility commands:")
        click.secho("\n".join(util_help))
        click.secho()

    # -- If there is a command, it is executed when this function is finished
    # -- Debug: print the command invoked
    # print(f"{ctx.invoked_subcommand}")
