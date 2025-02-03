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
from rich.style import Style
from rich.text import Text
from apio.common import styles, rich_lib_windows
from apio.common.styles import WARNING, ERROR, BORDER
from apio.common.proto.apio_pb2 import (
    TerminalMode,
    FORCE_PIPE,
    FORCE_TERMINAL,
    AUTO_TERMINAL,
)

# -- The names of the Rich library color names is available at:
# -- https://rich.readthedocs.io/en/stable/appendix/colors.html


# -- Redemanded table cell padding. 1 space on the left and 3 on the right.
PADDING = padding = (0, 3, 0, 1)

# -- Line width when rendering help and docs.
DOCS_WIDTH = 70

# -- The name of the colors theme that turns colors off.
NO_COLORS = "no-colors"


# -- This console state is initialized at the end of this file.
@dataclass
class ConsoleState:
    """Contains the state of the apio console."""

    # None = auto. True and False force to terminal and pipe mode respectively.
    terminal_mode: TerminalMode
    # The theme name. If None, default is "light"
    theme_name: str
    # The current console object.
    console: Console
    # The latest AnsiDecoder we use for capture printing.
    decoder: AnsiDecoder

    def __post_init__(self):
        assert self.terminal_mode is not None
        assert self.theme_name is not None
        assert self.console is not None
        assert self.decoder is not None


# -- Initialized by Configure().
_state: ConsoleState = None


# -- Default theme styles. Optimized for light terminal background.
THEME_LIGHT = {
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
    styles.STRING: "italic",
    styles.CODE: "dark_green",
    styles.URL: "dark_blue",
    styles.CMD_NAME: "dark_red bold",
    styles.TITLE: "dark_red bold",
    styles.BORDER: "dim",
    styles.EMPH1: "dark_cyan",
    styles.EMPH2: "deep_sky_blue4 bold",
    styles.EMPH3: "magenta",
    styles.SUCCESS: "green",
    styles.INFO: "yellow",
    styles.WARNING: "yellow",
    styles.ERROR: "red",
}


# -- Theme styles optimized for dark terminal background. Should contain
# -- exactly The same keys as THEME_LIGHT.
THEME_DARK = {
    # -- Styles that are used internally by rich library.
    "bar.back": Style(color="grey23"),
    "bar.complete": Style(color="rgb(249,38,114)"),
    "bar.finished": Style(color="rgb(114,156,31)"),
    "table.header": "",
    # --Apio's abstracted style names.
    styles.STRING: "italic",
    styles.CODE: "bright_green",
    styles.URL: "bright_blue",
    styles.CMD_NAME: "bright_red",
    styles.TITLE: "bright_red bold",
    styles.BORDER: "dim",
    styles.EMPH1: "bright_cyan",
    styles.EMPH2: "bright_blue bold",
    styles.EMPH3: "bright_magenta",
    styles.SUCCESS: "bright_green",
    styles.INFO: "bright_yellow",
    styles.WARNING: "bright_yellow",
    styles.ERROR: "bright_red",
}

THEMES_TABLE = {
    "light": THEME_LIGHT,
    "dark": THEME_DARK,
}


# NOTE: not declaring terminal_mode and  theme_name is Optional[] because it
# causes the tests to fail with python 3.9.
# pylint: disable=global-statement
def configure(
    *,
    terminal_mode: TerminalMode = None,
    theme_name: str = None,
) -> None:
    """Change the apio console settings."""
    global _state

    # -- Force utf-8 output encoding. This is a workaround for rich library
    # -- defaulting to non graphic ASCII border for tables.
    # --
    # stdout_fixed = rich_lib_windows.fix_windows_stdout_encoding()
    rich_lib_windows.fix_windows_stdout_encoding()

    # -- Determine theme name.
    if not theme_name:
        if _state:
            # -- Fall to theme name from state, if available.
            theme_name = _state.theme_name
        else:
            # -- Fall to default theme.
            theme_name = "light"

    # -- Determine terminal mode.
    if terminal_mode is None:
        if _state:
            # -- Fall to terminal mode from the state.
            terminal_mode = _state.terminal_mode
        else:
            # -- Fall to default.
            terminal_mode = AUTO_TERMINAL

    # -- Determine console color parameters.
    if theme_name == NO_COLORS:
        color_system = None
        theme_styles = THEME_LIGHT  # Arbitrary, ignored since colors are off.
    else:
        color_system = "auto"
        theme_styles = THEMES_TABLE.get(theme_name, THEME_LIGHT)

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
        theme=Theme(theme_styles, inherit=False),
    )

    # -- Construct the helper decoder.
    decoder = AnsiDecoder()

    # -- Save the state
    _state = ConsoleState(
        terminal_mode=terminal_mode,
        theme_name=theme_name,
        console=console_,
        decoder=decoder,
    )

    # -- For debugging.
    # print()
    # print(f"***     {_stdout_fixed=}")
    # print(f"***     {terminal_mode=}")
    # print(f"***     {theme_name=}")
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
    return _state.theme_name != NO_COLORS


def theme() -> str:
    """Return the current theme name."""
    check_apio_console_configured()
    return _state.theme_name


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
        assert isinstance(text_line, str)

        # -- If colors are off, strip potential coloring in the text.
        # -- This may be coloring that we received from the scons process.
        if not console().color_system:
            text_line = cunstyle(text_line)

        # -- Determine end of line
        end = "\n" if nl else ""

        # -- Write it out using the given style.
        console().out(text_line, style=style, highlight=False, end=end)


def cerror(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Error: ' and applying to all of them the red color."""
    # -- Output the first line.
    console().out(f"Error: {text_lines[0]}", style=ERROR, highlight=False)
    # -- Output the rest of the lines.
    for text_line in text_lines[1:]:
        console().out(text_line, highlight=False, style=ERROR)


def cwarning(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Warning: ' and applying to all of them the yellow color."""
    # -- Emit first line.
    console().out(f"Warning: {text_lines[0]}", style=WARNING, highlight=False)
    # -- Emit the rest of the lines
    for text_line in text_lines[1:]:
        console().out(text_line, highlight=False, style=WARNING)


def cprint(
    markdown_text: str, *, style: Optional[str] = None, highlight: bool = False
) -> None:
    """Render the given markdown text. Applying optional style and if enabled,
    highlighting semantic elements such as strings if enabled."""
    console().print(
        markdown_text,
        highlight=highlight,
        style=style,
    )


class ConsoleCapture:
    """A context manager to output into a string."""

    def __init__(self):
        self._saved_file = None
        self._buffer = None

    def __enter__(self):
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
    markdown_text: str, width: int = DOCS_WIDTH, end: str = "\n"
) -> None:
    """A wrapper around Console.print that is specialized for rendering
    help and docs."""
    console().print(markdown_text, highlight=True, width=width, end=end)


def docs_rule(width: int = DOCS_WIDTH):
    """Print a docs horizontal separator."""
    cout("─" * width, style=BORDER)


def is_terminal():
    """Returns True if the console writes to a terminal (vs a pipe)."""
    return console().is_terminal


def cwidth():
    """Return the console width."""
    return console().width
