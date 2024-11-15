# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio packages' command"""

from pathlib import Path
from typing import Tuple
from varname import nameof
import click
from click.core import Context
from apio.managers.installer import Installer
from apio.resources import Resources
from apio import cmd_util
from apio.commands import options


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _install(
    packages: list,
    resources: Resources,
    force: bool,
    verbose: bool,
):
    """Install the apio packages passed as a list
    * INPUTS:
      - packages: List of packages (Ex. ['examples', 'oss-cad-suite'])
      - platform: Specific platform (Advanced, just for developers)
      - force: Force package installation
      - verbose: Show detailed output.
    """
    # -- Install packages, one by one...
    for package in packages:

        # -- The instalation is performed by the Installer object
        modifiers = Installer.Modifiers(
            force=force, checkversion=True, verbose=verbose
        )
        installer = Installer(package, resources, modifiers)

        # -- Install the package!
        installer.install()


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _uninstall(packages: list, resources: Resources, sayyes, verbose: bool):
    """Uninstall the given list of packages"""

    # -- Ask the user for confirmation
    num_packages = (
        "1 package" if len(packages) == 1 else f"{len(packages)} packages"
    )
    if sayyes or click.confirm(f"Do you want to uninstall {num_packages}?"):

        # -- Uninstall packages, one by one
        for package in packages:

            # -- The uninstalation is performed by the Installer object
            modifiers = Installer.Modifiers(
                force=False, checkversion=False, verbose=verbose
            )
            installer = Installer(package, resources, modifiers)

            # -- Uninstall the package!
            installer.uninstall()

    # -- User quit!
    else:
        click.secho("Abort!", fg="red")


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

Adding --force to --install forces the reinstallation of existing packages,
otherwise, packages that are already installed correctly are left with no
change.

[Hint] In case of doubt, run 'apio packages --install --force' to reinstall
all packages from scratch.
"""

install_option = click.option(
    "install",  # Var name. Deconflicting from Python'g builtin 'all'.
    "-i",
    "--install",
    is_flag=True,
    help="Install packages.",
    cls=cmd_util.ApioOption,
)

uninstall_option = click.option(
    "uninstall",  # Var name. Deconflicting from Python'g builtin 'all'.
    "-u",
    "--uninstall",
    is_flag=True,
    help="Uninstall packages.",
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
@options.force_option_gen(help="Force installation.")
@options.project_dir_option
@options.platform_option
@options.sayyes
@options.verbose_option
def cli(
    ctx: Context,
    # Arguments
    packages: Tuple[str],
    # Options
    list_: bool,
    install,
    uninstall,
    force: bool,
    platform: str,
    project_dir: Path,
    sayyes: bool,
    verbose: bool,
):
    """Implements the packages command which allows to manage the
    apio packages.
    """

    # Validate the option combination.
    cmd_util.check_exactly_one_param(ctx, nameof(list_, install, uninstall))
    cmd_util.check_at_most_one_param(ctx, nameof(list_, force))
    cmd_util.check_at_most_one_param(ctx, nameof(uninstall, force))
    cmd_util.check_at_most_one_param(ctx, nameof(list_, packages))

    # -- Load the resources. We don't care about project specific resources.
    resources = Resources(
        platform_id_override=platform,
        project_dir=project_dir,
        project_scope=False,
    )

    # -- List all the packages (installed or not)

    if install:
        # -- If packages not specified, use all.
        if not packages:
            packages = resources.platform_packages
        # -- Install the packages.
        _install(packages, resources, force, verbose)
        ctx.exit(0)

    if uninstall:
        # -- If packages not specified, use all.
        if not packages:
            packages = resources.platform_packages
        _uninstall(packages, resources, sayyes, verbose)
        ctx.exit(0)

    # -- Here it must be --list.
    resources.list_packages()
    ctx.exit(0)
