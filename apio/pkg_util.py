# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Utility functions related to apio packages."""

from typing import List, Callable, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
import os
import sys
import click
import semantic_version
from apio.apio_context import ApioContext
from apio import util


@dataclass(frozen=True)
class EnvMutations:
    """Contains mutations to the system env."""

    # -- PATH items to add.
    paths: List[str]
    # -- Vars name/value paris.
    vars: List[Tuple[str, str]]


@dataclass(frozen=True)
class _PackageDesc:
    """Represents an entry in the packages table."""

    # -- Package folder name. E.g. "tools-oss-cad-suite"
    folder_name: str
    # -- True if the package is available for the current platform.
    platform_match: bool
    # -- A function to set the env for this package.
    env_func: Callable[[Path], EnvMutations]


def _get_env_mutations_for_packages(apio_ctx: ApioContext) -> EnvMutations:
    """Collects the env mutation for each of the defined packages,
    in the order they are defined."""

    result = EnvMutations([], [])
    for _, package_config in apio_ctx.platform_packages.items():
        # -- Get the json 'env' section. We require it, even if it's empty,
        # -- for clarity reasons.
        assert "env" in package_config
        package_env = package_config["env"]

        # -- Collect the path values.
        path_list = package_env.get("path", [])
        result.paths.extend(path_list)

        # -- Collect the env vars (name, value) pairs.
        vars_section = package_env.get("vars", {})
        for var_name, var_value in vars_section.items():
            result.vars.append((var_name, var_value))

    return result


def _dump_env_mutations(
    apio_ctx: ApioContext, mutations: EnvMutations
) -> None:
    """For debugging. Delete once stabalizing the new oss-cad-suite on
    windows."""
    click.secho("Envirnment settings:", fg="magenta")

    # -- Print PATH mutations.
    windows = apio_ctx.is_windows()
    for p in reversed(mutations.paths):
        styled_name = click.style("PATH", fg="magenta")
        if windows:
            click.secho(f"set {styled_name}={p};%PATH%")
        else:
            click.secho(f'{styled_name}="{p}:$PATH"')

    # -- Print vars mutations.
    for name, val in mutations.vars:
        styled_name = click.style(name, fg="magenta")
        if windows:
            click.secho(f"set {styled_name}={val}")
        else:
            click.secho(f'{styled_name}="{val}"')


def _apply_env_mutations(mutations: EnvMutations) -> None:
    """Apply a given set of env mutations, while preserving their order."""

    # -- Apply the path mutations, while preserving order.
    old_val = os.environ["PATH"]
    items = mutations.paths + [old_val]
    new_val = os.pathsep.join(items)
    os.environ["PATH"] = new_val

    # -- Apply the vars mutations, while preserving order.
    for name, value in mutations.vars:
        os.environ[name] = value


# -- A static flag that is used to make sure we set the env only once.
# -- This is to avoid extending the $PATH variable multiple time with the
# -- same directories.
__ENV_ALREADY_SET_FLAG = False


def set_env_for_packages(apio_ctx: ApioContext, verbose: bool = False) -> None:
    """Sets the environment variables for using all the that are
    available for this platform, even if currently not installed.

    The function sets the environment only on first call and in latter calls
    skips the operation silently.
    """

    # -- Collect the env mutations for all packages.
    mutations = _get_env_mutations_for_packages(apio_ctx)

    if verbose:
        _dump_env_mutations(apio_ctx, mutations)

    # -- If this is the first call in this apio invocation, apply the
    # -- mutations. These mutations are temporary for the lifetime of this
    # -- process and does not affect the user's shell environment.
    # -- The mutations are also inheritated by child processes such as the
    # -- scons processes.
    if not apio_ctx.env_was_already_set:
        _apply_env_mutations(mutations)
        apio_ctx.env_was_already_set = True
        if not verbose:
            click.secho("Setting the envinronment.")


def check_required_packages(
    apio_ctx: ApioContext, required_packages_names: List[str]
) -> None:
    """Checks that the packages whose names are in 'packages_names' are
    installed and have a version that meets the requirements. If any error,
    it prints an error message and aborts the program with an error status
    code.
    """

    installed_packages = apio_ctx.profile.packages
    spec_packages = apio_ctx.distribution.get("packages")

    # -- Check packages
    for package_name in required_packages_names:
        # -- Package name must be in all_packages. Otherwise it's a programming
        # -- error.
        if package_name not in apio_ctx.all_packages:
            raise RuntimeError(f"Unknown package named [{package_name}]")

        # -- Skip if packages is not applicable to this platform.
        if package_name not in apio_ctx.platform_packages:
            continue

        # -- The package is applicable to this platform. Check installed
        # -- version, if at all.
        current_version = installed_packages.get(package_name, {}).get(
            "version", None
        )

        # -- Check the installed version against the required version.
        spec_version = spec_packages.get(package_name, "")
        _check_required_package(
            apio_ctx, package_name, current_version, spec_version
        )


def _check_required_package(
    apio_ctx: ApioContext,
    package_name: str,
    current_version: Optional[str],
    spec_version: str,
) -> None:
    """Checks that the package with the given packages is installed and
    has a version that meets the requirements. If any error, it prints an
    error message and exists with an error code.

    'package_name' - the package name, e.g. 'oss-cad-suite'.
    'current_version' - the version of the install package or None if not
        installed.
    'spec_version' - a specification of the required version.
    'apio_ctx' - the apio context.
    """
    # -- Case 1: Package is not installed.
    if current_version is None:
        click.secho(
            f"Error: package '{package_name}' is not installed.", fg="red"
        )
        _show_package_install_instructions(package_name)
        sys.exit(1)

    # -- Case 2: Version does not match requirmeents.
    if not _version_matches(current_version, spec_version):
        click.secho(
            f"Error: package '{package_name}' version {current_version}"
            " does not\n"
            f"match the requirement for version {spec_version}.",
            fg="red",
        )

        _show_package_install_instructions(package_name)
        sys.exit(1)

    # -- Case 3: The package's directory does not exist.
    package_dir = apio_ctx.get_package_dir(package_name)
    if package_dir and not package_dir.is_dir():
        message = f"Error: package '{package_name}' is installed but missing"
        click.secho(message, fg="red")
        _show_package_install_instructions(package_name)
        sys.exit(1)


def _version_matches(current_version: str, spec_version: str) -> bool:
    """Tests if a given version satisfy the semantic version constraints
    * INPUTS:
      - version: Package version (Ex. '0.0.9')
      - spec_version: semantic version constraint (Ex. '>=0.0.1')
    * OUTPUT:
      - True: Version ok!
      - False: Version not ok! or incorrect version number
    """

    # -- Build a semantic version object
    spec = semantic_version.SimpleSpec(spec_version)

    # -- Check it!
    try:
        semver = semantic_version.Version(current_version)

    # -- Incorrect version number
    except ValueError:
        return False

    # -- Check the version (True if the semantic version is satisfied)
    return semver in spec


def _show_package_install_instructions(package_name: str):
    """Prints hints on how to install a package with a given name."""

    click.secho(
        "Please run:\n"
        f"   apio packages --install --force {package_name}\n"
        "or:\n"
        "   apio packages --install --force",
        fg="yellow",
    )


@dataclass
class PackageScanResults:
    """Represents results of packages scan."""

    # -- Normal. Packages in platform_packages that are instaleld properly.
    installed_package_ids: List[str]
    # -- Normal. Packages in platform_packages that are uninstaleld properly.
    uninstalled_package_ids: List[str]
    # -- Error. Packages in platform_packages with broken installation. E.g,
    # -- registered in profile but package directory is missing.
    broken_package_ids: List[str]
    # -- Error. Packages that are marked in profile as registered but are not
    # -- in platform_packages.
    orphan_package_ids: List[str]
    # -- Error. Basenames of directories in packages dir that don't match
    # -- folder_name of packages in platform_packates.
    orphan_dir_names: List[str]
    # -- Error. Basenames of all files in packages directory. That directory is
    # -- expected to contain only directories for packages.a
    orphan_file_names: List[str]

    def num_errors(self) -> bool:
        """Returns the number of errors.."""
        return (
            len(self.broken_package_ids)
            + len(self.orphan_package_ids)
            + len(self.orphan_dir_names)
            + len(self.orphan_file_names)
        )

    def dump(self):
        """Dump the content of this object. For debugging."""
        print("Package scan results:")
        print(f"  Installed    {self.installed_package_ids}")
        print(f"  Uninstalled  {self.uninstalled_package_ids}")
        print(f"  Broken       {self.broken_package_ids}")
        print(f"  Orphan ids   {self.orphan_package_ids}")
        print(f"  Orphan dirs  {self.orphan_dir_names}")
        print(f"  Orphan files {self.orphan_file_names}")


def scan_packages(apio_ctx: ApioContext) -> PackageScanResults:
    """Scans the available and installed packages and returns
    the findings as a PackageScanResults object."""

    # Initialize the result with empty data.
    result = PackageScanResults([], [], [], [], [], [])

    # -- A helper set that we populate with the 'folder_name' values of the
    # -- all the packages for this platform.
    platform_folder_names = set()

    # -- Scan packages ids in platform_packages and populate
    # -- the installed/uninstall/broken packages lists.
    for package_id in apio_ctx.platform_packages.keys():
        # -- Collect package's folder names in a set. For a later use.
        package_folder_name = apio_ctx.get_package_folder_name(package_id)
        platform_folder_names.add(package_folder_name)

        # -- Classify the package as one of three cases.
        in_profile = package_id in apio_ctx.profile.packages
        has_dir = apio_ctx.get_package_dir(package_id).is_dir()
        if in_profile and has_dir:
            result.installed_package_ids.append(package_id)
        elif not in_profile and not has_dir:
            result.uninstalled_package_ids.append(package_id)
        else:
            result.broken_package_ids.append(package_id)

    # -- Scan the packagtes ids that are registered in profile as installed
    # -- the ones that are not platform_packages as orphans.
    for package_id in apio_ctx.profile.packages:
        if package_id not in apio_ctx.platform_packages:
            result.orphan_package_ids.append(package_id)

    # -- Scan the packages directory and identify orphan dirs and files.
    for path in apio_ctx.packages_dir.glob("*"):
        base_name = os.path.basename(path)
        if path.is_dir():
            if base_name not in platform_folder_names:
                result.orphan_dir_names.append(base_name)
        else:
            result.orphan_file_names.append(base_name)

    # -- Return results
    return result


def _list_section(title: str, items: List[List[str]], color: str) -> None:
    """A helper function for printing one serction of list_packages()."""
    # -- Construct horizontal lines at terminal width.
    config = util.get_terminal_config()
    line_width = config.terminal_width if config.terminal_mode() else 80
    line = "─" * line_width
    dline = "═" * line_width

    # -- Print the section.
    click.secho()
    click.secho(dline, fg=color)
    click.secho(title, fg=color, bold=True)
    for item in items:
        click.secho(line)
        for sub_item in item:
            click.secho(sub_item)
    click.secho(dline, fg=color)


def list_packages(apio_ctx: ApioContext, scan: PackageScanResults) -> None:
    """Prints in a user friendly format the results of a packages scan."""

    # -- Shortcuts to reduce clutter.
    get_package_version = apio_ctx.profile.get_package_installed_version
    get_package_info = apio_ctx.get_package_info

    # --Print the installed packages, if any.
    if scan.installed_package_ids:
        items = []
        for package_id in scan.installed_package_ids:
            name = click.style(f"{package_id}", fg="cyan", bold=True)
            version = get_package_version(package_id)
            description = get_package_info(package_id)["description"]
            items.append([f"{name} {version}", f"{description}"])
        _list_section("Installed packages:", items, "green")

    # -- Print the uninstalled packages, if any,
    if scan.uninstalled_package_ids:
        items = []
        for package_id in scan.uninstalled_package_ids:
            name = click.style(f"{package_id}", fg="cyan", bold=True)
            description = get_package_info(package_id)["description"]
            items.append([f"{name}  {description}"])
        _list_section("Available packages (Not installed):", items, "yellow")

    # -- Print the broken packages, if any,
    if scan.broken_package_ids:
        items = []
        for package_id in scan.broken_package_ids:
            name = click.style(f"{package_id}", fg="red", bold=True)
            description = get_package_info(package_id)["description"]
            items.append([f"{name}  {description}"])
        _list_section("[Error] Broken packages:", items, None)

    # -- Print the orphan packages, if any,
    if scan.orphan_package_ids:
        items = []
        for package_id in scan.orphan_package_ids:
            name = click.style(f"{package_id}", fg="red", bold=True)
            items.append([name])
        _list_section("[Error] Unknown packages:", items, None)

    # -- Print orphan directories and files, if any,
    if scan.orphan_dir_names or scan.orphan_file_names:
        items = []
        for name in sorted(scan.orphan_dir_names + scan.orphan_file_names):
            name = click.style(f"{name}", fg="red", bold=True)
            items.append([name])
        _list_section("[Error] Unknown files and directories:", items, None)

    # -- Print an error summary
    if scan.num_errors():
        click.secho(f"Total of {util.plurality(scan.num_errors(), 'error')}")
    else:
        click.secho("No errors.")

    # -- A line seperator. For asthetic reasons.
    click.secho()
