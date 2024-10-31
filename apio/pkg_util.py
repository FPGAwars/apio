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

from typing import List, Callable, Dict, Optional
from pathlib import Path
import os
import sys
import platform
from dataclasses import dataclass
import click
import semantic_version
from apio import util
from apio.profile import Profile
from apio.resources import Resources


def _add_env_path(path: Path) -> None:
    """Prepends to given path to env variable PATH. Does not check for
    duplicates."""
    # print(f"  * Adding path: {path}")
    old_val = os.environ["PATH"]
    new_val = os.pathsep.join([str(path), old_val])
    os.environ["PATH"] = new_val


def _set_env_var(name: str, value: str) -> None:
    """Sets the env var with given name to given value."""
    # print(f"  * Setting env: {name} = {value}")
    os.environ[name] = value


def _set_oss_cad_package_env(package_path: Path) -> None:
    """Sets the environment variasbles for using the oss-cad-suite package."""

    _add_env_path(package_path / "bin")
    _add_env_path(package_path / "lib")

    _set_env_var("IVL", str(package_path / "lib" / "ivl"))
    _set_env_var("ICEBOX", str(package_path / "share" / "icebox"))
    _set_env_var("TRELLIS", str(package_path / "share" / "trellis"))
    _set_env_var("YOSYS_LIB", str(package_path / "share" / "yosys"))


def _set_examples_package_env(_: Path) -> None:
    """Sets the environment variasbles for using the examples package."""
    # -- Nothing to set here.


def _set_gtkwave_package_env(package_path: Path) -> None:
    """Sets the environment variasbles for using the gtkwave package.
    Called only on Windows, where this package is available.
    """
    _add_env_path(package_path / "bin")


def _set_drivers_package_env(package_path: Path) -> None:
    """Sets the environment variasbles for the drivers package.
    Called only on Windows, where this package is available.
    """
    _add_env_path(package_path / "bin")


@dataclass(frozen=True)
class _PackageDesc:
    """Represents an entry in the packages table."""

    # -- Package folder name. E.g. "tools-oss-cad-suite"
    folder_name: str
    # -- True if the package is available for the current platform.
    platform_match: bool
    # -- A function to set the env for this package.
    env_setting_func: Callable[[Path], None]


# pylint: disable=fixme
# -- TODO: Harmonize this table with the packages.json resource file.
# --   currently they are updated independent, with some overlap.
# --
# -- A dictionary that maps package names to package entries.
_PACKAGES: Dict[str, _PackageDesc] = {
    "oss-cad-suite": _PackageDesc(
        folder_name="tools-oss-cad-suite",
        platform_match=True,
        env_setting_func=_set_oss_cad_package_env,
    ),
    "examples": _PackageDesc(
        folder_name="examples",
        platform_match=True,
        env_setting_func=_set_examples_package_env,
    ),
    "gtkwave": _PackageDesc(
        folder_name="tool-gtkwave",
        platform_match=platform.system() == "Windows",
        env_setting_func=_set_gtkwave_package_env,
    ),
    "drivers": _PackageDesc(
        folder_name="tools-drivers",
        platform_match=platform.system() == "Windows",
        env_setting_func=_set_drivers_package_env,
    ),
}


def set_env_for_packages() -> None:
    """Sets the environment variables for using all the that are
    available for this platform, even if currently not installed.
    """
    for package_name, package_desc in _PACKAGES.items():
        if package_desc.platform_match:
            # print(f"*** Setting env for package: {package_name}")
            package_path = get_package_dir(package_name)
            package_desc.env_setting_func(package_path)


def check_required_packages(
    required_packages_names: List[str], resources: Resources
) -> None:
    """Checks that the packages whose names are in 'packages_names' are
    installed and have a version that meets the requirements. If any error,
    it prints an error message and aborts the program with an error status
    code.
    """

    profile = Profile()
    installed_packages = profile.packages
    spec_packages = resources.distribution.get("packages")

    # -- Check packages
    for package_name in required_packages_names:
        package_desc = _PACKAGES[package_name]
        if package_desc.platform_match:
            current_version = installed_packages.get(package_name, {}).get(
                "version", None
            )
            spec_version = spec_packages.get(package_name, "")
            _check_required_package(
                package_name, current_version, spec_version
            )


def _check_required_package(
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
    package_dir = get_package_dir(package_name)
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
        f"   apio install {package_name} --force\n"
        "or:\n"
        "   apio install --all --force",
        fg="yellow",
    )


def _get_packages_dir() -> Path:
    """Return the base directory of apio packages.
    Packages are installed in the following folder:
      * Default: $APIO_HOME_DIR/packages
      * $APIO_PKG_DIR/packages: if the APIO_PKG_DIR env variable is set
      * INPUT:
        - pkg_name: Package name (Ex. 'examples')
      * OUTPUT:
        - The package folder (PosixPath)
           (Ex. '/home/obijuan/.apio/packages/examples'))
        - or None if the packageis not installed
    """

    # -- Get the apio home dir:
    # -- Ex. '/home/obijuan/.apio'
    apio_home_dir = util.get_home_dir()

    # -- Get the APIO_PKG_DIR env variable
    # -- It returns None if it was not defined
    apio_pkg_dir_env = util.get_projconf_option_dir("pkg_dir")

    # -- Get the pkg base dir. It is what the APIO_PKG_DIR env variable
    # -- says, or the default folder if None
    if apio_pkg_dir_env:
        pkg_home_dir = Path(apio_pkg_dir_env)

    # -- Default value
    else:
        pkg_home_dir = apio_home_dir

    # -- Create the package folder
    # -- Ex '/home/obijuan/.apio/packages/tools-oss-cad-suite'
    package_dir = pkg_home_dir / "packages"

    # -- Return the folder if it exists
    # if package_dir.exists():
    return package_dir


def get_package_dir(package_name: str) -> Path:
    """Return the APIO package dir of a given package
    Packages are installed in the following folder:
      * Default: $APIO_HOME_DIR/packages
      * $APIO_PKG_DIR/packages: if the APIO_PKG_DIR env variable is set
      * INPUT:
        - pkg_name: Package name (Ex. 'examples')
      * OUTPUT:
        - The package folder (PosixPath)
           (Ex. '/home/obijuan/.apio/packages/examples'))
        - or None if the packageis not installed
    """

    package_folder = _PACKAGES[package_name].folder_name
    package_dir = _get_packages_dir() / package_folder

    return package_dir
