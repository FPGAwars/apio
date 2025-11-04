# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""A module with functions  to manages the apio console output."""

from io import StringIO
from dataclasses import dataclass
from typing import Optional
from rich.console import Console
from rich.ansi import AnsiDecoder
from rich.theme import Theme
from rich.text import Text
from rich.table import Table
from apio.common import rich_lib_windows
from apio.common.apio_styles import WARNING, ERROR
from apio.common.apio_themes import ApioTheme, THEMES_TABLE, DEFAULT_THEME
from apio.common.proto.apio_pb2 import (
    TerminalMode,
    FORCE_PIPE,
    FORCE_TERMINAL,
    AUTO_TERMINAL,
)

# -- The Rich library colors names are listed at:
# -- https://rich.readthedocs.io/en/stable/appendix/colors.html


# -- Redemanded table cell padding. 1 space on the left and 3 on the right.
PADDING = padding = (0, 3, 0, 1)

# -- Line width when rendering help and docs.
DOCS_WIDTH = 70


# -- This console state is initialized at the end of this file.
@dataclass
class ConsoleState:
    """Contains the state of the apio console."""

    # None = auto. True and False force to terminal and pipe mode respectively.
    terminal_mode: TerminalMode
    # The theme object.
    theme: ApioTheme
    # The current console object.
    console: Console
    # The latest AnsiDecoder we use for capture printing.
    decoder: AnsiDecoder

    def __post_init__(self):
        assert self.terminal_mode is not None
        assert self.theme is not None
        assert self.console is not None
        assert self.decoder is not None


# -- Initialized by Configure().
_state: ConsoleState = None


# NOTE: not declaring terminal_mode and  theme_name is Optional[] because it
# causes the tests to fail with python 3.9.
def configure(
    *,
    terminal_mode: TerminalMode = None,
    theme_name: str = None,
) -> None:
    """Change the apio console settings."""

    # pylint: disable=global-statement

    global _state

    # -- Force utf-8 output encoding. This is a workaround for rich library
    # -- defaulting to non graphic ASCII border for tables.
    # --
    stdout_fixed = rich_lib_windows.fix_windows_stdout_encoding()
    _ = stdout_fixed  # For pylint, when debugging code below commented out.

    # -- Determine the theme.
    if theme_name:
        # -- Used caller specified theme.
        assert theme_name in THEMES_TABLE, theme_name
        theme = THEMES_TABLE[theme_name]
        assert theme.name == theme_name, theme
    elif _state:
        # -- Fall to theme name from state, if available.
        theme = _state.theme
    else:
        # -- Fall to default theme.
        theme = DEFAULT_THEME

    # -- Determine terminal mode.
    if terminal_mode is None:
        if _state:
            # -- Fall to terminal mode from the state.
            terminal_mode = _state.terminal_mode
        else:
            # -- Fall to default.
            terminal_mode = AUTO_TERMINAL

    # -- Determine console color system parameter.
    color_system = "auto" if theme.colors_enabled else None

    # -- Determine console's force_terminal parameter.
    if terminal_mode == FORCE_TERMINAL:
        force_terminal = True
    elif terminal_mode == FORCE_PIPE:
        force_terminal = False
    else:
        assert terminal_mode == AUTO_TERMINAL, terminal_mode
        force_terminal = None

    # -- Construct the new console.
    console_ = Console(
        color_system=color_system,
        force_terminal=force_terminal,
        theme=Theme(theme.styles, inherit=False),
    )

    # -- Construct the helper decoder.
    decoder = AnsiDecoder()

    # -- Save the state
    _state = ConsoleState(
        terminal_mode=terminal_mode,
        theme=theme,
        console=console_,
        decoder=decoder,
    )

    # -- For debugging.
    # print()
    # print(f"***     {stdout_fixed=}")
    # print(f"***     {terminal_mode=}")
    # print(f"***     {theme_name=}")
    # print(f"***     {theme.name=}")
    # print(f"***     {color_system=}")
    # print(f"***     {terminal_mode=}")
    # print(f"***     {force_terminal=}")
    # print(f"***     {_state.console.is_terminal=}")
    # print(f"***     {_state.console.encoding=}")
    # print(f"***     {_state.console.is_dumb_terminal=}")
    # print(f"***     {_state.console.safe_box=}")
    # print(f"***     state={_state}")
    # print()


def check_apio_console_configured():
    """A common check that the apio console has been configured."""
    assert _state.console, "The apio console is not configured."


def is_colors_enabled() -> bool:
    """Returns True if colors are enabled."""
    check_apio_console_configured()
    return _state.theme.colors_enabled


def current_theme_name() -> str:
    """Return the current theme name."""
    check_apio_console_configured()
    return _state.theme.name


def console():
    """Returns the underlying console. This value should not be cached as
    the console object changes when the configure() or reset() are called."""
    check_apio_console_configured()
    return _state.console


def cunstyle(text: str) -> str:
    """A replacement for click unstyle(). This function removes ansi colors
    from a string."""
    check_apio_console_configured()
    text_obj: Text = _state.decoder.decode_line(text)
    return text_obj.plain


def cflush() -> None:
    """Flush the console output."""

    # pylint: disable=protected-access

    # -- Flush the console buffer to the output stream.
    # -- NOTE: We couldn't find an official API for flushing
    # -- THE console's buffer.
    console()._check_buffer()
    # -- Flush the output stream.
    console().file.flush()


def cout(
    *text_lines: str,
    style: Optional[str] = None,
    nl: bool = True,
) -> None:
    """Prints lines of text to the console, using the optional style."""
    # -- If no args, just do an empty println.
    if not text_lines:
        text_lines = [""]

    for text_line in text_lines:
        # -- User is responsible to conversion to strings.
        assert isinstance(text_line, (str, Table)), type(text_line)

        # -- If colors are off, strip potential coloring in the text.
        # -- This may be coloring that we received from the scons process.
        if not console().color_system:
            text_line = cunstyle(text_line)

        # -- Write it out using the given style but without line break.
        # -- We first convert it to Text as a workaround for
        # -- https://github.com/Textualize/rich/discussions/3779.
        console().print(
            Text.from_ansi(text_line, style=style, end=None),
            highlight=False,
            end=None,
        )

        # console().file.flush()

        # -- If needed, write the line break. By writing the line break in
        # -- a separate call, we force the console().out() call above to
        # -- reset the colors before the line break rather than after. This
        # -- caused an additional blank lines after a colored fatal error
        # -- messages from scons.
        if nl:
            console().print("")

    # console().file.flush()
    # console()._check_buffer()
    cflush()


def ctable(table: Table) -> None:
    """Write out a Rich lib Table."""
    assert isinstance(table, Table), type(table)
    console().print(table)
    cflush()


def cmarkdown(markdown_text: str) -> None:
    """Write out a Rich markdown text."""
    assert isinstance(markdown_text, str), type(markdown_text)
    console().print(markdown_text)
    cflush()


def cwrite(s: str) -> None:
    """A low level output that doesn't do any formatting, style, line
    terminator and so on. Flushing is important"""
    # -- Flush the existing console buffer and the output stream.
    cflush()
    # -- Write directly to the output stream, bypassing the
    # -- console's buffer.
    console().file.write(s)
    # -- Flush again.
    cflush()


def cerror(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Error: ' and applying to all of them the red color."""
    # -- Output the first line.
    console().out(f"Error: {text_lines[0]}", style=ERROR, highlight=False)
    # -- Output the rest of the lines.
    for text_line in text_lines[1:]:
        console().out(text_line, highlight=False, style=ERROR)
    cflush()


def cwarning(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Warning: ' and applying to all of them the yellow color."""
    # -- Emit first line.
    console().out(f"Warning: {text_lines[0]}", style=WARNING, highlight=False)
    # -- Emit the rest of the lines
    for text_line in text_lines[1:]:
        console().out(text_line, highlight=False, style=WARNING)
    cflush()


class ConsoleCapture:
    """A context manager to output into a string."""

    def __init__(self):
        self._saved_file = None
        self._buffer = None

    def __enter__(self):
        cflush()
        self._saved_file = console().file
        self._buffer = StringIO()
        console().file = self._buffer
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        console().file = self._saved_file

    @property
    def value(self):
        """Returns the captured text."""
        return self._buffer.getvalue()


def cstyle(text: str, style: Optional[str] = None) -> str:
    """Render the text to a string using an optional style."""
    with ConsoleCapture() as capture:
        console().out(text, style=style, highlight=False, end="")
        return capture.value


def docs_text(
    rich_text: str, width: int = DOCS_WIDTH, end: str = "\n"
) -> None:
    """A wrapper around Console.print that is specialized for rendering
    help and docs."""
    console().print(rich_text, highlight=True, width=width, end=end)


def is_terminal():
    """Returns True if the console writes to a terminal (vs a pipe)."""
    return console().is_terminal


def cwidth():
    """Return the console width."""
    return console().width


def get_theme() -> ApioTheme:
    """Return the the current theme."""
    check_apio_console_configured()
    return _state.theme
