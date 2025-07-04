# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utility functions related to apio packages."""

from typing import List, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
import os
from apio.common.apio_console import cout, cstyle
from apio.common.apio_styles import EMPH3
from apio.apio_context import ApioContext
from apio.utils import util
from apio.profile import PackageRemoteConfig


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
    cout("Environment settings:", style=EMPH3)

    # -- Print PATH mutations.
    windows = apio_ctx.is_windows
    for p in reversed(mutations.paths):
        styled_name = cstyle("PATH", style=EMPH3)
        if windows:
            cout(f"set {styled_name}={p};%PATH%")
        else:
            cout(f'{styled_name}="{p}:$PATH"')

    # -- Print vars mutations.
    for name, val in mutations.vars:
        styled_name = cstyle(name, style=EMPH3)
        if windows:
            cout(f"set {styled_name}={val}")
        else:
            cout(f'{styled_name}="{val}"')


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
    see are executed in a modified env settings.
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
    # -- The mutations are also inherited by child processes such as the
    # -- scons processes.
    if not apio_ctx.env_was_already_set:
        _apply_env_mutations(mutations)
        apio_ctx.env_was_already_set = True
        if not verbose and not quiet:
            cout("Setting shell vars.")


@dataclass
class PackageScanResults:
    """Represents results of packages scan."""

    # -- Normal and Error. Packages in platform_packages that are installed
    # -- regardless if the version matches or not.
    installed_ok_package_names: List[str]
    # -- Error. Packages in platform_packages that are installed but with
    # -- version mismatch.
    bad_version_package_names: List[str]
    # -- Normal. Packages in platform_packages that are uninstalled properly.
    uninstalled_package_names: List[str]
    # -- Error. Packages in platform_packages with broken installation. E.g,
    # -- registered in profile but package directory is missing.
    broken_package_names: List[str]
    # -- Error. Packages that are marked in profile as registered but are not
    # -- in platform_packages.
    orphan_package_names: List[str]
    # -- Error. Basenames of directories in packages dir that don't match
    # -- folder_name of packages in platform_packages.
    orphan_dir_names: List[str]
    # -- Error. Basenames of all files in packages directory. That directory is
    # -- expected to contain only directories for packages.a
    orphan_file_names: List[str]

    def packages_installed_ok(self) -> bool:
        """Returns true if all packages are installed ok, regardless of
        other fixable errors."""
        return (
            len(self.bad_version_package_names) == 0
            and len(self.uninstalled_package_names) == 0
            and len(self.broken_package_names) == 0
        )

    def num_errors_to_fix(self) -> bool:
        """Returns the number of errors that required , having a non installed
        packages is not considered an error that need to be fix."""
        return (
            len(self.bad_version_package_names)
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
        cout()
        cout("Package scan results:")
        cout(f"  Installed     {self.installed_ok_package_names}")
        cout(f"  bad version   {self.bad_version_package_names}")
        cout(f"  Uninstalled   {self.uninstalled_package_names}")
        cout(f"  Broken        {self.broken_package_names}")
        cout(f"  Orphan ids    {self.orphan_package_names}")
        cout(f"  Orphan dirs   {self.orphan_dir_names}")
        cout(f"  Orphan files  {self.orphan_file_names}")


def package_version_ok(
    apio_ctx: ApioContext,
    package_name: str,
) -> bool:
    """Return true if the package is both in profile and platform packages
    and its version in the profile meet the requirements in the
    config.jsonc file. Otherwise return false."""

    # If this package is not applicable to this platform, return False.
    if package_name not in apio_ctx.platform_packages:
        return False

    # -- If the current version is not available, the package is not installed.
    current_ver, package_platform_id = (
        apio_ctx.profile.get_package_installed_info(package_name)
    )
    if not current_ver or package_platform_id != apio_ctx.platform_id:
        return False

    # -- Get the package remote config.
    package_config: PackageRemoteConfig = apio_ctx.profile.get_package_config(
        package_name
    )

    # -- Compare to the required version. We expect the two version to be
    # -- normalized and ths a string comparison is sufficient.
    return current_ver == package_config.release_version


def scan_packages(apio_ctx: ApioContext) -> PackageScanResults:
    """Scans the available and installed packages and returns
    the findings as a PackageScanResults object."""

    # pylint: disable=too-many-branches

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

        # -- Classify the package as one of four cases.
        in_profile = package_name in apio_ctx.profile.installed_packages
        has_dir = apio_ctx.get_package_dir(package_name).is_dir()
        version_ok = package_version_ok(apio_ctx, package_name)
        if in_profile and has_dir:
            if version_ok:
                # Case 1: Package installed ok.
                result.installed_ok_package_names.append(package_name)
            else:
                # -- Case 2: Package installed but version mismatch.
                result.bad_version_package_names.append(package_name)
        elif not in_profile and not has_dir:
            # -- Case 3: Package not installed.
            result.uninstalled_package_names.append(package_name)
        else:
            # -- Case 4: Package is broken.
            result.broken_package_names.append(package_name)

    # -- Scan the packages ids that are registered in profile as installed
    # -- the ones that are not platform_packages as orphans.
    for package_name in apio_ctx.profile.installed_packages:
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
    if util.is_debug(1):
        result.dump()

    return result
