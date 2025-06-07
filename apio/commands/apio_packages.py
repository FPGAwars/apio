# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio packages' command"""

from typing import Tuple
import click
from rich.table import Table
from rich import box
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import INFO, BORDER, ERROR, SUCCESS
from apio.managers import installer
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import pkg_util
from apio.commands import options
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


def print_packages_report(apio_ctx: ApioContext, verbose: bool) -> None:
    """A common function to print the state of the packages."""

    # -- Scan the packages
    scan = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=False, verbose=verbose
    )

    # -- Shortcuts to reduce clutter.
    get_package_version = apio_ctx.profile.get_package_installed_version
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
    table.add_column("DESCRIPTION", no_wrap=True)
    table.add_column("STATUS", no_wrap=True)

    # -- Add raws for installed ok packages.
    for package_name in scan.installed_ok_package_names:
        version = get_package_version(package_name)
        description = get_package_info(package_name)["description"]
        table.add_row(package_name, version, description, "OK")

    # -- Add rows for uninstalled packages.
    for package_name in scan.uninstalled_package_names:
        description = get_package_info(package_name)["description"]
        table.add_row(
            package_name, None, description, "Uninstalled", style=INFO
        )

    # -- Add raws for installed with version mismatch packages.
    for package_name in scan.bad_version_package_names:
        version = get_package_version(package_name)
        description = get_package_info(package_name)["description"]
        table.add_row(
            package_name,
            version,
            description,
            "Wrong version",
            style=ERROR,
        )

    # -- Add rows for broken packages.
    for package_name in scan.broken_package_names:
        description = get_package_info(package_name)["description"]
        table.add_row(package_name, None, description, "Broken", style=ERROR)

    # -- Render table.
    cout()
    cprint(table)

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
        cprint(table)

    # -- Print summary.
    cout()
    if not scan.packages_installed_ok():
        cout(
            "Run 'apio packages install' to install all packages.",
            style=INFO,
        )
    elif scan.num_errors_to_fix():
        cout(
            "Run 'apio packages fix' to fix the errors.",
            style=INFO,
        )
    else:
        cout("All Apio packages are installed OK.", style=SUCCESS)


# ------ apio packages install

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_INSTALL_HELP = """
The command 'apio packages install' installs Apio packages that are required \
for the operation of Apio on your system.

Examples:[code]
  apio packages install                   # Install missing packages.
  apio pack inst                          # Same, with shortcuts
  apio packages install --force           # Reinstall all packages.
  apio packages install oss-cad-suite     # Install package.
  apio packages install examples@0.0.32   # Install a specific version.[/code]

Adding the '--force' option forces the reinstallation of existing packages; \
otherwise, packages that are already installed correctly remain unchanged.
"""


@click.command(
    name="install",
    cls=ApioCommand,
    short_help="Install apio packages.",
    help=APIO_PACKAGES_INSTALL_HELP,
)
@click.argument("packages", metavar="PACKAGE", nargs=-1, required=False)
@options.force_option_gen(help="Force installation.")
@options.verbose_option
def _install_cli(
    # Arguments
    packages: Tuple[str],
    # Options
    force: bool,
    verbose: bool,
):
    """Implements the 'apio packages install' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    cout(f"Platform id '{apio_ctx.platform_id}'")

    # -- First thing, fix broken packages, if any.
    installer.scan_and_fix_packages(
        apio_ctx, cached_config_ok=False, verbose=verbose
    )

    # -- If packages where specified, install all the missing ones, if any.
    scan = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=False, verbose=False
    )
    if not packages:
        packages = apio_ctx.platform_packages.keys()

    # -- Install the packages, one by one.
    for package in packages:
        if force or package not in scan.installed_ok_package_names:
            installer.install_package(
                apio_ctx,
                package_spec=package,
                force_reinstall=force,
                cached_config_ok=False,
                verbose=verbose,
            )

    # -- Scan the available and installed packages.
    print_packages_report(apio_ctx, verbose=verbose)


# ------ apio packages uninstall

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_UNINSTALL_HELP = """
The command 'apio packages uninstall' removes installed Apio packages from \
your system. The command does not uninstall the Apio tool itself.

Examples:[code]
  apio packages uninstall                    # Uninstall all packages
  apio packages uninstall oss-cad-suite      # Uninstall a package
  apio packages uninstall verible examples   # Uninstall two packages[/code]
"""


@click.command(
    name="uninstall",
    cls=ApioCommand,
    short_help="Uninstall apio packages.",
    help=APIO_PACKAGES_UNINSTALL_HELP,
)
@click.argument("packages", metavar="PACKAGE", nargs=-1, required=False)
@options.verbose_option
def _uninstall_cli(
    # Arguments
    packages: Tuple[str],
    # Options
    verbose: bool,
):
    """Implements the 'apio packages uninstall' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- First thing, fix broken packages, if any.
    installer.scan_and_fix_packages(
        apio_ctx, cached_config_ok=False, verbose=verbose
    )

    # -- Scan the packages.
    scan = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=False, verbose=False
    )

    # -- If packages where specified, uninstall all packages.
    if not packages:
        packages = apio_ctx.platform_packages.keys()

    # -- Uninstall the packages.
    for package in packages:
        # -- Skip packages that are alredy uninstalled.
        if package not in scan.uninstalled_package_names:
            installer.uninstall_package(
                apio_ctx, package_spec=package, verbose=verbose
            )

    # -- Print updated package report.
    print_packages_report(apio_ctx, verbose=verbose)


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
@options.verbose_option
def _list_cli(
    # Options
    verbose: bool,
):
    """Implements the 'apio packages list' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Print packages report.
    print_packages_report(apio_ctx, verbose=verbose)


# ------ apio packages fix

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_FIX_HELP = """
The command 'apio packages fix' removes broken or obsolete packages \
that are listed as broken by the command 'apio packages list'.

Examples:[code]
  apio packages fix     # Fix package errors, if any.[/code]
"""


@click.command(
    name="fix",
    cls=ApioCommand,
    short_help="Fix broken apio packages.",
    help=APIO_PACKAGES_FIX_HELP,
)
@options.verbose_option
def _fix_cli(
    # Options
    verbose: bool,
):
    """Implements the 'apio packages fix' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- First thing, fix broken packages, if any.
    installer.scan_and_fix_packages(
        apio_ctx, cached_config_ok=False, verbose=verbose
    )

    # -- Print updated packages report.
    print_packages_report(apio_ctx, verbose=False)


# ------ apio packages (group)

# -- Text in the rich-text format of the python rich library.
APIO_PACKAGES_HELP = """
The command group 'apio packages' provides commands to manage the \
installation of Apio packages. These are not Python packages but \
Apio-specific packages containing various tools and data essential for the \
operation of Apio.

The list of available packages depends on the operating system you are \
using and may vary between different operating systems.
"""


# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _install_cli,
            _uninstall_cli,
            _list_cli,
            _fix_cli,
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
