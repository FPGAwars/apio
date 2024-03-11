"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import json
from pathlib import Path
from os.path import isdir
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
        """DOC: TODO"""

        # -- If the package is installed...
        if name in self.packages:

            # -- Get the current version
            pkg_version = self.get_package_version(name)

            # pkg_version = self._convert_old_version(pkg_version)
            # version = self._convert_old_version(version)

            return semantic_version.Version(
                pkg_version
            ) == semantic_version.Version(version)
        return None

    @staticmethod
    def _convert_old_version(version):
        # Convert old versions to new format
        try:
            ver = int(version)
            version = f"1.{ver}.0"
        except ValueError:
            pass
        return version

    def check_exe_default(self):
        """DOC: todo"""

        return self.config.get("exe", "") == "default"

    def add_package(self, name, version):
        """DOC: todo"""

        self.packages[name] = {"version": version}

    def add_setting(self, key, value):
        """DOC: todo"""

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

    def remove_package(self, name):
        """DOC: todo"""

        if name in self.packages.keys():
            del self.packages[name]

    def get_verbose_mode(self):
        """DOC: todo"""

        return int(self.config.get("verbose", False))

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def get_package_version(self, name: str, release_name: str = None) -> str:
        """Return the version of the given package"""

        # -- If the package is installed
        if name in self.packages:

            # -- Get the version
            version = self.packages[name]["version"]

            # -- REturn the version
            return version

        version = "0.0.0"

        if release_name:
            dir_name = util.get_package_dir(release_name)
            if isdir(dir_name):
                filepath = str(Path(dir_name) / "package.json")
                try:
                    with open(filepath, "r", encoding="utf8") as json_file:
                        tmp_data = json.load(json_file)
                        if "version" in tmp_data.keys():
                            version = tmp_data.get("version")
                except Exception:
                    pass
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
        """DOC: todo"""

        util.mkdir(self._profile_path)

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
