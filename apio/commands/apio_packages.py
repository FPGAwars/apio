# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio packages' command"""

from typing import Tuple
import click
from apio.common.apio_console import cout
from apio.managers import installer
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils import pkg_util
from apio.commands import options
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# ------ apio packages install

# -- Text in the markdown format of the python rich library.
APIO_PACKAGES_INSTALL_HELP = """
The command 'apio packages install' installs Apio packages that are required \
for the operation of Apio on your system.

Examples:[code]
  apio packages install                   # Install missing packages.
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

    # -- If packages where specified, install all packages that are valid
    # -- for this platform.
    if not packages:
        packages = apio_ctx.platform_packages.keys()

    # -- Install the packages, one by one.
    for package in packages:
        installer.install_package(
            apio_ctx,
            package_spec=package,
            force_reinstall=force,
            cached_config_ok=False,
            verbose=verbose,
        )


# ------ apio packages uninstall

# -- Text in the markdown format of the python rich library.
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

    # -- If packages where specified, uninstall all packages that are valid
    # -- for this platform.
    if not packages:
        packages = apio_ctx.platform_packages.keys()

    # -- Uninstall the packages.
    for package in packages:
        installer.uninstall_package(
            apio_ctx, package_spec=package, verbose=verbose
        )


# ------ apio packages list

# -- Text in the markdown format of the python rich library.
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
def _list_cli():
    """Implements the 'apio packages list' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Scan the available and installed packages.
    scan = pkg_util.scan_packages(
        apio_ctx, cached_config_ok=False, verbose=False
    )

    # -- List the findings.
    # pkg_util.list_packages(apio_ctx, scan)
    pkg_util.print_packages_report(apio_ctx, scan)

    # -- Print an hint or summary based on the findings.
    if scan.num_errors_to_fix():
        cout(
            "",
            "Run 'apio packages fix' to fix the errors.",
            style="yellow",
        )
    elif scan.uninstalled_package_names:
        cout(
            "",
            "Run 'apio packages install' to install all "
            "available packages.",
            style="yellow",
        )
    else:
        cout("", "All packages are installed OK.", style="green")


# ------ apio packages fix

# -- Text in the markdown format of the python rich library.
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
def _fix_cli():
    """Implements the 'apio packages fix' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- First thing, fix broken packages, if any.
    _, fix_needed = installer.scan_and_fix_packages(
        apio_ctx, cached_config_ok=False, verbose=False
    )

    #  If fixed not needed, say so.
    if not fix_needed:
        cout("No errors to fix", style="green")


# ------ apio packages (group)

# -- Text in the markdown format of the python rich library.
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
