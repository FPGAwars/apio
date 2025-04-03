# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio examples' command"""

from pathlib import Path
from typing import List, Any
import click
from rich.table import Table
from rich import box
from apio.common import apio_console
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import INFO, BORDER, EMPH1
from apio.managers import installer
from apio.managers.examples import Examples, ExampleInfo
from apio.commands import options
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import util
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# ---- apio examples list


# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_LIST_HELP = """
The command 'apio examples list' lists the available Apio project examples \
that you can use.

Examples:[code]
  apio examples list                     # List all examples
  apio examples list  -v                 # More verbose output.
  apio examples list | grep alhambra-ii  # Show alhambra-ii examples.
  apio examples list | grep -i blink     # Show blinking examples.[/code]
"""


def examples_sort_key(entry: ExampleInfo) -> Any:
    """A key for sorting the fpga entries in our preferred order."""
    return (util.fpga_arch_sort_key(entry.fpga_arch), entry.name)


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def list_examples(apio_ctx: ApioContext, verbose: bool) -> None:
    """Print all the examples available. Return a process exit
    code, 0 if ok, non zero otherwise."""

    # -- Make sure that the examples package is installed.
    installer.install_missing_packages_on_the_fly(apio_ctx)

    # -- Get list of examples.
    entries: List[ExampleInfo] = Examples(apio_ctx).get_examples_infos()

    # -- Sort boards by case insensitive board name.
    entries.sort(key=examples_sort_key)

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=False,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Examples",
        title_justify="left",
    )

    # -- Add columns.
    table.add_column("BOARD/EXAMPLE", no_wrap=True, style=EMPH1)
    table.add_column("ARCH", no_wrap=True)
    if verbose:
        table.add_column("PART-NUM", no_wrap=True)
        table.add_column("SIZE", no_wrap=True)
    table.add_column(
        "DESCRIPTION",
        no_wrap=True,
        max_width=40 if verbose else 70,  # Limit in verbose mode.
    )

    # -- Add rows.
    last_arch = None
    for entry in entries:
        # -- Separation before each architecture group, unless piped out.
        if last_arch != entry.fpga_arch and apio_console.is_terminal():
            table.add_section()
        last_arch = entry.fpga_arch

        # -- Collect row's values.
        values = []
        values.append(entry.name)
        values.append(entry.fpga_arch)
        if verbose:
            values.append(entry.fpga_part_num)
            values.append(entry.fpga_size)
        values.append(entry.description)

        # -- Append the row
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)

    # -- Print summary.
    if apio_console.is_terminal():
        cout(f"Total of {util.plurality(entries, 'example')}")
        if not verbose:
            cout(
                "Run 'apio examples list -v' for additional columns.",
                style=INFO,
            )


@click.command(
    name="list",
    cls=ApioCommand,
    short_help="List the available apio examples.",
    help=APIO_EXAMPLES_LIST_HELP,
)
@options.verbose_option
def _list_cli(verbose: bool):
    """Implements the 'apio examples list' command group."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # --List all available examples.
    list_examples(apio_ctx, verbose)


# ---- apio examples fetch

# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_FETCH_HELP = """
The command 'apio examples fetch' fetches the files of the specified example \
to the current directory or to the directory specified by the '-dst' option. \
The destination directory does not need to exist, but if it does, it must be \
empty.

Examples:[code]
  apio examples fetch alhambra-ii/ledon
  apio examples fetch alhambra-ii/ledon -d foo/bar[/code]
"""


@click.command(
    name="fetch",
    cls=ApioCommand,
    short_help="Fetch the files of an example.",
    help=APIO_EXAMPLES_FETCH_HELP,
)
@click.argument("example", metavar="EXAMPLE", nargs=1, required=True)
@options.dst_option_gen(help="Set a different destination directory.")
def _fetch_cli(
    # Arguments
    example: str,
    # Options
    dst: Path,
):
    """Implements the 'apio examples fetch' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Create the examples manager.
    examples = Examples(apio_ctx)

    # -- Determine the destination directory.
    dst_dir_path = util.user_directory_or_cwd(
        dst, description="Destination", must_exist=False
    )

    # -- Fetch example files. This also creates the destination directory
    # -- if missing.
    examples.copy_example_files(example, dst_dir_path)


# ---- apio examples fetch-board

# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_FETCH_BOARD_HELP = """
The command 'apio examples fetch-board' is used to fetch all the Apio \
examples for a specific board. The examples are copied to the current \
directory or to the specified destination directory if the '–-dst' \
option is provided.

Examples:[code]
  apio examples fetch-board alhambra-ii  # Fetch board examples.

"""


@click.command(
    name="fetch-board",
    cls=ApioCommand,
    short_help="Fetch all examples of a board.",
    help=APIO_EXAMPLES_FETCH_BOARD_HELP,
)
@click.argument("board", metavar="BOARD", nargs=1, required=True)
@options.dst_option_gen(help="Set a different destination directory.")
def _fetch_board_cli(
    # Arguments
    board: str,
    # Options
    dst: Path,
):
    """Implements the 'apio examples fetch-board' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- This fails with an error message if there is no such board.
    apio_ctx.lookup_board_name(board)

    # -- Create the examples manager.
    examples = Examples(apio_ctx)

    # -- Determine the destination directory.
    dst_dir_path = util.user_directory_or_cwd(
        dst, description="Destination", must_exist=False
    )

    # -- Fetch the examples. This also creates the destination directory if
    # -- needed.
    examples.copy_board_examples(board, dst_dir_path)


# ---- apio examples

# -- Text in the rich-text format of the python rich library.
APIO_EXAMPLES_HELP = """
The command group 'apio examples' provides subcommands for listing and \
fetching Apio-provided examples. Each example is a self-contained \
mini-project that can be built and uploaded to an FPGA board.
"""


# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _list_cli,
            _fetch_cli,
            _fetch_board_cli,
        ],
    )
]


@click.command(
    name="examples",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="List and fetch apio examples.",
    help=APIO_EXAMPLES_HELP,
)
def cli():
    """Implements the 'apio examples' command group."""

    # pass
