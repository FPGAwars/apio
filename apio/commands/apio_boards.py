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
from datetime import date
from dataclasses import dataclass
from typing import List, Dict, Optional
import click
from rich.table import Table
from rich import box
from apio.common.apio_console import cout, ctable, cwrite
from apio.common.apio_styles import INFO
from apio.common import apio_console
from apio.common.apio_styles import BORDER, EMPH1
from apio.utils import util, cmd_util
from apio.commands import options
from apio.managers.examples import Examples
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


@dataclass(frozen=True)
class Entry:
    """Holds the values of a single board report line."""

    # pylint: disable=too-many-instance-attributes

    board: str
    examples_count: str
    board_description: str
    fpga_arch: str
    fpga_size: str
    fpga_id: str
    fpga_part_num: str
    fpga_type: str
    fpga_pack: str
    fpga_speed: str
    programmer: str

    def sort_key(self):
        """A key for sorting the fpga entries in our preferred order."""
        return (util.fpga_arch_sort_key(self.fpga_arch), self.board.lower())


def _collect_board_entries(apio_ctx) -> List[Entry]:

    # pylint: disable=too-many-locals

    # -- Get examples counts by board. This is a sparse dictionary.
    examples = Examples(apio_ctx)
    examples_counts: Dict[str, int] = examples.count_examples_by_board()

    # -- Collect the boards info into a list of entires, one per board.
    result: List[Entry] = []
    for board, board_info in apio_ctx.boards.items():
        fpga_id = board_info.get("fpga-id", "")
        fpga_info = apio_ctx.fpgas.get(fpga_id, {})

        examples_count = "   " + str(examples_counts.get(board, ""))
        board_description = board_info.get("description", "")
        fpga_arch = fpga_info.get("arch", "")
        fpga_size = fpga_info.get("size", "")
        fpga_part_num = fpga_info.get("part-num", "")
        fpga_type = fpga_info.get("type", "")
        fpga_pack = fpga_info.get("pack", "")
        fpga_speed = fpga_info.get("speed", "")
        programmer_id = board_info.get("programmer", {}).get("id", "")

        result.append(
            Entry(
                board=board,
                examples_count=examples_count,
                board_description=board_description,
                fpga_arch=fpga_arch,
                fpga_size=fpga_size,
                fpga_id=fpga_id,
                fpga_part_num=fpga_part_num,
                fpga_type=fpga_type,
                fpga_pack=fpga_pack,
                fpga_speed=fpga_speed,
                programmer=programmer_id,
            )
        )

    # -- Sort boards by our preferred order.
    result.sort(key=lambda x: x.sort_key())

    # -- All done.
    return result


def _list_boards(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available board definitions."""

    # -- Collect the boards info into a list of entires, one per board.
    entries: List[Entry] = _collect_board_entries(apio_ctx)

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
        table.add_column("PRODUCT", no_wrap=True, max_width=25)
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
            values.append(entry.fpga_id)
        values.append(entry.fpga_part_num)
        values.append(entry.programmer)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    ctable(table)

    # -- Show the summary.

    if apio_console.is_terminal():
        cout(f"Total of {util.plurality(entries, 'board')}")
        if not verbose:
            cout(
                "Run 'apio boards -v' for additional columns.",
                style=INFO,
            )


def _list_boards_docs_format(apio_ctx: ApioContext):
    """Output boards information in a format for Apio Docs."""

    # -- Get the version of the 'definitions' package use. At this point it's
    # -- expected to be installed.
    def_version, _ = apio_ctx.profile.get_installed_package_info("definitions")

    # -- Collect the boards info into a list of entires, one per board.
    entries: List[Entry] = _collect_board_entries(apio_ctx)

    # -- Determine column sizes
    w1 = max(len("BOARD"), *(len(entry.board) for entry in entries))
    w2 = max(len("SIZE"), *(len(entry.fpga_size) for entry in entries))
    w3 = max(
        len("DESCRIPTION"),
        *(len(entry.board_description) for entry in entries),
    )
    w4 = max(len("FPGA"), *(len(entry.fpga_part_num) for entry in entries))

    # -- Print page header
    today = date.today()
    today_str = f"{today.strftime('%B')} {today.day}, {today.year}"
    cwrite("\n<!-- BEGIN generation by 'apio boards --docs' -->\n")
    cwrite("\n# Supported FPGA Boards\n")
    cwrite(
        f"\nThis markdown page was generated automatically on {today_str} "
        f"from version `{def_version}` of the Apio definitions package.\n"
    )
    cwrite(
        "\n> Custom board definitions can be added in the project directory "
        "can latter be contributed to Apio in the "
        "[apio-definitions](https://github.com/FPGAwars/apio-definitions/"
        "tree/main/definitions) repository.\n"
    )

    # -- Add the rows, with separation line between architecture groups.
    last_arch = None
    for entry in entries:
        # -- If switching architecture, add an horizontal separation line.
        if last_arch != entry.fpga_arch:

            cout(f"\n## {entry.fpga_arch.upper()} boards")

            cwrite(
                "\n| {0} | {1} | {2} | {3} |\n".format(
                    "BOARD-ID".ljust(w1),
                    "SIZE".ljust(w2),
                    "DESCRIPTION".ljust(w3),
                    "FPGA".ljust(w4),
                )
            )
            cwrite(
                "| {0} | {1} | {2} | {3} |\n".format(
                    ":-".ljust(w1, "-"),
                    ":-".ljust(w2, "-"),
                    ":-".ljust(w3, "-"),
                    ":-".ljust(w4, "-"),
                )
            )

            last_arch = entry.fpga_arch

        cwrite(
            "| {0} | {1} | {2} | {3} |\n".format(
                entry.board.ljust(w1),
                entry.fpga_size.ljust(w2),
                entry.board_description.ljust(w3),
                entry.fpga_part_num.ljust(w4),
            )
        )

    cwrite("\n<!-- END generation by 'apio boards --docs' -->\n\n")


# ------------- apio boards


# -- Text in the rich-text format of the python rich library.
APIO_BOARDS_HELP = """
The command 'apio boards' lists the FPGA boards recognized by Apio. \
Custom boards can be defined by placing a custom 'boards.jsonc' file in the \
project directory, which will override Apio’s default 'boards.jsonc' file.

Examples:[code]
  apio boards                   # List all boards
  apio boards -v                # List with extra columns
  apio boards | grep ecp5       # Filter boards results
  apio boards --docs            # Generate a report for Apio docs[/code]

"""


@click.command(
    name="boards",
    cls=cmd_util.ApioCommand,
    short_help="List available board definitions.",
    help=APIO_BOARDS_HELP,
)
@options.verbose_option
@options.docs_format_option
@options.project_dir_option
def cli(
    # Options
    verbose: bool,
    docs: bool,
    project_dir: Optional[Path],
):
    """Implements the 'boards' command which lists available board
    definitions."""

    # -- Determine project policy for the apio context. For docs output we
    # -- want to ignore custom boards.
    project_policy = (
        ProjectPolicy.NO_PROJECT if docs else ProjectPolicy.PROJECT_OPTIONAL
    )

    # -- Create the apio context. If the project exists, it's custom
    # -- boards.jsonc is also loaded. Config is required since we query
    # -- the example package.
    # -- We suppress the message with the env and board ids since it's
    # -- not relevant for this command.
    apio_ctx = ApioContext(
        project_policy=project_policy,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        project_dir_arg=project_dir,
        report_env=False,
    )

    if docs:
        _list_boards_docs_format(apio_ctx)
    else:
        _list_boards(apio_ctx, verbose)

    sys.exit(0)
