# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio packages' command"""

import click
from rich.table import Table
from rich import box
from apio.common.apio_console import cout, ctable
from apio.common.apio_styles import INFO, BORDER, ERROR, SUCCESS
from apio.managers import packages
from apio.apio_context import ApioContext, ProjectPolicy, RemoteConfigPolicy
from apio.commands import options
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


def print_packages_report(apio_ctx: ApioContext) -> None:
    """A common function to print the state of the packages."""

    # -- Scan the packages
    scan = packages.scan_packages(apio_ctx)

    # -- Shortcuts to reduce clutter.
    get_package_version = apio_ctx.profile.get_package_installed_info
    get_package_info = apio_ctx.get_package_info

    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Packages Status",
        title_justify="left",
        padding=(0, 2),
    )

    table.add_column("PACKAGE NAME", no_wrap=True)
    table.add_column("VERSION", no_wrap=True)
    table.add_column("PLATFORM", no_wrap=True)
    table.add_column("DESCRIPTION", no_wrap=True)
    table.add_column("STATUS", no_wrap=True)

    # -- Add raws for installed ok packages.
    for package_name in scan.installed_ok_package_names:
        version, platform_id = get_package_version(package_name)
        description = get_package_info(package_name)["description"]
        table.add_row(package_name, version, platform_id, description, "OK")

    # -- Add rows for uninstalled packages.
    for package_name in scan.uninstalled_package_names:
        description = get_package_info(package_name)["description"]
        table.add_row(
            package_name, None, description, "Uninstalled", style=INFO
        )

    # -- Add raws for installed with version or platform mismatch.
    for package_name in scan.bad_version_package_names:
        version, platform_id = get_package_version(package_name)
        description = get_package_info(package_name)["description"]
        table.add_row(
            package_name,
            version,
            platform_id,
            description,
            "Mismatch",
            style=ERROR,
        )

    # -- Add rows for broken packages.
    for package_name in scan.broken_package_names:
        description = get_package_info(package_name)["description"]
        table.add_row(
            package_name, None, None, description, "Broken", style=ERROR
        )

    # -- Render table.
    cout()
    ctable(table)

    # -- Define errors table.
    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="Apio Packages Errors",
        title_justify="left",
        padding=(0, 2),
    )

    # -- Add columns.
    table.add_column("ERROR TYPE", no_wrap=True, min_width=15, style=ERROR)
    table.add_column("NAME", no_wrap=True, min_width=15)

    # -- Add rows.
    for package_name in scan.orphan_package_names:
        table.add_row("Orphan package", package_name)

    for name in sorted(scan.orphan_dir_names):
        table.add_row("Orphan dir", name)

    for name in sorted(scan.orphan_file_names):
        table.add_row("Orphan file", name)

    # -- Render the table, unless empty.
    if table.row_count:
        cout()
        ctable(table)

    # -- Print summary.
    cout()
    if scan.is_all_ok():
        cout("All Apio packages are installed OK.", style=SUCCESS)
    else:
        cout(
            "Run 'apio packages update' to update the packages.",
            style=INFO,
        )


# ------ apio packages update

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_UPDATE_HELP = """
The command 'apio packages update' updates the installed Apio packages  \
to their latest requirements.

Examples:[code]
  apio packages update            # Update packages
  apio pack upd                   # Same, with shortcuts
  apio packages update --force    # Force reinstallation from scratch
  apio packages update --verbose  # Provide additional info[/code]

Adding the '--force' option forces the reinstallation of existing packages; \
otherwise, packages that are already installed correctly remain unchanged.

It is highly recommended to run the 'apio packages update' once in a while \
because it check the Apio remote server for the latest packages versions \
which may included fixes and enhancements such as new examples that were \
added to the examples package.
"""


@click.command(
    name="update",
    cls=ApioCommand,
    short_help="Update apio packages.",
    help=APIO_PACKAGES_UPDATE_HELP,
)
@options.force_option_gen(help="Force reinstallation.")
@options.verbose_option
def _update_cli(
    # Options
    force: bool,
    verbose: bool,
):
    """Implements the 'apio packages update' command."""

    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        config_policy=RemoteConfigPolicy.GET_FRESH,
    )

    # cout(f"Platform id '{apio_ctx.platform_id}'")

    # -- First thing, fix broken packages, if any. This forces fetching
    # -- of the latest remote config file.
    packages.scan_and_fix_packages(apio_ctx)

    # -- Install the packages, one by one.
    for package in apio_ctx.platform_packages:
        packages.install_package(
            apio_ctx,
            package_name=package,
            force_reinstall=force,
            verbose=verbose,
        )

    # -- Scan the available and installed packages.
    print_packages_report(apio_ctx)


# ------ apio packages list

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_LIST_HELP = """
The command 'apio packages list' lists the available and installed Apio \
packages. The list of available packages depends on the operating system \
you are using and may vary between operating systems.

Examples:[code]
  apio packages list[/code]
"""


@click.command(
    name="list",
    cls=ApioCommand,
    short_help="List apio packages.",
    help=APIO_PACKAGES_LIST_HELP,
)
# @options.verbose_option
def _list_cli():
    """Implements the 'apio packages list' command."""

    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        config_policy=RemoteConfigPolicy.CACHED_OK,
    )

    # -- Print packages report.
    print_packages_report(apio_ctx)


# ------ apio packages (group)

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_HELP = """
The command group 'apio packages' provides commands to manage the \
installation of Apio packages. These are not Python packages but \
Apio  packages containing various tools and data essential for the \
operation of Apio.

The list of available packages depends on the operating system you are \
using and may vary between different operating systems.
"""


# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _update_cli,
            _list_cli,
        ],
    )
]


@click.command(
    name="packages",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Manage the apio packages.",
    help=APIO_PACKAGES_HELP,
)
def cli():
    """Implements the 'apio packages' command group.'"""

    # pass
