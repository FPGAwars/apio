# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Manage the apio profile file"""

import json
from pathlib import Path
import click
import semantic_version


class Profile:
    """Class for managing the apio profile file
    ex. ~/.apio/profile.json
    """

    def __init__(self, home_dir: Path):

        # ---- Set the default parameters
        # Apio settings
        self.settings = {}

        # -- Installed package versions
        self.packages = {}

        # -- Get the profile path
        # -- Ex. '/home/obijuan/.apio'
        self._profile_path = home_dir / "profile.json"

        # -- Read the profile from file
        self.load()

    def is_installed_version_ok(self, name: str, version: str, verbose: bool):
        """Check the if the given package version is installed
        * INPUT:
          - name: Package name
          - version: Version to install
        * OUTPUT:
          - True: Version installed, with the given version
          - False:
            - Package not installed
            - Package installed but different version
        """

        # -- If the package is installed...
        if name in self.packages:

            # -- Get the current version
            pkg_version = self.get_package_installed_version(name)

            # -- Compare versions: current vs version to install
            current_ver = semantic_version.Version(pkg_version)
            to_install_ver = semantic_version.Version(version)

            if verbose:
                click.secho(f"Current version: {current_ver}")

            same_versions = current_ver == to_install_ver

            # -- Return the state of the installed package:
            # -- True: Package installed (with the given version)
            # -- False: Package installed (but different version)
            return same_versions

        # -- Package not installed
        return False

    def add_package(self, name: str, version: str):
        """Add a package to the profile class"""

        self.packages[name] = {"version": version}

    def add_setting(self, key: str, value: str):
        """Add one key,value pair in the settings"""

        self.settings[key] = value

    def remove_package(self, name: str):
        """Remove a package from the profile file"""

        if name in self.packages.keys():
            del self.packages[name]

    def get_package_installed_version(
        self, package_name: str, default="0.0.0"
    ) -> str:
        """Return the installed version of the given package of default if
        not installed."""

        # -- If package is installed, return the installed version.
        if package_name in self.packages:
            return self.packages[package_name]["version"]

        # -- Else, return the default value.
        return default

    def load(self):
        """Load the profile from the file"""

        # -- Check if the file exist
        if self._profile_path.exists():

            # -- Open the profile file
            with open(self._profile_path, "r", encoding="utf8") as profile:

                # -- Read the profile file
                self._load_profile(profile)

    def _load_profile(self, profile: Path):
        """Read the profile file
        profile: Profile path (Ex. /home/obijuan/.apio/profile.json)
        """

        # -- Process the json file
        data = json.load(profile)

        # -- Add the settings object
        if "settings" in data.keys():
            self.settings = data["settings"]

        # -- Add the packages version object
        if "packages" in data.keys():
            self.packages = data["packages"]

        else:
            self.packages = data  # Backward compatibility

    def save(self):
        """Save the profile file"""

        # -- Create the profile folder, if it does not exist yet
        path = self._profile_path.parent
        if not path.exists():
            path.mkdir()

        with open(self._profile_path, "w", encoding="utf8") as profile:
            data = {
                "settings": self.settings,
                "packages": self.packages,
            }
            json.dump(data, profile, indent=4, sort_keys=True)
