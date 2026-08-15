# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manage the apio profile file"""

import json
import sys
from datetime import datetime

from typing import Tuple, Optional
from pathlib import Path
from apio.common import apio_console
from apio.common.apio_console import cout, cerror
from apio.common.apio_themes import THEMES_TABLE
from apio.common.apio_styles import INFO, EMPH3
from apio.utils import util


def get_datetime_stamp(dt: Optional[datetime] = None) -> str:
    """Returns a string with time now as yyyy-mm-dd-hh-mm"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d-%H-%M")


class Profile:
    """Class for managing the apio profile file
    ex. ~/.apio/profile.json
    """

    # -- Only these instance vars are allowed.
    __slots__ = (
        "_profile_path",
        "_packages_index_path",
        "preferences",
        "installed_packages",
    )

    def __init__(
        self,
        home_dir: Path,
        packages_dir: Path,
    ):
        """remote_config_url_template is a url string with the
        placeholder {major} and {minor} for the apio's major and minor
        version. '"""

        # ---- Set the default parameters

        # User preferences
        self.preferences = {}

        # -- Installed package versions
        self.installed_packages = {}

        # -- Cache the profile file path
        # -- Ex. '/home/obijuan/.apio/profile.json'
        self._profile_path = home_dir / "profile.json"

        # -- Cache the packages index file path
        # -- Ex. '/home/obijuan/.apio/packages/installed_packages.json'
        self._packages_index_path = packages_dir / "installed_packages.json"

        # -- Read the profile from file, if exists.
        self._maybe_load_profile_file()

        # -- Read the installed packages file, if exists.
        self._maybe_load_installed_packages_file()

    def add_package(self, name: str, version: str, platform_id: str, url: str):
        """Add a package to the profile class"""

        # -- Updated the installed package data.
        self.installed_packages[name] = {
            "version": version,
            "platform": platform_id,
            "loaded-by": util.get_apio_version_str(),
            "loaded-at": get_datetime_stamp(),
            "loaded-from": url,
        }
        # self._save()
        self._save_installed_packages()

    def set_preferences_theme(self, theme: str):
        """Set prefer theme name."""
        self.preferences["theme"] = theme
        self._save()
        self.apply_color_preferences()

    def remove_package(self, name: str):
        """Remove a package from the profile file"""

        if name in self.installed_packages.keys():
            del self.installed_packages[name]
            # self._save()
            self._save_installed_packages()

    @staticmethod
    def apply_color_preferences():
        """Apply currently preferred theme."""
        # -- Make sure the console is configured, with the default theme,
        # -- before reading the preferences. Reading the preferences resolves
        # -- the apio home dir which may exit with a console error message,
        # -- for example if the home dir path contains a space.
        apio_console.configure()

        # -- If not specified, read the theme from file.
        theme: str = Profile.read_preferences_theme()

        # -- Apply to the apio console.
        apio_console.configure(theme_name=theme)

    @staticmethod
    def read_preferences_theme(*, default: str = "light") -> str:
        """Returns the value of the theme preference or default if not
        specified. This is a static method because we may need this value
        before creating  the profile object, for example when printing command
        help.
        """

        profile_path = util.resolve_home_dir() / "profile.json"

        if not profile_path.exists():
            return default

        try:
            with open(profile_path, "r", encoding="utf8") as f:
                # -- Get the colors preferences value, if exists.
                data = json.load(f)
                preferences = data.get("preferences", {})
                theme = preferences.get("theme", default)
        except (OSError, ValueError, AttributeError):
            # -- A corrupt profile file. Not reporting it here since
            # -- _load_profile_file() reports it with a proper error message.
            return default

        # -- Fall back to the default for unknown theme names or values,
        # -- e.g. from a hand edited or old profile file, since
        # -- apio_console.configure() accepts only known theme names.
        if not isinstance(theme, str) or theme not in THEMES_TABLE:
            return default

        return theme

    def get_installed_package_info(self, package_name: str) -> Tuple[str, str]:
        """Return (package_version, platform_id) of the given installed
        package. Values are replaced with "" if not installed or a value is
        missing."""
        package_info = self.installed_packages.get(package_name, {})
        package_version = package_info.get("version", "")
        platform_id = package_info.get("platform", "")
        return (package_version, platform_id)

    def _maybe_load_profile_file(self):
        """Load the profile file if exists, e.g.
        /home/obijuan/.apio/profile.json)
        """

        # -- If profile file doesn't exist then nothing to do.
        if not self._profile_path.exists():
            return

        # -- Read the profile file as a json dict and extract its fields.
        # -- Handle invalid content gracefully, e.g. a corrupt or hand
        # -- edited file, since this runs on every apio command.
        try:
            with open(self._profile_path, "r", encoding="utf8") as f:
                data = json.load(f)

            # -- Extract the fields. If remote config is of a different
            # -- apio version, drop it.
            self.preferences = data.get("preferences", {})

            # -- Perform a shallow sanity check.
            # -- TODO: Perform a full json validation.
            assert isinstance(
                self.preferences, dict
            ), "profile.preferences is not a dict"

        except (OSError, ValueError, AttributeError, AssertionError) as e:
            cerror(f"Invalid profile file {self._profile_path}", f"{e}")
            cout(
                "You can delete the file, "
                "Apio will recreate it automatically.",
                style=INFO,
            )
            sys.exit(1)

    def _maybe_load_installed_packages_file(self):
        """Load the installed packages index file if exists, e.g.
        /home/obijuan/.apio/packages/installed_packages.json)
        """

        if self._packages_index_path.exists():

            # -- Read the file as a json dict. Handle invalid content
            # -- gracefully, since this runs on every apio command.
            try:
                with open(
                    self._packages_index_path, "r", encoding="utf8"
                ) as f:
                    self.installed_packages = json.load(f)

                # -- Perform a shallow sanity check.
                # -- TODO: Do a full json validation.
                assert isinstance(
                    self.installed_packages, dict
                ), "Install packages not a dict"
                for name, info in self.installed_packages.items():
                    assert isinstance(
                        info, dict
                    ), f"installed package '{name}' not a dict"

            except (OSError, ValueError, AssertionError) as e:
                cerror(
                    f"Invalid downloaded packages index file "
                    f"{self._packages_index_path}",
                    f"{e}",
                )
                cout(
                    "You can delete the file, "
                    "Apio will recreate it automatically.",
                    style=INFO,
                )
                sys.exit(1)

    def _save(self):
        """Save the profile file"""

        # -- Create the enclosing folder, if it does not exist yet
        path = self._profile_path.parent
        if not path.exists():
            path.mkdir()

        # -- Construct the json dict.
        data = {}
        if self.preferences:
            data["preferences"] = self.preferences

        # -- Write to profile file.
        with open(self._profile_path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=2)

        # -- Dump for debugging.
        if util.is_debug(1):
            cout("Saved profile:", style=EMPH3)
            cout(json.dumps(data, indent=2))

    def _save_installed_packages(self):
        """Save the installed packages file"""

        # -- Create the enclosing folder, if it does not exist yet
        path = self._packages_index_path.parent
        if not path.exists():
            path.mkdir()

        # -- Write to installed packages file.
        with open(self._packages_index_path, "w", encoding="utf8") as f:
            json.dump(self.installed_packages, f, indent=4)

        # -- Dump for debugging.
        if util.is_debug(1):
            cout("Saved installed packages index:", style=EMPH3)
            cout(json.dumps(self.installed_packages, indent=2))
