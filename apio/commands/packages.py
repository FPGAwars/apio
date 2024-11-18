# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio packages' command"""

from pathlib import Path
from typing import Tuple, List
from varname import nameof
import click
from click.core import Context
from apio.managers import installer
from apio.resources import Resources
from apio import cmd_util, pkg_util, util
from apio.commands import options


def _install(
    resources: Resources, packages: List[str], force: bool, verbose: bool
) -> int:
    """Handles the --install operation. Returns exit code."""
    click.secho(f"Platform id '{resources.platform_id}'")

    # -- If packages where specified, install all packages that are valid
    # -- for this platform.
    if not packages:
        packages = resources.platform_packages.keys()

    # -- Install the packages, one by one.
    for package in packages:
        installer.install_package(
            resources, package_spec=package, force=force, verbose=verbose
        )

    return 0


def _uninstall(
    resources: Resources, packages: List[str], verbose: bool, sayyes: bool
) -> int:
    """Handles the --uninstall operation. Returns exit code."""

    # -- If packages where specified, uninstall all packages that are valid
    # -- for this platform.
    if not packages:
        packages = resources.platform_packages.keys()

    # -- Ask the user for confirmation
    if not (
        sayyes
        or click.confirm(
            "Do you want to uninstall " f"{util.count(packages, 'package')}?"
        )
    ):
        # -- User doesn't want to continue.
        click.secho("User said no", fg="red")
        return 1

    # -- Here when going on with the uninstallation.
    click.secho(f"Platform id '{resources.platform_id}'")

    # -- Uninstall the packages, one by one
    for package in packages:
        installer.uninstall_package(
            resources, package_spec=package, verbose=verbose
        )

    return 0


def _fix(resources: Resources, verbose: bool) -> int:
    """Handles the --fix operation. Returns exit code."""

    # -- Scan the availeable and installed packages.
    scan = pkg_util.scan_packages(resources)

    # -- Fix any errors.
    if scan.num_errors():
        installer.fix_packages(resources, scan, verbose)
    else:
        click.secho("No errors to fix")

    # -- Show the new state
    new_scan = pkg_util.scan_packages(resources)
    pkg_util.list_packages(resources, new_scan)

    return 0


def _list(resources: Resources, verbose: bool) -> int:
    """Handles the --list operation. Returns exit code."""

    if verbose:
        click.secho(f"Platform id '{resources.platform_id}'")

    # -- Scan the available and installed packages.
    scan = pkg_util.scan_packages(resources)

    # -- List the findings.
    pkg_util.list_packages(resources, scan)

    # -- Print an hint or summary based on the findings.
    if scan.num_errors():
        click.secho(
            "[Hint] run 'apio packages -fix' to fix the errors.", fg="yellow"
        )
    elif scan.uninstalled_package_ids:
        click.secho(
            "[Hint] run 'apio packages -install' to install all "
            "available packages.",
            fg="yellow",
        )
    else:
        click.secho("All available messages are installed.", fg="green")

    return 0


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The packages command manages the apio packages which are required by most
of the apio commands. These are not python packages but apio
specific packages that contain various tools and data and they can be installed
after the apip python package is installed using 'pip install apip' or
similar command. Also note that some apio packages are available and required
only of some platforms but not on others.

\b
Examples:
  apio packages --list                      # List the apio packages.
  apio packages --install                   # Install all missing packages.
  apio packages --install --force           # Re/install all missing packages.
  apio packages --install oss-cad-suite     # Install a specific package.
  apio packages --install examples@0.0.32   # Install a specific version.
  apio packages --uninstall                 # Uninstall all packages.
  apio packages --uninstall oss-cad-suite   # Uninstall only given package(s).
  apio packages --fix                       # Fix package errors.

Adding --force to --install forces the reinstallation of existing packages,
otherwise, packages that are already installed correctly are left with no
change.

[Hint] In case of doubt, run 'apio packages --install --force' to reinstall
all packages from scratch.
"""

install_option = click.option(
    "install",  # Var name.
    "-i",
    "--install",
    is_flag=True,
    help="Install packages.",
    cls=cmd_util.ApioOption,
)

uninstall_option = click.option(
    "uninstall",  # Var name.
    "-u",
    "--uninstall",
    is_flag=True,
    help="Uninstall packages.",
    cls=cmd_util.ApioOption,
)

fix_option = click.option(
    "fix",  # Var name.
    "--fix",
    is_flag=True,
    help="Fix package errors.",
    cls=cmd_util.ApioOption,
)


# pylint: disable=duplicate-code
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "install",
    short_help="Manage the apio packages.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("packages", nargs=-1, required=False)
@options.list_option_gen(help="List packages.")
@install_option
@uninstall_option
@fix_option
@options.force_option_gen(help="Force installation.")
@options.project_dir_option
@options.sayyes
@options.verbose_option
def cli(
    ctx: Context,
    # Arguments
    packages: Tuple[str],
    # Options
    list_: bool,
    install: bool,
    uninstall: bool,
    fix: bool,
    force: bool,
    project_dir: Path,
    sayyes: bool,
    verbose: bool,
):
    """Implements the packages command which allows to manage the
    apio packages.
    """

    # Validate the option combination.
    cmd_util.check_exactly_one_param(
        ctx, nameof(list_, install, uninstall, fix)
    )
    cmd_util.check_at_most_one_param(ctx, nameof(list_, force))
    cmd_util.check_at_most_one_param(ctx, nameof(uninstall, force))
    cmd_util.check_at_most_one_param(ctx, nameof(fix, force))
    cmd_util.check_at_most_one_param(ctx, nameof(list_, packages))
    cmd_util.check_at_most_one_param(ctx, nameof(fix, packages))

    # -- Load the resources. We don't care about project specific resources.
    resources = Resources(
        project_dir=project_dir,
        project_scope=False,
    )

    if install:
        exit_code = _install(resources, packages, force, verbose)
        ctx.exit(exit_code)

    if uninstall:
        exit_code = _uninstall(resources, packages, verbose, sayyes)
        ctx.exit(exit_code)

    if fix:
        exit_code = _fix(resources, verbose)
        ctx.exit(exit_code)

    # -- Here it must be --list.
    exit_code = _list(resources, verbose)
    ctx.exit(exit_code)
