# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""Test for the apio_themes.py."""

from apio.common.apio_themes import THEMES_TABLE, DEFAULT_THEME


def test_theme_style():
    """Tests that all theme have the same set of style keys."""

    for theme_name, theme_obj in THEMES_TABLE.items():
        print(f"Testing theme {theme_name}")
        assert set(theme_obj.styles.keys()) == set(DEFAULT_THEME.styles.keys())
