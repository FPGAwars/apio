# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio boards' command"""

import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import click
from rich.table import Table
from rich import box
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import INFO
from apio.common import apio_console
from apio.common.apio_styles import BORDER, EMPH1
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import util, cmd_util
from apio.commands import options
from apio.managers.examples import Examples


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Entry:
    """Holds the values of a single board report line."""

    board: str
    examples_count: str
    board_description: str
    fpga_arch: str
    fpga_size: str
    fpga: str
    fpga_part_num: str
    fpga_type: str
    fpga_pack: str
    fpga_speed: str
    programmer: str

    def sort_key(self):
        """A key for sorting the fpga entries in our preferred order."""
        return (util.fpga_arch_sort_key(self.fpga_arch), self.board.lower())


# R0914: Too many local variables (17/15)
# pylint: disable=R0914
def list_boards(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available board definitions."""

    # -- Get examples counts by board. This is a sparse dictionary.
    examples = Examples(apio_ctx)
    examples_counts: Dict[str, int] = examples.count_examples_by_board()

    # -- Collect the boards info into a list of entires, one per board.
    entries: List[Entry] = []
    for board, board_info in apio_ctx.boards.items():
        fpga = board_info.get("fpga", "")
        fpga_info = apio_ctx.fpgas.get(fpga, {})

        examples_count = "   " + str(examples_counts.get(board, ""))
        board_description = board_info.get("description", "")
        fpga_arch = fpga_info.get("arch", "")
        fpga_size = fpga_info.get("size", "")
        fpga_part_num = fpga_info.get("part_num", "")
        fpga_type = fpga_info.get("type", "")
        fpga_pack = fpga_info.get("pack", "")
        fpga_speed = fpga_info.get("speed", "")
        programmer = board_info.get("programmer", {}).get("type", "")

        entries.append(
            Entry(
                board=board,
                examples_count=examples_count,
                board_description=board_description,
                fpga_arch=fpga_arch,
                fpga_size=fpga_size,
                fpga=fpga,
                fpga_part_num=fpga_part_num,
                fpga_type=fpga_type,
                fpga_pack=fpga_pack,
                fpga_speed=fpga_speed,
                programmer=programmer,
            )
        )

    # -- Sort boards by our preferred order.
    entries.sort(key=lambda x: x.sort_key())

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=False,
        box=box.SQUARE,
        border_style=BORDER,
        title_justify="left",
        title="Apio Supported Boards",
    )

    # -- Add columns.
    table.add_column("BOARD-ID", no_wrap=True, style=EMPH1)
    table.add_column("EXMPLS", no_wrap=True)
    if verbose:
        table.add_column("DESCRIPTION", no_wrap=True, max_width=25)
    table.add_column("ARCH", no_wrap=True)
    table.add_column("SIZE", no_wrap=True)
    if verbose:
        table.add_column("FPGA-ID", no_wrap=True)
    table.add_column("PART-NUMBER", no_wrap=True)
    table.add_column("PROGRAMMER", no_wrap=True)

    # -- Add rows, with separation line between architecture groups.
    last_arch = None
    for entry in entries:
        # -- If switching architecture, add an horizontal separation line.
        if last_arch != entry.fpga_arch and apio_console.is_terminal():
            table.add_section()
        last_arch = entry.fpga_arch

        # -- Collect row values.
        values = []
        values.append(entry.board)
        values.append(str(entry.examples_count))
        if verbose:
            values.append(entry.board_description)
        values.append(entry.fpga_arch)
        values.append(str(entry.fpga_size))
        if verbose:
            values.append(entry.fpga)
        values.append(entry.fpga_part_num)
        values.append(entry.programmer)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)

    # -- Show the summary.

    if apio_console.is_terminal():
        cout(f"Total of {util.plurality(entries, 'board')}")
        if not verbose:
            cout(
                "Run 'apio boards -v' for additional columns.",
                style=INFO,
            )


# ------------- apio boards


# -- Text in the rich-text format of the python rich library.
APIO_BOARDS_HELP = """
The command 'apio boards' lists the FPGA boards recognized by Apio. \
Custom boards can be defined by placing a custom 'boards.jsonc' file in the \
project directory, which will override Apio’s default 'boards.jsonc' file.

Examples:[code]
  apio boards                   # List all boards.
  apio boards -v                # List with extra columns..
  apio boards | grep ecp5       # Filter boards results.[/code]

"""


@click.command(
    name="boards",
    cls=cmd_util.ApioCommand,
    short_help="List available board definitions.",
    help=APIO_BOARDS_HELP,
)
@options.verbose_option
@options.project_dir_option
def cli(
    # Options
    verbose: bool,
    project_dir: Path,
):
    """Implements the 'boards' command which lists available board
    definitions."""

    # -- Create the apio context. If the project exists, it's custom
    # -- boards.jsonc is also loaded.
    apio_ctx = ApioContext(
        scope=ApioContextScope.PROJECT_OPTIONAL,
        project_dir_arg=project_dir,
    )

    list_boards(apio_ctx, verbose)
    sys.exit(0)
