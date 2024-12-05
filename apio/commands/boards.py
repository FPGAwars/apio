# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio boards' command"""

import sys
from pathlib import Path
import click
from apio.apio_context import ApioContext
from apio import cmd_util, util
from apio.commands import options


# R0914: Too many local variables (17/15)
# pylint: disable=R0914
def list_boards(apio_ctx: ApioContext):
    """Prints all the available board definitions."""
    # Get terminal configuration. It will help us to adapt the format
    # to a terminal vs a pipe.
    config: util.TerminalConfig = util.get_terminal_config()

    # -- Table title
    title = click.style("Board", fg="cyan") + " (FPGA, Arch, Type, Size, Pack)"

    # -- Print the table header for terminal mode.
    if config.terminal_mode():
        title = (
            click.style("Board", fg="cyan") + " (FPGA, Arch, Type, Size, Pack)"
        )
        # -- Horizontal line across the terminal.
        seperator_line = "─" * config.terminal_width
        click.secho(seperator_line)
        click.secho(title)
        click.secho(seperator_line)

    # -- Sort boards names by case insentive alphabetical order.
    board_names = list(apio_ctx.boards.keys())
    board_names.sort(key=lambda x: x.lower())

    # -- For a pipe, determine the max example name length.
    max_board_name_len = max(len(x) for x in board_names)

    # -- Print all the boards!
    for board in board_names:

        # -- Generate the report for a terminal. Color and multi lines
        # -- are ok.

        # -- Get board FPGA long name
        fpga = apio_ctx.boards[board]["fpga"]

        # -- Get information about the FPGA
        arch = apio_ctx.fpgas[fpga]["arch"]
        type_ = apio_ctx.fpgas[fpga]["type"]
        size = apio_ctx.fpgas[fpga]["size"]
        pack = apio_ctx.fpgas[fpga]["pack"]

        # -- Print the item with information
        # -- Print the Board in a differnt color

        item_fpga = f"(FPGA:{fpga}, {arch}, {type_}, {size}, {pack})"

        if config.terminal_mode():
            # -- Board name with a bullet point and color
            board_str = click.style(board, fg="cyan")
            item_board = f"{board_str}"

            # -- Item in one line
            one_line_item = f"{item_board}  {item_fpga}"

            # -- If there is enough space, print in one line
            if len(one_line_item) <= config.terminal_width:
                click.secho(one_line_item)

            # -- Not enough space: Print it in two separate lines
            else:
                two_lines_item = f"{item_board}\n      {item_fpga}"
                click.secho(two_lines_item)

        else:
            # -- Generate the report for a pipe. Single line, no color, no
            # -- bullet points.
            click.secho(f"{board:<{max_board_name_len}} |  {item_fpga}")

    # -- Print the footer.
    if config.terminal_mode():
        click.secho(seperator_line)

    click.secho(f"Total of {util.plurality(apio_ctx.boards, 'board')}")


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable = R0801
HELP = """
The boards commands lists the FPGA boards that are recongnized by apio.
Custom boards can be defined by placing a custom boards.json file in the
project directory. If such a case, the command
lists the boards from that custom file.

The commands is typically used in the root directory
of the project that contains the apio.ini file.

\b
Examples:
  apio boards                # List all boards
  apio boards | grep ecp5    # Filter boards results
  apio boards --project-dir foo/bar  # Use a different

"""


@click.command(
    "boards",
    short_help="List available board definitions.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@options.project_dir_option
def cli(
    _: click.core.Context,
    # Options
    project_dir: Path,
):
    """Implements the 'boards' command which lists available board
    definitions."""

    # -- Create the apio context. If project dir has a boards.json file,
    # -- it will be loaded instead of the apio's standard file.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=False)

    list_boards(apio_ctx)
    sys.exit(0)
