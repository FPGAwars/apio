# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manage the apio profile file"""

import json
import re
import sys
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
import requests
from apio.common import apio_console
from apio.common.apio_console import cout, cerror, cwarning
from apio.common.apio_styles import INFO, EMPH3
from apio.utils import util, jsonc


class RemoteConfigPolicy(Enum):
    """Represents possible requirements from the remote config."""

    # -- Config is not being used in this Apio invocation.
    NO_CONFIG = 1
    # -- Config is being used but can be a cached value, as long that it's
    # -- not too old.
    CACHED_OK = 2
    # -- Config is being used and a fresh copy is that was fetch in this
    # -- invocation of Apio is required.
    GET_FRESH = 3


@dataclass(frozen=True)
class PackageRemoteConfig:
    """Contains a package info from the remote config."""

    # -- E.g. "tools-oss-cad-suite"
    repo_name: str
    # -- E.g. "FPGAwars"
    repo_organization: str
    # -- E.g. "0.2.3"
    release_version: str
    # -- E.g. "${YYYY-MM-DD}""
    release_tag: str
    # -- E.g. "apio-oss-cad-suite-${PLATFORM}-${YYYYMMDD}.zip"
    release_file: str


def get_datetime_stamp(dt: Optional[datetime] = None) -> str:
    """Returns a string with time now as yyyy-mm-dd-hh-mm"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d-%H-%M")


def days_between_datetime_stamps(
    ts1: str, ts2: str, default: Any
) -> Optional[int]:
    """Given two values generated by get_datetime_stamp(), return the
    number of days from ts1 to ts2. The value can be negative if ts2 is
    earlier than ts1. Returns the given 'default' value if either timestamp
    is invalid."""

    # -- The parsing format.
    fmt = "%Y-%m-%d-%H-%M"

    # -- Convert to timedates
    try:
        datetime1 = datetime.strptime(ts1, fmt)
        datetime2 = datetime.strptime(ts2, fmt)
    except ValueError:
        return default

    # -- Round to beginning of day.
    day1 = datetime(datetime1.year, datetime1.month, datetime1.day)
    day2 = datetime(datetime2.year, datetime2.month, datetime2.day)

    # -- Compute the diff in days.
    delta_days: int = (day2 - day1).days

    # -- All done.
    assert isinstance(delta_days, int)
    return delta_days


class Profile:
    """Class for managing the apio profile file
    ex. ~/.apio/profile.json
    """

    # -- Only these instance vars are allowed.
    __slots__ = (
        "_profile_path",
        "remote_config_url",
        "remote_config_ttl_days",
        "_remote_config_policy",
        "_cached_remote_config",
        "preferences",
        "installed_packages",
    )

    def __init__(
        self,
        home_dir: Path,
        remote_config_url_template: str,
        remote_config_ttl_days: int,
        remote_config_policy: RemoteConfigPolicy,
    ):
        """remote_config_url_template is a url string with a "{V}"
        placeholder for the apio version such as "0.9.6."""

        # -- Sanity check
        assert isinstance(remote_config_ttl_days, int)
        assert 0 < remote_config_ttl_days <= 30

        # -- Resolve and cache the remote config url. We replace any {V} with
        # -- the apio version such as "0.9.6".
        self.remote_config_url = remote_config_url_template.replace(
            "{V}", util.get_apio_version()
        )

        # -- Save remote url ttl setting.
        self.remote_config_ttl_days = remote_config_ttl_days

        # -- Save remote config policy.
        self._remote_config_policy = remote_config_policy

        # -- Verify that we resolved all the placeholders.
        assert "%" not in self.remote_config_url, self.remote_config_url

        if util.is_debug(1):
            cout(f"Remote config url: {self.remote_config_url}")

        # ---- Set the default parameters

        # User preferences
        self.preferences = {}

        # -- Installed package versions
        self.installed_packages = {}

        # -- A copy of remote config.
        self._cached_remote_config = {}

        # -- Get the profile path
        # -- Ex. '/home/obijuan/.apio'
        self._profile_path = home_dir / "profile.json"

        # -- Read the profile from file, if exists.
        self._load_profile_file()

        # -- Apply config policy
        self._apply_remote_config_policy()

    def _apply_remote_config_policy(self) -> None:
        """Called after loading the profile file, to apply the remote config
        policy for this invocation."""

        # -- Case 1 - Remote config not used at all.
        if self._remote_config_policy == RemoteConfigPolicy.NO_CONFIG:
            return

        # -- Case 2 - A fresh config is required for the current command.
        if self._remote_config_policy == RemoteConfigPolicy.GET_FRESH:
            self._fetch_and_update_remote_config(error_is_fatal=True)
            return

        # -- Case 3 - A fresh config is optional but there is no cached
        # -- config.
        assert self._remote_config_policy == RemoteConfigPolicy.CACHED_OK
        if not self._cached_remote_config:
            if util.is_debug(1):
                cout("Saved remote config is not available.", style=INFO)
            self._fetch_and_update_remote_config(error_is_fatal=True)
            return

        # -- Case 4 - May need to fetch a new config but can continue with
        # -- the cached config in case of a fetch failure.
        #
        # -- Get the cached config metadata.
        cashed_config_metadata = self._cached_remote_config.get("metadata", {})
        last_fetch_timestamp = cashed_config_metadata.get("loaded-at", "")
        last_fetch_url = cashed_config_metadata.get("loaded-from", "")

        # -- Determine if we need a new config because the remote config URL
        # -- was changed (e.g. with APIO_REMOTE_CONFIG_URL)
        url_changed = last_fetch_url != self.remote_config_url

        # -- Determine if there is time related reason to fetch a new config.
        days_since_last_fetch = days_between_datetime_stamps(
            last_fetch_timestamp, get_datetime_stamp(), default=99999
        )
        time_expired = days_since_last_fetch >= self.remote_config_ttl_days
        time_unexpected = days_since_last_fetch < 0

        # -- Announce a reason for the fetch. We announce at most one.
        if util.is_debug(1):
            cout(
                f"{days_since_last_fetch=}, {time_expired=}, "
                f"{time_unexpected}, {url_changed=}",
                style=INFO,
            )

        # -- Fetch the new config if needed.
        if url_changed or time_expired or time_unexpected:
            self._fetch_and_update_remote_config(error_is_fatal=False)

    def _check_config_enabled(self) -> None:
        """Check that the remote config is enabled for this invocation."""
        if self._remote_config_policy == RemoteConfigPolicy.NO_CONFIG:
            # -- This is a programming error.
            raise ValueError(
                f"Remote config not available, initialized "
                f"with context {self._remote_config_policy}"
            )

    @property
    def remote_config(self) -> Dict:
        """Returns the remote config that is applicable for this invocation.
        Should not called if the context was initialized with NO_CONFIG."""
        self._check_config_enabled()
        return self._cached_remote_config

    def add_package(self, name: str, version: str, platform_id: str, url: str):
        """Add a package to the profile class"""

        self.installed_packages[name] = {
            "version": version,
            "platform": platform_id,
            "loaded-by": util.get_apio_version(),
            "loaded-at": get_datetime_stamp(),
            "loaded-from": url,
        }
        self._save()

    def set_preferences_theme(self, theme: str):
        """Set prefer theme name."""
        self.preferences["theme"] = theme
        self._save()
        self.apply_color_preferences()

    def remove_package(self, name: str):
        """Remove a package from the profile file"""

        if name in self.installed_packages.keys():
            del self.installed_packages[name]
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

    def get_package_installed_info(self, package_name: str) -> Optional[str]:
        """Return (package_version, platform_id) of the given installed
        package. Values are replaced with "" if not installed or a value is
        missing."""
        package_info = self.installed_packages.get(package_name, {})
        package_version = package_info.get("version", "")
        platform_id = package_info.get("platform", "")
        return (package_version, platform_id)

    def get_package_config(
        self,
        package_name: str,
    ) -> PackageRemoteConfig:
        """Given a package name, return the remote config information with the
        version and fetch information.
        """
        self._check_config_enabled()

        # -- Extract package's remote config.
        package_config = self.remote_config["packages"][package_name]
        repo_name = package_config["repository"]["name"]
        repo_organization = package_config["repository"]["organization"]
        release_version = package_config["release"]["version"]
        release_tag = package_config["release"]["release-tag"]
        release_file = package_config["release"]["package-file"]

        return PackageRemoteConfig(
            repo_name=repo_name,
            repo_organization=repo_organization,
            release_version=release_version,
            release_tag=release_tag,
            release_file=release_file,
        )

    def _load_profile_file(self):
        """Load the profile file if exists, e.g.
        /home/obijuan/.apio/profile.json)
        """

        # -- If profile file doesn't exist then nothing to do.
        if not self._profile_path.exists():
            return

        # -- Read the profile file as a json dict.
        with open(self._profile_path, "r", encoding="utf8") as f:
            data = json.load(f)

        # -- Determine if the cached remote config is usable.
        remote_config = data.get("remote-config", {})
        config_apio_version = remote_config.get("metadata", {}).get(
            "loaded-by", ""
        )
        config_usable = config_apio_version == util.get_apio_version()

        # -- Extract the fields. If remote config is of a different apio
        # -- version, drop it.
        self.preferences = data.get("preferences", {})
        self.installed_packages = data.get("installed-packages", {})
        self._cached_remote_config = remote_config if config_usable else {}

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

        if self.installed_packages:
            data["installed-packages"] = self.installed_packages
        if self._cached_remote_config:
            data["remote-config"] = self._cached_remote_config

        # -- Write to profile file.
        with open(self._profile_path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=4)

        # -- Dump for debugging.
        if util.is_debug(1):
            cout("Saved profile:", style=EMPH3)
            cout(json.dumps(data, indent=2))

    def _fetch_and_update_remote_config(self, *, error_is_fatal: bool) -> None:
        """Returns the apio remote config JSON dict."""

        self._check_config_enabled()

        # -- Fetch the config text. Returns None if error_is_fatal=False and
        # -- fetch failed.
        config_text: Optional[str] = self._fetch_remote_config_text(
            error_is_fatal=error_is_fatal
        )

        if config_text is None:
            assert not error_is_fatal
            return

        # -- Print the file's content for debugging
        if util.is_debug(1):
            cout(config_text)

        # -- Convert the jsonc to json by removing '//' comments.
        config_text = jsonc.to_json(config_text)

        # -- Parse the remote JSON config file into a dict.
        try:
            remote_config = json.loads(config_text)

        # -- Handle parsing error.
        except json.decoder.JSONDecodeError as exc:

            # -- Handle as a fatal error.
            msg = [
                "Fetched a fresh remote config file but it failed to parse.",
                f"{exc}",
            ]
            if error_is_fatal:
                cerror(*msg)
                sys.exit(1)
            # -- Else, handle as a soft error
            cwarning(*msg)
            return

        # -- Append remote config metadata
        metadata_dict = {}
        metadata_dict["loaded-by"] = util.get_apio_version()
        metadata_dict["loaded-at"] = get_datetime_stamp()
        metadata_dict["loaded-from"] = self.remote_config_url
        remote_config["metadata"] = metadata_dict

        # -- Do some checks and fail if invalid. This is not an exhaustive
        # -- check.
        ok = self._check_remote_config(
            remote_config, error_is_fatal=error_is_fatal
        )
        if not ok:
            return

        self._cached_remote_config = remote_config
        self._save()

        # Announce
        if util.is_debug(1):
            cout("A fresh remote config was fetched and saved.", style=INFO)

    @staticmethod
    def _check_remote_config(config: Dict, error_is_fatal: bool) -> bool:
        """Check that the package versions have the expected format YYYY.MM.DD
        so we can transform them to the tag YYYYY-MM-DD. Fatal error if not.
        """
        pattern = r"^[0-9]{4}[.][0-9]{2}[.][0-9]{2}$"
        for package_id, package_info in config["packages"].items():
            version = package_info["release"]["version"]
            if not re.match(pattern, version):
                msg = (
                    f"Invalid version '{version}' in package "
                    f"'{package_id}' remote config."
                )
                hint = (
                    "Package versions should have the format "
                    "YYYY.MM.DD, e.g. 2025.06.15."
                )

                # -- Handle as a fatal error.
                if error_is_fatal:
                    cerror(msg)
                    cout(
                        hint,
                        style=INFO,
                    )
                    sys.exit(1)

                # -- Handle as a soft error
                cwarning(msg)
                cout(hint, style=INFO)
                return False

        # -- All is ok.
        return True

    def _fetch_remote_config_text(self, error_is_fatal: bool) -> Optional[str]:
        """Fetches and returns the apio remote config JSON text. In case
        of an error, returns None."""

        # pylint: disable=broad-exception-caught

        # -- Announce the remote config url
        if util.is_debug(1):
            cout(
                f"Fetching remote config from '{self.remote_config_url}'",
                style=INFO,
            )

        # -- If the URL has a file protocol, read from the file. This
        # -- is used mostly for testing of a new package version.
        if self.remote_config_url.startswith("file://"):
            file_path = self.remote_config_url[7:]
            try:
                with open(file_path, encoding="utf-8") as f:
                    file_text = f.read()
            except Exception as e:
                # -- Since local config file can be fixed and doesn't depend
                # -- on availability of a remote server, we make this a fatal
                # -- error instead of returning None.
                cerror("Failed to read a local config file.", str(e))
                sys.exit(1)

            # -- Local file read OK.
            return file_text

        # -- Here is the normal case where the config url is not of a local
        # -- file but at a remote URL.

        # -- Fetch the remote config. With timeout = 10, this failed a
        # -- few times on github workflow tests so increased to 25.
        resp: requests.Response = requests.get(
            self.remote_config_url, timeout=25
        )

        # -- Exit if http error.
        if resp.status_code != 200:
            msg = (
                "Downloading apio remote config file failed, "
                f"error code {resp.status_code}"
            )
            hint = f"URL {self.remote_config_url}"

            # -- Handle as a fatal error.
            if error_is_fatal:
                cerror(msg)
                cout(hint, style=INFO)
                sys.exit(1)

            # -- Else, handle as a soft error.
            cwarning(msg)
            cout(hint, style=INFO)
            return None

        # -- Done ok.
        assert resp.text is not None
        return resp.text
