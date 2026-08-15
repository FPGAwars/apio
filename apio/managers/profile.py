# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
"""Manage the apio profile file"""

import json
import sys
from pathlib import Path
from apio.common import apio_console
from apio.common.apio_console import cout, cerror
from apio.common.apio_themes import THEMES_TABLE
from apio.common.apio_styles import INFO, EMPH3
from apio.utils import util


class Profile:
    """Class for managing the apio profile file
    ex. ~/.apio/profile.json
    """

    # -- Only these instance vars are allowed.
    __slots__ = (
        "_profile_path",
        "preferences",
    )

    def __init__(
        self,
        home_dir: Path,
    ):
        """remote_config_url_template is a url string with the
        placeholder {major} and {minor} for the apio's major and minor
        version. '"""

        # ---- Set the default parameters

        # User preferences
        self.preferences = {}

        # -- Cache the profile file path
        # -- Ex. '/home/obijuan/.apio/profile.json'
        self._profile_path = home_dir / "profile.json"

        # -- Read the profile from file, if exists.
        self._maybe_load_profile_file()

    def set_preferences_theme(self, theme: str):
        """Set prefer theme name."""
        self.preferences["theme"] = theme
        self._save()
        self.apply_color_preferences()

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
