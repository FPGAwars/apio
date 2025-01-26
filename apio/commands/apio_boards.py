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
from dataclasses import dataclass
from typing import List, Dict
import click
from apio.utils.apio_console import cout, cstyle
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import util
from apio.commands import options
from apio.managers.examples import Examples


# R0801: Similar lines in 2 files
# pylint: disable=R0801
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
        """A key for sorting the fpga entries in our prefered order."""
        return (util.fpga_arch_sort_key(self.fpga_arch), self.board.lower())


# R0914: Too many local variables (17/15)
# pylint: disable=R0914
# pylint: disable=too-many-statements
def list_boards(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available board definitions."""

    # -- Get the output info (terminal vs pipe).
    output_config = util.get_terminal_config()

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

    # -- Sort boards by our prefered order.
    entries.sort(key=lambda x: x.sort_key())

    # -- Compute the columns widths.

    margin = 2 if verbose else 4
    board_len = max(len(x.board) for x in entries) + margin - 2
    examples_count_len = 7 + margin
    board_description_len = (
        max(len(x.board_description) for x in entries) + margin
    )
    fpga_arch_len = max(len(x.fpga_arch) for x in entries) + margin
    fpga_size_len = max(len(x.fpga_size) for x in entries) + margin
    fpga_len = max(len(x.fpga) for x in entries) + margin
    fpga_part_num_len = max(len(x.fpga_part_num) for x in entries) + margin
    fpga_type_len = max(len(x.fpga_type) for x in entries) + margin
    fpga_pack_len = max(len(x.fpga_pack) for x in entries) + margin
    fpga_speed_len = 5 + margin
    programmer_len = max(len(x.programmer) for x in entries) + margin

    # -- Construct the title fields.
    parts = []
    parts.append(f"{'BOARD':<{board_len}}")
    parts.append(f"{'EXAMPLES':<{examples_count_len}}")
    if verbose:
        parts.append(f"{'DESCRIPTION':<{board_description_len}}")
    parts.append(f"{'ARCH':<{fpga_arch_len}}")
    parts.append(f"{'SIZE':<{fpga_size_len}}")
    if verbose:
        parts.append(f"{'FPGA-ID':<{fpga_len}}")
    parts.append(f"{'PART-NUMBER':<{fpga_part_num_len}}")
    if verbose:
        parts.append(f"{'TYPE':<{fpga_type_len}}")
        parts.append(f"{'PACK':<{fpga_pack_len}}")
        parts.append(f"{'SPEED':<{fpga_speed_len}}")
    parts.append(f"{'PROGRAMMER':<{programmer_len}}")

    # -- Print the title line.
    cout("".join(parts), style="cyan")

    # -- Print all the boards.
    last_arch = None
    for entry in entries:
        # -- If not piping, add architecture groups seperations.
        if last_arch != entry.fpga_arch and output_config.terminal_mode:
            cout("")
            cout(f"{entry.fpga_arch.upper()}", style="magenta")
        last_arch = entry.fpga_arch

        # -- Construct the line fields.
        parts = []
        parts.append(cstyle(f"{entry.board:<{board_len}}", style="cyan"))
        parts.append(f"{entry.examples_count:<{examples_count_len}}")
        if verbose:
            parts.append(f"{entry.board_description:<{board_description_len}}")
        parts.append(f"{entry.fpga_arch:<{fpga_arch_len}}")
        parts.append(f"{entry.fpga_size:<{fpga_size_len}}")
        if verbose:
            parts.append(f"{entry.fpga:<{fpga_len}}")
        parts.append(f"{entry.fpga_part_num:<{fpga_part_num_len}}")
        if verbose:
            parts.append(f"{entry.fpga_type:<{fpga_type_len}}")
            parts.append(f"{entry.fpga_pack:<{fpga_pack_len}}")
            parts.append(f"{entry.fpga_speed:<{fpga_speed_len}}")
        parts.append(f"{entry.programmer:<{programmer_len}}")

        # -- Print the line
        cout("".join(parts))

    # -- Show the summary.

    if output_config.terminal_mode:
        cout(f"Total of {util.plurality(entries, 'board')}")
        if not verbose:
            cout(
                "Run 'apio boards -v' for additional columns.", style="yellow"
            )


# ---------------------------
# -- COMMAND
# ---------------------------
# R0801: Similar lines in 2 files
# pylint: disable = R0801
APIO_BOARDS_HELP = """
The command 'apio boards' lists the FPGA boards recognized by Apio.
Custom boards can be defined by placing a custom 'boards.jsonc' file in the
project directory, which will override Apio’s default 'boards.jsonc' file.

\b
Examples:
  apio boards                   # List all boards.
  apio boards -v                # List with extra columns..
  apio boards | grep ecp5       # Filter boards results.

"""


@click.command(
    name="boards",
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
