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

from typing import List, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
import os
import click
from click import secho
from apio.apio_context import ApioContext
from apio.utils import util


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
    """Dumps a user friendly representation of the env mutations."""
    secho("Envirnment settings:", fg="magenta")

    # -- Print PATH mutations.
    windows = apio_ctx.is_windows()
    for p in reversed(mutations.paths):
        styled_name = click.style("PATH", fg="magenta")
        if windows:
            secho(f"set {styled_name}={p};%PATH%")
        else:
            secho(f'{styled_name}="{p}:$PATH"')

    # -- Print vars mutations.
    for name, val in mutations.vars:
        styled_name = click.style(name, fg="magenta")
        if windows:
            secho(f"set {styled_name}={val}")
        else:
            secho(f'{styled_name}="{val}"')


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


def set_env_for_packages(
    apio_ctx: ApioContext, *, quiet: bool = False, verbose: bool = False
) -> None:
    """Sets the environment variables for using all the that are
    available for this platform, even if currently not installed.

    The function sets the environment only on first call and in latter calls
    skips the operation silently.

    If quite is set, no output is printed. When verbose is set, additional
    output such as the env vars mutations are printed, otherwise, a minimal
    information is printed to make the user aware that they commands they
    see are exectuted in a modified env settings.
    """

    # -- If this fails, this is a programming error. Quiet and verbose
    # -- cannot be combined.
    assert not (quiet and verbose), "Can't have both quite and verbose."

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
        if not verbose and not quiet:
            secho("Setting the envinronment.")


@dataclass
class PackageScanResults:
    """Represents results of packages scan."""

    # -- Normal and Error. Packages in platform_packages that are installed
    # -- regardless if the versin matches or not.
    installed_package_names: List[str]
    # -- Error. The subset of installed_package_names that have version
    # -- mismatch.
    bad_version_package_names_subset: List[str]
    # -- Normal. Packages in platform_packages that are uninstaleld properly.
    uninstalled_package_names: List[str]
    # -- Error. Packages in platform_packages with broken installation. E.g,
    # -- registered in profile but package directory is missing.
    broken_package_names: List[str]
    # -- Error. Packages that are marked in profile as registered but are not
    # -- in platform_packages.
    orphan_package_names: List[str]
    # -- Error. Basenames of directories in packages dir that don't match
    # -- folder_name of packages in platform_packates.
    orphan_dir_names: List[str]
    # -- Error. Basenames of all files in packages directory. That directory is
    # -- expected to contain only directories for packages.a
    orphan_file_names: List[str]

    def num_errors_to_fix(self) -> bool:
        """Returns the number of errors that required , having a non installed
        packages is not considered an error that need to be fix."""
        return (
            len(self.bad_version_package_names_subset)
            + len(self.broken_package_names)
            + len(self.orphan_package_names)
            + len(self.orphan_dir_names)
            + len(self.orphan_file_names)
        )

    def is_all_ok(self) -> bool:
        """Return True if all packages are installed properly with no
        issues."""
        return (
            not self.num_errors_to_fix() and not self.uninstalled_package_names
        )

    def dump(self):
        """Dump the content of this object. For debugging."""
        print("Package scan results:")
        print(f"  Installed     {self.installed_package_names}")
        print(f"  bad version   {self.bad_version_package_names_subset}")
        print(f"  Uninstalled   {self.uninstalled_package_names}")
        print(f"  Broken        {self.broken_package_names}")
        print(f"  Orphan ids    {self.orphan_package_names}")
        print(f"  Orphan dirs   {self.orphan_dir_names}")
        print(f"  Orphan files  {self.orphan_file_names}")


def package_version_ok(
    apio_ctx: ApioContext,
    package_name: str,
    *,
    cached_config_ok: bool,
    verbose: bool,
) -> bool:
    """Return true if the packagea is both in profile and plagrom packages
    and its version in the provile meet the requirements in the
    distribution.json file. Otherwise return false."""

    # If this package is not applicable to this platform, return False.
    if package_name not in apio_ctx.platform_packages:
        return False

    # -- If the current version is not available, the package is not installed.
    current_ver = apio_ctx.profile.get_package_installed_version(
        package_name, None
    )
    if not current_ver:
        return False

    # -- Get the required version from the remote config.
    remote_ver = apio_ctx.profile.get_package_required_version(
        package_name, cached_config_ok=cached_config_ok, verbose=verbose
    )

    # -- Compare. We expect the two version to be nomalized and ths a string
    # -- comparison is sufficient.
    return current_ver == remote_ver


def scan_packages(
    apio_ctx: ApioContext, *, cached_config_ok: bool, verbose: bool
) -> PackageScanResults:
    """Scans the available and installed packages and returns
    the findings as a PackageScanResults object."""

    # Initialize the result with empty data.
    result = PackageScanResults([], [], [], [], [], [], [])

    # -- A helper set that we populate with the 'folder_name' values of the
    # -- all the packages for this platform.
    platform_folder_names = set()

    # -- Scan packages ids in platform_packages and populate
    # -- the installed/uninstall/broken packages lists.
    for package_name in apio_ctx.platform_packages.keys():
        # -- Collect package's folder names in a set. For a later use.
        platform_folder_names.add(package_name)

        # -- Classify the package as one of three cases.
        in_profile = package_name in apio_ctx.profile.packages
        has_dir = apio_ctx.get_package_dir(package_name).is_dir()
        version_ok = package_version_ok(
            apio_ctx,
            package_name,
            cached_config_ok=cached_config_ok,
            verbose=verbose,
        )
        if in_profile and has_dir:
            result.installed_package_names.append(package_name)
            if not version_ok:
                # -- The subset of installed_package_namess that has bad
                # -- version.
                result.bad_version_package_names_subset.append(package_name)
        elif not in_profile and not has_dir:
            result.uninstalled_package_names.append(package_name)
        else:
            result.broken_package_names.append(package_name)

    # -- Scan the packagtes ids that are registered in profile as installed
    # -- the ones that are not platform_packages as orphans.
    for package_name in apio_ctx.profile.packages:
        if package_name not in apio_ctx.platform_packages:
            result.orphan_package_names.append(package_name)

    # -- Scan the packages directory and identify orphan dirs and files.
    for path in apio_ctx.packages_dir.glob("*"):
        base_name = os.path.basename(path)
        if path.is_dir():
            if base_name not in platform_folder_names:
                result.orphan_dir_names.append(base_name)
        else:
            result.orphan_file_names.append(base_name)

    # -- Return results
    if util.is_debug():
        result.dump()

    return result


def _list_section(title: str, items: List[List[str]], color: str) -> None:
    """A helper function for printing one serction of list_packages()."""
    # -- Construct horizontal lines at terminal width.
    config = util.get_terminal_config()
    line_width = config.terminal_width if config.terminal_mode() else 80
    line = "─" * line_width
    dline = "═" * line_width

    # -- Print the section.
    secho()
    secho(dline, fg=color)
    secho(title, fg=color, bold=True)
    for item in items:
        secho(line)
        for sub_item in item:
            secho(sub_item)
    secho(dline, fg=color)


# pylint: disable=too-many-branches
def list_packages(apio_ctx: ApioContext, scan: PackageScanResults) -> None:
    """Prints in a user friendly format the results of a packages scan."""

    # -- Shortcuts to reduce clutter.
    get_package_version = apio_ctx.profile.get_package_installed_version
    get_package_info = apio_ctx.get_package_info

    # --Print the installed packages, if any.
    if scan.installed_package_names:
        items = []
        for package_name in scan.installed_package_names:
            name = click.style(f"{package_name}", fg="cyan", bold=True)
            version = get_package_version(package_name)
            if package_name in scan.bad_version_package_names_subset:
                note = click.style(" [Wrong version]", fg="red", bold=True)
            else:
                note = ""
            description = get_package_info(package_name)["description"]
            items.append([f"{name} {version}{note}", f"{description}"])
        _list_section("Installed packages:", items, "green")

    # -- Print the uninstalled packages, if any,
    if scan.uninstalled_package_names:
        items = []
        for package_name in scan.uninstalled_package_names:
            name = click.style(f"{package_name}", fg="cyan", bold=True)
            description = get_package_info(package_name)["description"]
            items.append([f"{name}  {description}"])
        _list_section("Uinstalled packages:", items, "yellow")

    # -- Print the broken packages, if any,
    if scan.broken_package_names:
        items = []
        for package_name in scan.broken_package_names:
            name = click.style(f"{package_name}", fg="red", bold=True)
            description = get_package_info(package_name)["description"]
            items.append([f"{name}  {description}"])
        _list_section("[Error] Broken packages:", items, None)

    # -- Print the orphan packages, if any,
    if scan.orphan_package_names:
        items = []
        for package_name in scan.orphan_package_names:
            name = click.style(f"{package_name}", fg="red", bold=True)
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
    if scan.num_errors_to_fix():
        secho(f"Total of {util.plurality(scan.num_errors_to_fix(), 'error')}")

    # -- A line seperator. For asthetic reasons.
    secho()
