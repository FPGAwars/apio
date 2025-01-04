# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio packages' command"""

import sys
from typing import Tuple
import click
from click import secho
from apio.managers import installer
from apio.apio_context import ApioContext, ApioContextScope
from apio import pkg_util, util
from apio.commands import options
from apio.cmd_util import ApioGroup, ApioSubgroup


# ------ apio packages install

APIO_PACKAGES_INSTALL_HELP = """
The command ‘apio packages install’ installs Apio packages that are required
for the operation of Apio on your system.


\b
Examples:
  apio packages install                   # Install all missing packages.
  apio packages install --force           # Re/install all missing packages.
  apio packages install oss-cad-suite     # Install just this package.
  apio packages install examples@0.0.32   # Install a specific version.

Adding the --force option forces the reinstallation of existing packages;
otherwise, packages that are already installed correctly remain unchanged.
"""


@click.command(
    name="install",
    short_help="Install apio packages.",
    help=APIO_PACKAGES_INSTALL_HELP,
)
@click.argument("packages", nargs=-1, required=False)
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

    secho(f"Platform id '{apio_ctx.platform_id}'")

    # -- If packages where specified, install all packages that are valid
    # -- for this platform.
    if not packages:
        packages = apio_ctx.platform_packages.keys()

    # -- Install the packages, one by one.
    for package in packages:
        installer.install_package(
            apio_ctx, package_spec=package, force=force, verbose=verbose
        )


# ------ apio packages uninstall

APIO_PACKAGES_UNINSTALL_HELP = """
The command ‘apio packages uninstall’ removes installed Apio packages from
your system. The command does not uninstall the Apio tool itself.

\b
Examples:
  apio packages uninstall                 # Uninstall all packages.
  apio packages uninstall --sayyes        # Same but does not ask yes/no.
  apio packages uninstall oss-cad-suite   # Uninstall only given package(s).
"""


@click.command(
    name="uninstall",
    short_help="Uninstall apio packages.",
    help=APIO_PACKAGES_UNINSTALL_HELP,
)
@click.argument("packages", nargs=-1, required=False)
@options.sayyes
@options.verbose_option
def _uninstall_cli(
    # Arguments
    packages: Tuple[str],
    # Options
    sayyes: bool,
    verbose: bool,
):
    """Implements the 'apio packages uninstall' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- If packages where specified, uninstall all packages that are valid
    # -- for this platform.
    if not packages:
        packages = apio_ctx.platform_packages.keys()

    # -- Ask the user for confirmation
    if not sayyes:
        prompt = click.style(
            "Do you want to uninstall "
            f"{util.plurality(packages, 'apio package')}?",
            fg="magenta",
        )
        if not click.confirm(prompt):
            # -- User doesn't want to continue.
            secho("User said no", fg="red")
            sys.exit(1)

    # -- Here when going on with the uninstallation.
    secho(f"Platform id '{apio_ctx.platform_id}'")

    # -- Uninstall the packages, one by one
    for package in packages:
        installer.uninstall_package(
            apio_ctx, package_spec=package, verbose=verbose
        )


# ------ apio packages list

APIO_PACKAGES_LIST_HELP = """
The command ‘apio packages list’ lists the available and installed Apio
packages. The list of available packages depends on the operating system
you are using and may vary between operating systems.

\b
Examples:
  apio packages list
"""


@click.command(
    name="list",
    short_help="List apio packages.",
    help=APIO_PACKAGES_LIST_HELP,
)
def _list_cli():
    """Implements the 'apio packages list' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Scan the available and installed packages.
    scan = pkg_util.scan_packages(apio_ctx)

    # -- List the findings.
    pkg_util.list_packages(apio_ctx, scan)

    # -- Print an hint or summary based on the findings.
    if scan.num_errors():
        secho("[Hint] run 'apio packages fix' to fix the errors.", fg="yellow")
    elif scan.uninstalled_package_ids:
        secho(
            "[Hint] run 'apio packages install' to install all "
            "available packages.",
            fg="yellow",
        )
    else:
        secho("All available messages are installed.", fg="green")


# ------ apio packages fix

APIO_PACKAGES_FIX_HELP = """
The command ‘apio packages fix’ resolves partially installed or leftover Apio
packages that are listed as broken by the command ‘apio packages list’.
If there are no broken packages, the command does nothing and exits.

\b
Examples:
  apio packages fix           # Fix package errors.
  apio packages fix  -v       # Same but with verbose output.
"""


@click.command(
    name="fix",
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

    # -- Scan the availeable and installed packages.
    scan = pkg_util.scan_packages(apio_ctx)

    # -- Fix any errors.
    if scan.num_errors():
        installer.fix_packages(apio_ctx, scan, verbose)
    else:
        secho("No errors to fix")

    # -- Show the new state
    new_scan = pkg_util.scan_packages(apio_ctx)
    pkg_util.list_packages(apio_ctx, new_scan)


# ------ apio packages (group)


APIO_PACKAGES_HELP = """
The command group ‘apio packages’ provides commands to manage the installation
of Apio packages. These are not Python packages but Apio-specific packages
containing various tools and data essential for the operation of Apio.
These packages are installed after the installation of the Apio Python package
itself, using the command ‘apio packages install’.

The list of available
packages depends on the operating system you are using and may vary between
different operating systems.
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
