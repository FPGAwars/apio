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

from typing import List, Callable, Dict
from pathlib import Path
import os
import platform
from dataclasses import dataclass
import click
import semantic_version
from apio import util
from apio.profile import Profile
from apio.resources import Resources


def _add_env_path(path: Path) -> None:
    """Prepends given path to env PATH variable. Not checking for dupes."""
    print(f"  * Adding path: {path}")
    old_val = os.environ["PATH"]
    new_val = os.pathsep.join([str(path), old_val])
    os.environ["PATH"] = new_val


def _set_env_var(name: str, value: str) -> None:
    """Sets env var to given value."""
    print(f"  * Setting env: {name} = {value}")
    os.environ[name] = value


def _set_oss_cad_package_env(package_path: Path) -> None:
    """Sets the environment variasbles for the oss-cad-suite package."""

    _add_env_path(package_path / "bin")
    _add_env_path(package_path / "lib")
    _add_env_path(package_path / "libexec")

    _set_env_var("IVL", str(package_path / "lib" / "ivl"))
    _set_env_var("ICEBOX", str(package_path / "share" / "icebox"))
    _set_env_var("TRELLIS", str(package_path / "share" / "trellis"))
    _set_env_var("YOSYS_LIB", str(package_path / "share" / "yosys"))


def _set_examples_package_env(_: Path) -> None:
    """Sets the environment variasbles for the examples package."""
    # -- Nothing to set here.


def _set_gtkwave_package_env(package_path: Path) -> None:
    """Sets the environment variasbles for the gtkwave package."""
    _add_env_path(package_path / "bin")


def _set_drivers_package_env(package_path: Path) -> None:
    """Sets the environment variasbles for the drivers package."""
    _add_env_path(package_path / "bin")


@dataclass(frozen=True)
class _PackageDesc:
    """Represents an entry in the packages table."""

    # -- Package folder name. E.g. "tools-oss-cad-suite"
    folder_name: str
    # -- True if the package is available for this platform.
    platform_match: bool
    # -- A function to set the env for this package.
    env_setting_func: Callable[[Path], None]


# -- Package names to package properties. Using lambda as a workaround for
# -- forward reference to the env functions.
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
    """Sets the environment variables for using the packages."""
    # print(f"*** set_env_for_packages()")
    # base_path = get_packages_dir()
    for package_name, package_desc in _PACKAGES.items():
        if package_desc.platform_match:
            print(f"*** Setting env for package: {package_name}")
            package_path = get_package_dir(package_name)
            package_desc.env_setting_func(package_path)


def check_packages(packages_names: List[str], resources: Resources) -> None:
    """Tesks if the given packages have proper versions installed.
    Returns True if OK.
    """

    profile = Profile()
    installed_packages = profile.packages
    spec_packages = resources.distribution.get("packages")

    # -- Check packages
    check = True
    for package_name in packages_names:
        package_desc = _PACKAGES[package_name]
        if package_desc.platform_match:
            version = installed_packages.get(package_name, {}).get(
                "version", ""
            )
            spec_version = spec_packages.get(package_name, "")

            _bin = get_package_dir(package_name) / "bin"

            # -- Check this package
            check &= check_package(package_name, version, spec_version, _bin)

    return check


def check_package(
    name: str, version: str, spec_version: str, path: Path
) -> bool:
    """Check if the given package is ok
       (and can be installed without problems)
    * INPUTS:
      - name: Package name
      - version: Package version
      - spec_version: semantic version constraint
      - path: path where the binary files of the package are stored

    * OUTPUT:
      - True: Package
    """

    # Check package path
    if path and not path.is_dir():
        show_package_path_error(name)
        show_package_install_instructions(name)
        return False

    # Check package version
    if not _check_package_version(version, spec_version):
        _show_package_version_error(name, version, spec_version)
        show_package_install_instructions(name)
        return False

    return True


def _check_package_version(version: str, spec_version: str) -> bool:
    """Check if a given version satisfy the semantic version constraints
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
        semver = semantic_version.Version(version)

    # -- Incorrect version number
    except ValueError:
        return False

    # -- Check the version (True if the semantic version is satisfied)
    return semver in spec


def _show_package_version_error(
    name: str, current_version: str, spec_version: str
):
    """Print error message: a package is missing or has a worng version."""

    if current_version:
        message = (
            (
                f"Error: package '{name}' version {current_version} does not\n"
                f"match the requirement for version {spec_version}."
            ),
        )

    else:
        message = f"Error: package '{name}' is missing."
    click.secho(message, fg="red")


def show_package_path_error(name: str):
    """Display an error: package Not installed
    * INPUTs:
      - name: Package name
    """

    message = f"Error: package '{name}' is not installed"
    click.secho(message, fg="red")


def show_package_install_instructions(name: str):
    """Print the package install instructions
    * INPUTs:
      - name: Package name
    """

    click.secho(f"Please run:\n   apio install {name}", fg="yellow")


def get_package_version(name: str, profile: dict) -> str:
    """Get the version of a given package
    * INPUTs:
      - name: Package name
      - profile: Dictrionary with the profile information
    * OUTPUT:
      - The version (Ex. '0.0.9')
    """

    # -- Default version
    version = ""

    # -- Check if the package is intalled
    if name in profile.packages:
        version = profile.packages[name]["version"]

    # -- Return the version
    return version


def get_package_spec_version(name: str, resources: dict) -> str:
    """Get the version restrictions for a given package
    * INPUTs:
      * name: Package name
      * resources: Apio resources object
    * OUTPUT: version restrictions for that package
      Ex. '>=1.1.0,<1.2.0'
    """

    # -- No restrictions by default
    spec_version = ""

    # -- Check that the package is valid
    if name in resources.distribution["packages"]:

        # -- Get the package restrictions
        spec_version = resources.distribution["packages"][name]

    # -- Return the restriction
    return spec_version


def get_packages_dir() -> Path:
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
    package_dir = get_packages_dir() / package_folder

    return package_dir
