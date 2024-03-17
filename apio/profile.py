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
from apio import util


class Profile:
    """Class for managing the apio profile file
    ex. /home/obijuan/.apio/profile.json
    """

    def __init__(self):

        # ---- Set the default parameters
        # -- Apio default config mode
        self.config = {"exe": "default", "verbose": 0}

        self.labels = {"exe": "Executable", "verbose": "Verbose"}

        # Apio settings
        self.settings = {}

        # -- Installed package versions
        self.packages = {}

        # -- Get the profile path
        # -- Ex. '/home/obijuan/.apio'
        self._profile_path = util.get_home_dir() / "profile.json"

        # print(f"(DEBUG) Profile path: {self._profile_path}")
        # print(f"(DEBUG) Home_dir: {util.get_home_dir()}")

        # -- Read the profile from file
        self.load()

    def installed_version(self, name: str, version: str):
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
            pkg_version = self.get_package_version(name)

            # -- Compare versions: current vs version to install
            current_ver = semantic_version.Version(pkg_version)
            to_install_ver = semantic_version.Version(version)

            same_versions = current_ver == to_install_ver

            # -- Return the state of the installed package:
            # -- True: Package installed (with the given version)
            # -- False: Package installed (but different version)
            return same_versions

        # -- Package not installed
        return False

    def check_exe_default(self) -> bool:
        """Check if the exe mode is 'default'"""

        is_exe_default = self.config["exe"] == "default"

        return is_exe_default

    def add_package(self, name: str, version: str):
        """Add a package to the profile class"""

        self.packages[name] = {"version": version}

    def add_setting(self, key: str, value: str):
        """Add one key,value pair in the settings"""

        self.settings[key] = value

    def add_config(self, key: str, value: str):
        """Add/modify a configuration value"""

        # -- Update the config value if it is different
        if self.config[key] != value:

            # -- Update config value
            self.config[key] = value

            # -- Update it in the profile file
            self.save()

            # -- Inform the user
            click.secho(
                f"{self.labels[key]} mode updated: {value}",
                fg="green",
            )

        # -- The same value is given
        else:
            click.secho(
                f"{self.labels[key]} mode already {value}",
                fg="yellow",
            )

    def remove_package(self, name: str):
        """Remove a package from the profile file"""

        if name in self.packages.keys():
            del self.packages[name]

    def get_verbose_mode(self) -> int:
        """Get the verbose mode"""

        return int(self.config["verbose"], False)

    def get_package_version(self, name: str) -> str:
        """Return the version of the given package"""

        # -- If the package is installed
        if name in self.packages:

            # -- Get the version
            version = self.packages[name]["version"]

        else:
            version = "0.0.0"

        return version

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

        # -- Add the configuration object
        if "config" in data.keys():
            self.config = data["config"]

            if "exe" not in self.config.keys():
                self.config["exe"] = "default"

            if "verbose" not in self.config.keys():
                self.config["verbose"] = 0

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
                "config": self.config,
                "settings": self.settings,
                "packages": self.packages,
            }
            json.dump(data, profile, indent=4, sort_keys=True)

    def list(self):
        """Print configuration parameters on the console"""

        # -- Go through all the config parameters
        for key in self.config:

            # -- Print the parameter
            click.secho(
                f"{self.labels[key]} mode: {self.config[key]}",
                fg="yellow",
            )
        print()
