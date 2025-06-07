# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manage the apio profile file"""

import json
import sys
from dataclasses import dataclass
from typing import Dict, Optional
from pathlib import Path
import requests
from apio.common import apio_console
from apio.common.apio_console import cout, cerror, cprint
from apio.common.apio_styles import INFO, EMPH3, ERROR
from apio.utils import util, jsonc, env_options


@dataclass(frozen=True)
class PackageRemoteConfig:
    """Contains a package info from the remote config."""

    # -- E.g. "tools-oss-cad-suite"
    repo_name: str
    # -- E.g. "FPGAwars"
    repo_organization: str
    # -- E.g. "0.2.3"
    release_version: str
    # -- E.g. %T
    release_tag: str


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
            cout(f"Remote config url: {self.remote_config_url}")

        # ---- Set the default parameters

        # User preferences
        self.preferences = {}

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

    def set_preferences_theme(self, theme: str):
        """Set prefer theme name."""
        self.preferences["theme"] = theme
        self._save()
        self.apply_color_preferences()

    def remove_package(self, name: str):
        """Remove a package from the profile file"""

        if name in self.packages.keys():
            del self.packages[name]
            self._save()

    @staticmethod
    def apply_color_preferences():
        """Apply currently preferred theme."""
        # -- If not specified, read the theme from file.
        theme: str = Profile.read_preferences_theme()

        # -- Apply to the apio console.
        apio_console.configure(theme_name=theme)

    @staticmethod
    def read_preferences_theme(*, default: str = "light") -> Optional[str]:
        """Returns the value of the theme preference or default if not
        specified. This is a static method because we may need this value
        before creating  the profile object, for example when printing command
        help.
        """

        profile_path = util.resolve_home_dir() / "profile.json"

        if not profile_path.exists():
            return default

        with open(profile_path, "r", encoding="utf8") as f:
            # -- Get the colors preferences value, if exists.
            data = json.load(f)
            preferences = data.get("preferences", {})
            theme = preferences.get("theme", None)

        # -- Get the click context, if exists.
        return theme if theme else default

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

    def get_package_config(
        self,
        package_name: str,
        *,
        cached_config_ok=True,
        verbose: bool = False,
    ) -> PackageRemoteConfig:
        """Given a package name, return the remote config information with the
        version and fetch information.
        If cached_config_ok is False, we make sure to use a fresh remote config
        from this invocation of apio.
        """
        config = self._get_remote_config(
            cached_config_ok=cached_config_ok, verbose=verbose
        )

        # -- Extract package's remote config.
        remote_config = config["packages"][package_name]
        repo_name = remote_config["repository"]["name"]
        repo_organization = remote_config["repository"]["organization"]
        release_version = remote_config["release"]["version"]
        release_tag = remote_config["release"]["tag"]

        return PackageRemoteConfig(
            repo_name=repo_name,
            repo_organization=repo_organization,
            release_version=release_version,
            release_tag=release_tag,
        )

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

        if self.packages:
            data["installed-packages"] = self.packages
        if self.remote_config:
            data["remote-config"] = self.remote_config

        # -- Write to profile file.
        with open(self._profile_path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4, sort_keys=True)

        # -- Dump for debugging.
        if util.is_debug():
            cout("Saved profile:", style=EMPH3)
            cprint(json.dumps(data, indent=2))

    def _fetch_remote_config_text(self) -> str:
        """Fetch and return the apio remote config JSON text."""

        # pylint: disable=broad-exception-caught

        # -- If the URL has a file protocol, read from the file. This
        # -- is used mostly for testing of a new package version.
        if self.remote_config_url.startswith("file://"):
            file_path = self.remote_config_url[7:]
            try:
                with open(file_path, encoding="utf-8") as f:
                    file_text = f.read()
            except Exception as e:
                cout("Failed to load local config file.", str(e), style=ERROR)
                sys.exit(1)

            # -- Local file read OK.
            return file_text

        # -- Here is the normal case where the config url is not of a local
        # -- file but at a remote URL.

        # -- Fetch the remote config. With timeout = 5, this failed a few times
        # -- on github workflow tests so increased to 10.
        resp: requests.Response = requests.get(
            self.remote_config_url, timeout=10
        )

        # -- Exit if http error.
        if resp.status_code != 200:
            cerror(
                "Downloading apio remote config file failed, "
                f"error code {resp.status_code}",
            )
            cout(f"URL {self.remote_config_url}", style=INFO)
            sys.exit(1)

        return resp.text

    def _get_remote_config(
        self, *, cached_config_ok: bool, verbose: bool
    ) -> Dict:
        """Returns the apio remote config JSON dict. If the value is cached
        in the profile and force_cache = False, then it's returned as is,
        otherwise, it's fetched remotely and also saved in the profile.
        """
        # -- If a remote config is already available and fetch is not force
        # -- use it.
        if self.remote_config_fetched or (
            cached_config_ok and self.remote_config
        ):
            return self.remote_config

        # -- Here we need to fetch the remote config from the remote server.
        # -- Construct remote config file url.
        if env_options.is_defined(env_options.APIO_REMOTE_CONFIG_URL):
            cout(
                f"Custom remote config: '{self.remote_config_url}'",
                style=EMPH3,
            )
        elif verbose or util.is_debug():
            cout(f"Remote config: '{self.remote_config_url}'")

        # -- Fetch the config text.
        config_text = self._fetch_remote_config_text()

        # -- Here when download was ok.
        cout("Remote config fetched ok.")

        # -- Print the file's content.
        if util.is_debug():
            cout(config_text)

        # -- Convert the jsonc to json by removing '//' comments.
        config_text = jsonc.to_json(config_text)

        # -- Parse the remote JSON config file into a dict.
        try:
            remote_config = json.loads(config_text)

        # -- Handle parsing error.
        except json.decoder.JSONDecodeError as exc:

            # -- Show the error and abort.
            cerror("Invalid remote config file", f"{exc}")
            sys.exit(1)

        # -- Update the profile and save
        if remote_config != self.remote_config:
            self.remote_config = remote_config
            self._save()

        # -- Mark that we have the last config.
        self.remote_config_fetched = True

        # -- Return the object for the resource
        return remote_config
