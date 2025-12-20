# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio fpgas' command"""

import sys
from datetime import date
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional
import click
from rich.table import Table
from rich import box
from apio.common import apio_console
from apio.common.apio_console import cout, ctable, cwrite
from apio.common.apio_styles import INFO, BORDER, EMPH1
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils import util, cmd_util
from apio.commands import options


@dataclass(frozen=True)
class Entry:
    """A class to hold the field of a single line of the report."""

    # pylint: disable=too-many-instance-attributes

    fpga: str
    board_count: int
    fpga_arch: str
    fpga_part_num: str
    fpga_size: str
    fpga_type: str
    fpga_pack: str
    fpga_speed: str

    def sort_key(self):
        """A key for sorting the fpga entries in our preferred order."""
        return (util.fpga_arch_sort_key(self.fpga_arch), self.fpga.lower())


def _collect_fpgas_entries(apio_ctx: ApioContext) -> List[Entry]:
    """Returns a sorted list of supported fpgas entries."""

    # -- Collect a sparse dict with fpga ids to board count.
    boards_counts: Dict[str, int] = {}
    for board_info in apio_ctx.boards.values():
        fpga_id = board_info.get("fpga-id", None)
        if fpga_id:
            old_count = boards_counts.get(fpga_id, 0)
            boards_counts[fpga_id] = old_count + 1

    # -- Collect all entries.
    result: List[Entry] = []
    for fpga_id, fpga_info in apio_ctx.fpgas.items():
        # -- Construct the Entry for this fpga.
        board_count = boards_counts.get(fpga_id, 0)
        fpga_arch = fpga_info.get("arch", "")
        fpga_part_num = fpga_info.get("part-num", "")
        fpga_size = fpga_info.get("size", "")
        fpga_type = fpga_info.get("type", "")
        fpga_pack = fpga_info.get("pack", "")
        fpga_speed = fpga_info.get("speed", "")
        # -- Append to the list
        result.append(
            Entry(
                fpga=fpga_id,
                board_count=board_count,
                fpga_arch=fpga_arch,
                fpga_part_num=fpga_part_num,
                fpga_size=fpga_size,
                fpga_type=fpga_type,
                fpga_pack=fpga_pack,
                fpga_speed=fpga_speed,
            )
        )

    # -- Sort boards by our preferred order.
    result.sort(key=lambda x: x.sort_key())

    # -- All done
    return result


def _list_fpgas(apio_ctx: ApioContext, verbose: bool):
    """Prints all the available FPGA definitions."""

    # -- Collect a sorted list of supported fpgas.
    entries: List[Entry] = _collect_fpgas_entries(apio_ctx)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=False,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Supported FPGAs",
        title_justify="left",
    )

    # -- Add columns
    table.add_column("FPGA-ID", no_wrap=True, style=EMPH1)
    table.add_column("BOARDS", no_wrap=True, justify="center")
    table.add_column("ARCH", no_wrap=True)
    table.add_column("PART-NUMBER", no_wrap=True)
    table.add_column("SIZE", no_wrap=True, justify="right")
    if verbose:
        table.add_column("TYPE", no_wrap=True)
        table.add_column("PACK", no_wrap=True)
        table.add_column("SPEED", no_wrap=True, justify="center")

    # -- Add rows.
    last_arch = None
    for entry in entries:
        # -- If switching architecture, add an horizontal separation line.
        if last_arch != entry.fpga_arch and apio_console.is_terminal():
            table.add_section()
        last_arch = entry.fpga_arch

        # -- Collect row values.
        values = []
        values.append(entry.fpga)
        values.append(f"{entry.board_count:>2}" if entry.board_count else "")
        values.append(entry.fpga_arch)
        values.append(entry.fpga_part_num)
        values.append(entry.fpga_size)
        if verbose:
            values.append(entry.fpga_type)
            values.append(entry.fpga_pack)
            values.append(entry.fpga_speed)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    ctable(table)

    # -- Show summary.
    if apio_console.is_terminal():
        cout(f"Total of {util.plurality(entries, 'fpga')}")
        if not verbose:
            cout(
                "Run 'apio fpgas -v' for additional columns.",
                style=INFO,
            )


def _list_fpgas_docs_format(apio_ctx: ApioContext):
    """Output fpgas information in a format for Apio Docs."""

    # -- Get the version of the 'definitions' package use. At this point it's
    # -- expected to be installed.
    def_version, _ = apio_ctx.profile.get_installed_package_info("definitions")

    # -- Collect the fpagas info into a list of entires, one per fpga.
    entries: List[Entry] = _collect_fpgas_entries(apio_ctx)

    # -- Determine column sizes
    w1 = max(len("FPGA-ID"), *(len(entry.fpga) for entry in entries))
    w2 = max(len("SIZE"), *(len(entry.fpga_size) for entry in entries))
    w3 = max(len("PART-NUM"), *(len(entry.fpga_part_num) for entry in entries))

    # -- Print page header
    today = date.today()
    today_str = f"{today.strftime('%B')} {today.day}, {today.year}"
    cwrite("\n<!-- BEGIN generation by 'apio fpgas --docs' -->\n")
    cwrite("\n# Supported FPGAs\n")
    cwrite(
        f"\nThis markdown page was generated automatically on {today_str} "
        f"from version `{def_version}` of the Apio definitions package.\n"
    )
    cwrite(
        "\n> Custom FPGAs definitions can be added in the project directory "
        "and can latter be contributed in the "
        "[apio-definitions](https://github.com/FPGAwars/apio-definitions/"
        "tree/main/definitions) repository.\n"
    )

    # -- Add the rows, with separation line between architecture groups.
    last_arch = None
    for entry in entries:
        # -- If switching architecture, add an horizontal separation line.
        if last_arch != entry.fpga_arch:

            cwrite(f"\n## {entry.fpga_arch.upper()} FPGAs\n")

            cwrite(
                "\n| {0} | {1} | {2} |\n".format(
                    "FPGA-ID".ljust(w1),
                    "SIZE".ljust(w2),
                    "PART-NUM".ljust(w3),
                )
            )
            cwrite(
                "| {0} | {1} | {2} |\n".format(
                    ":-".ljust(w1, "-"),
                    ":-".ljust(w2, "-"),
                    ":-".ljust(w3, "-"),
                )
            )

            last_arch = entry.fpga_arch

        cwrite(
            "| {0} | {1} | {2} |\n".format(
                entry.fpga.ljust(w1),
                entry.fpga_size.ljust(w2),
                entry.fpga_part_num.ljust(w3),
            )
        )

    cwrite("\n<!-- END generation by 'apio fpgas --docs' -->\n\n")


# -------- apio fpgas


# -- Text in the rich-text format of the python rich library.
APIO_FPGAS_HELP = """
The command 'apio fpgas' lists the FPGAs recognized by Apio. Custom FPGAs \
supported by the underlying Yosys toolchain can be defined by placing a \
custom 'fpgas.jsonc' file in the project directory, overriding Apio’s \
standard 'fpgas.jsonc' file.

Examples:[code]
  apio fpgas                # List all fpgas
  apio fpgas -v             # List with extra columns
  apio fpgas | grep gowin   # Filter FPGA results
  apio fpgas --docs         # Generate a report for Apio docs[/code]
"""


@click.command(
    name="fpgas",
    cls=cmd_util.ApioCommand,
    short_help="List available FPGA definitions.",
    help=APIO_FPGAS_HELP,
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
    """Implements the 'fpgas' command which lists available fpga
    definitions.
    """

    # -- Determine context policy for the apio context. For docs output we
    # -- want to ignore custom boards.
    project_policy = (
        ProjectPolicy.NO_PROJECT if docs else ProjectPolicy.PROJECT_OPTIONAL
    )

    # -- Create the apio context. If project dir has a fpgas.jsonc file,
    # -- it will be loaded instead of the apio's standard file.
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
        _list_fpgas_docs_format(apio_ctx)
    else:
        _list_fpgas(apio_ctx, verbose)

    sys.exit(0)
