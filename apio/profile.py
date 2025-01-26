# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Manage the apio profile file"""

import json
import sys
from typing import Union, Any, Dict
from pathlib import Path
import click
import requests
from apio.common import apio_console
from apio.common.apio_console import cout, cerror, cprint
from apio.utils import util


class Profile:
    """Class for managing the apio profile file
    ex. ~/.apio/profile.json
    """

    def __init__(self, home_dir: Path, remote_config_url_template: str):
        """remote_config_url_template is a url string with a "%V"
        placeholder for the apio version such as "0.9.6."""

        # -- Resolve and cache the remote config url. We replace any %V with
        # -- the apio version such as "0.9.6".
        self.remote_config_url = remote_config_url_template.replace(
            "%V", util.get_apio_version()
        )

        # -- Verify that we resolved all the placeholders.
        assert "%" not in self.remote_config_url, self.remote_config_url

        if util.is_debug():
            print(f"Remote config url: {self.remote_config_url}")

        # ---- Set the default parameters

        # User preferences
        self.preferences = {}

        # Apio settings
        self.settings = {}

        # -- Installed package versions
        self.packages = {}

        # -- A copy of remote config.
        self.remote_config = {}

        # -- We use this flag to make sure we fetch the config from the
        # -- remote server no more than once, since it's not expected to change
        # -- that often.
        self.remote_config_fetched = False

        # -- Get the profile path
        # -- Ex. '/home/obijuan/.apio'
        self._profile_path = home_dir / "profile.json"

        # -- Read the profile from file
        self.load()

    def add_package(self, name: str, version: str):
        """Add a package to the profile class"""

        self.packages[name] = {"version": version}
        self._save()

    def add_setting(self, key: str, value: str):
        """Add one key,value pair in the settings"""

        self.settings[key] = value
        self._save()

    def set_preferences_colors(self, value: str):
        """Set the colors prefernes to on or off."""
        assert value in ["on", "off"], f"Invalid value [{value}]"
        self.preferences["colors"] = value
        self._save()
        self.apply_color_preferences()

    def remove_package(self, name: str):
        """Remove a package from the profile file"""

        if name in self.packages.keys():
            del self.packages[name]
            self._save()

    @staticmethod
    def apply_color_preferences():
        """If an colors are disabled and a click context exist, set it up to
        disable colors.
        """
        # -- Determine if colors should be on or off.
        colors: bool = Profile.read_color_prefernces()

        # -- Apply to the click library.
        # -- If colors are on, we don't write True but None, to use the default
        # -- policy of emitting colors only if not piped out.
        click_context = click.get_current_context(silent=True)
        if click_context:
            click_context.color = None if colors else False

        # -- Apply to the Rich library
        apio_console.configure(colors=colors)

    @staticmethod
    def read_color_prefernces(*, default=True) -> Union[bool, Any]:
        """Returns the value of the colors preferences or default if not
        specified. This is a static method because we may need this value
        before creating  the profile object, for example when printing command
        help.
        """

        profile_path = util.resolve_home_dir() / "profile.json"

        if not profile_path.exists():
            return default

        with open(profile_path, "r", encoding="utf8") as f:
            # -- Get the colors preferenes value, if exists.
            data = json.load(f)
            preferences = data.get("preferences", {})
            colors = preferences.get("colors", None)

        # -- Get the click context, if exists.
        if colors == "on":
            return True
        if colors == "off":
            return False
        return default

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

    def get_package_required_version(
        self,
        package_name: str,
        *,
        cached_config_ok=True,
        verbose: bool = False,
    ):
        """Get from the required version of the package with given name.
        If cached_config_ok is False, we make sure to use a fresh remote config
        from this invocation of apio.
        """
        config = self._get_remote_config(
            cached_config_ok=cached_config_ok, verbose=verbose
        )
        required_version = config["packages"][package_name]["version"]
        return required_version

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

        # -- Extract the fields
        self.preferences = data.get("preferences", {})
        self.settings = data.get("settings", {})
        self.packages = data.get("installed-packages", {})
        self.remote_config = data.get("remote-config", {})

        # -- Indicate that the current remote config may be old.
        self.remote_config_fetched = False

    def _save(self):
        """Save the profile file"""

        # -- Create the profile folder, if it does not exist yet
        path = self._profile_path.parent
        if not path.exists():
            path.mkdir()

        # -- Construct the json dict.
        data = {}
        if self.preferences:
            data["preferences"] = self.preferences
        if self.settings:
            data["settings"] = self.settings
        if self.packages:
            data["installed-packages"] = self.packages
        if self.remote_config:
            data["remote-config"] = self.remote_config

        # -- Write to profile file.
        with open(self._profile_path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4, sort_keys=True)

        # -- Dump for debugging.
        if util.is_debug():
            cout("Saved profile:", style="magenta")
            cprint(json.dumps(data, indent=2))

    def _get_remote_config(
        self, *, cached_config_ok: bool, verbose: bool
    ) -> Dict:
        """Returns the apio remote config JSON dict. If the value is cached
        in the profile and force_cache = False, then it's returned as is,
        otherwise, it's fetched remotly and also saved in the profile.
        """
        # -- If a remote config is already available and fetch is not force
        # -- use it.
        if self.remote_config_fetched or (
            cached_config_ok and self.remote_config
        ):
            return self.remote_config

        # -- Here we need to fetch the remote config from the remote server.
        # -- Construct remote config file url.
        # apio_version = util.get_apio_version()
        # config_url = APIO_REMOTE_CONFIG_URL_TEMPLATE.format(apio_version)
        if verbose or util.is_debug():
            cout(f"Fetching remote config from '{self.remote_config_url}'")

        # -- Fetch the version info.
        resp: requests.Response = requests.get(
            self.remote_config_url, timeout=5
        )

        # -- Exit if http error.
        if resp.status_code != 200:
            cerror(
                "Downloading apio remote config file failed, "
                f"error code {resp.status_code}",
            )
            cout(f"URL {self.remote_config_url}", style="yellow")
            sys.exit(1)

        # -- Here when download was ok.
        if verbose or util.is_debug():
            cout("Remote config file downloaded ok.")

        # -- Print the file's content.
        if util.is_debug():
            cout(resp.text)

        # -- Parse the remote JSON config file into adict.
        try:
            remote_config = json.loads(resp.text)

        # -- Handle parsing error.
        except json.decoder.JSONDecodeError as exc:

            # -- Show the error and abort.
            cerror("Invalid remote cofing file", f"{exc}")
            sys.exit(1)

        # -- Update the profile and save
        if remote_config != self.remote_config:
            self.remote_config = remote_config
            self._save()

        # -- Mark that we have the altest config.
        self.remote_config_fetched = True

        # -- Return the object for the resource
        return remote_config
