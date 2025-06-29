# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Apio themes definitions"""

from typing import Dict, Union
from dataclasses import dataclass
from rich.style import Style
from apio.common import apio_styles


@dataclass(frozen=True)
class ApioTheme:
    """Represents a theme."""

    # -- The theme name, as selected by the 'apio preferences' command.
    name: str
    # -- True if colors are enabled. False for monochrome.
    colors_enabled: bool
    # -- The theme styles table. All theme are expected to have the same
    # -- set of styles keys, even if color is disabled.
    styles: Dict[str, Union[str, Style]]


# -- A theme that is optimized for light backgrounds.
THEME_LIGHT = ApioTheme(
    name="light",
    colors_enabled=True,
    styles={
        # -- Styles that are used internally by rich library methods we
        # -- call. These styles are not used directly by apio and thus we don't
        # -- assign them abstract names.  For the full list of available
        # -- styles see https://tinyurl.com/rich-default-styles
        # -- Colors: https://rich.readthedocs.io/en/stable/appendix/colors.html
        "bar.back": Style(color="grey23"),
        "bar.complete": Style(color="rgb(249,38,114)"),
        "bar.finished": Style(color="rgb(114,156,31)"),
        "table.header": "",
        # --Apio's abstracted style names.
        apio_styles.STRING: "italic",
        apio_styles.CODE: "dark_green",
        apio_styles.URL: "dark_blue",
        apio_styles.CMD_NAME: "dark_red bold",
        apio_styles.TITLE: "dark_red bold",
        apio_styles.BORDER: "dim",
        apio_styles.EMPH1: "dark_cyan",
        apio_styles.EMPH2: "deep_sky_blue4 bold",
        apio_styles.EMPH3: "magenta",
        apio_styles.SUCCESS: "green",
        apio_styles.INFO: "yellow",
        apio_styles.WARNING: "yellow",
        apio_styles.ERROR: "red",
    },
)

# -- A theme that is optimized for dark backgrounds.
THEME_DARK = ApioTheme(
    name="dark",
    colors_enabled=True,
    styles={
        # -- Styles that are used internally by rich library.
        "bar.back": Style(color="grey23"),
        "bar.complete": Style(color="rgb(249,38,114)"),
        "bar.finished": Style(color="rgb(114,156,31)"),
        "table.header": "",
        # --Apio's abstracted style names.
        apio_styles.STRING: "italic",
        apio_styles.CODE: "bright_green",
        apio_styles.URL: "bright_blue",
        apio_styles.CMD_NAME: "bright_red",
        apio_styles.TITLE: "bright_red bold",
        apio_styles.BORDER: "dim",
        apio_styles.EMPH1: "bright_cyan",
        apio_styles.EMPH2: "bright_blue bold",
        apio_styles.EMPH3: "bright_magenta",
        apio_styles.SUCCESS: "bright_green",
        apio_styles.INFO: "bright_yellow",
        apio_styles.WARNING: "bright_yellow",
        apio_styles.ERROR: "bright_red",
    },
)

# -- A monochrome theme.
THEME_NO_COLORS = ApioTheme(
    name="no-colors",
    colors_enabled=False,
    # -- A fake style table that is suppressed by the flag above.
    styles={key: "" for key in THEME_LIGHT.styles},
)

# -- Mapping of theme name to theme object.
THEMES_TABLE = {
    THEME_LIGHT.name: THEME_LIGHT,
    THEME_DARK.name: THEME_DARK,
    THEME_NO_COLORS.name: THEME_NO_COLORS,
}

# -- A list of theme names.
THEMES_NAMES = list(THEMES_TABLE.keys())

# -- The default theme.
DEFAULT_THEME = THEME_LIGHT
