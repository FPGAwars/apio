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

from io import StringIO
from typing import Optional
from rich.console import Console
from rich.ansi import AnsiDecoder
from rich.text import Text

# Suppress earning about access to the global variables.
# pylint: disable=global-statement


_console: Console = None
_decoder: AnsiDecoder = None


def _make_console(colors: bool = True) -> Console:
    """Create a fresh Console object."""
    color_system = "auto" if colors else None
    console = Console(width=100, color_system=color_system)
    return console


def apply_color_preference(colors: bool) -> None:
    """Turn the color support on or off."""
    global _console
    # pylint: enable=global-statement

    # -- Get current color setting.
    has_colors = bool(_console.color_system)

    # -- If the new value is different, create a new console.
    if colors != has_colors:
        _console = _make_console(colors=colors)


def cout(*text_lines: str, style: Optional[str] = None) -> None:
    """Prints lines of text to the console, using the optional style."""

    for text_line in text_lines:
        # -- If colors are off, strip potential coloring in the text.
        # -- This may be coloring that we recieved from the scons process.
        if not _console.color_system:
            text_objs: Text = _decoder.decode_line(text_line)
            text_line = text_objs.plain

        # -- Write it out using the given style.
        _console.out(text_line, style=style, highlight=False)


def cerror(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Error: ' and aplying to all of them the red color."""
    # -- Output the first line.
    _console.out(f"Error: {text_lines[0]}", style="red", highlight=False)
    # -- Output the rest of the lines.
    for text_line in text_lines[1:]:
        _console.out(text_line, highlight=False, style="red")


def cwarning(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Warning: ' and aplying to all of them the yellow color."""
    # -- Emit first line.
    _console.out(f"Warning: {text_lines[0]}", style="yellow", highlight=False)
    # -- Emit the rest of the lines
    for text_line in text_lines[1:]:
        _console.out(text_line, highlight=False, style="yellow")


def crender(
    markdown_text: str, *, style: Optional[str] = None, highlight: bool = False
) -> None:
    """Render the given markdown text. Applying optional style and if enabled,
    highlighting semantic elements such as strings if enabled."""
    _console.print(
        markdown_text,
        highlight=highlight,
        style=style,
    )


def cstyle(text: str, style: Optional[str] = None) -> str:
    """Render the text to a string using an optional style."""
    # -- Save the old output.
    file_save = _console.file
    # -- Set output to a buffer.
    _console.file = StringIO()
    # -- Output to buffer.
    _console.out(text, style=style, highlight=False, end="")
    # -- Get captured string.
    result = _console.file.getvalue()
    # -- Restore old output.
    _console.file = file_save
    # -- Return the capture value.
    return result


# -- Init
_console = _make_console()
_decoder = AnsiDecoder()
