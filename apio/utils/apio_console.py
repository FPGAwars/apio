# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""A class that manages the console output of the apio process."""

from typing import Optional
from rich.console import Console
from rich.ansi import AnsiDecoder
from rich.text import Text


def _make_console(colors: bool = True) -> Console:
    """Create a fresh console. Since we can not change the color_system
    attribute of an existing, console, we need to create a new one when
    it changes."""
    color_system = "auto" if colors else None
    console = Console(width=100, color_system=color_system)
    return console


# -- The singleton console object we use throughout the apio process.
_console: Console = _make_console()

# -- Ansi decoer that we use to strip ansi colors from the scons process
# -- if coloring is off.
_decoder = AnsiDecoder()


def apply_color_preference(colors: bool) -> None:
    """Turn the color support on or off."""
    # W0603: Using the global statement (global-statement)
    # pylint: disable=W0603
    global _console
    # pylint: enable=W0603

    # -- Get current color setting.
    has_colors = bool(_console.color_system)
    # -- If the new value is different, create a new console.
    if colors != has_colors:
        _console = _make_console(colors=colors)


def cout(text: str, *, style: Optional[str] = None) -> None:
    """Prints markdown text to the console, using the optional style."""

    # -- If colors are off, strip potential coloring in the text. This may be
    # -- coloring that we recieved from the scons process.
    if not _console.color_system:
        text_objs: Text = _decoder.decode_line(text)
        text = text_objs.plain

    # -- Write it out using the given style.
    _console.out(text, style=style, highlight=False)


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def cprint(markdown_text: str, *, style: Optional[str] = None) -> None:
    """Prints markdown text to the console, using the optional style."""
    _console.print(markdown_text, style=style, highlight=False)


def cerror(markdown_text: str) -> None:
    """Prints an error markdown message to the console The message is printed
    in red and with the prefix 'Error: '."""
    _console.print(
        f"Error: {markdown_text}", style="red bold", highlight=False
    )


def cwarning(markdown_text: str) -> None:
    """Prints a warning markdown message to the console. The message is
    printed in yellow and with the prefix 'Warning: '."""
    _console.print(
        f"Warning: {markdown_text}", style="yellow", highlight=False
    )
