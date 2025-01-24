# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""A class that manages the console output of the apio scons process."""

from rich.console import Console


def _make_console() -> Console:
    """Create a fresh console."""
    # -- We force terminal mode and always send colors to the apio process
    # -- via the stdout pipe. The apio process strips those colors if
    # -- its output is also pipeed out.
    console = Console(width=100, force_terminal=True)
    return console


# -- The singleton console object we use throughout the apio scons process.
_console: Console = _make_console()


def cprint(markdown_text: str, *, style: str = None) -> None:
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
