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
from apio.common import styles
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


# -- This console state is initialized at the end of this file.
@dataclass
class ConsoleState:
    """Contains the state of the apio console."""

    # None = auto. True and False force to terminal and pipe mode respectively.
    terminal_mode: TerminalMode = None
    # The theme name. If None, default is "light"
    theme_name: str = None
    # The current console object.
    console: Console = None
    # The latest AnsiDecoder we use for capture printing.
    decoder: AnsiDecoder = None

    def __post_init__(self):
        self.reset()

    def reset(self):
        """Reset the state to its default state."""
        self.terminal_mode = AUTO_TERMINAL
        self.theme_name = "light"
        self.console = None
        self.decoder = None


# -- Initialized below by reset.
_state: ConsoleState = ConsoleState()


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
    styles.CODE: "bold",
    styles.URL: "dark_blue",
    styles.CMD_NAME: "dark_red bold",
    styles.TITLE: "dark_red bold",
    styles.BORDER: "dim",
    styles.EMPH1: "cyan",
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
    styles.CODE: "bold",
    styles.URL: "bright_blue",
    styles.CMD_NAME: "bright_red",
    styles.TITLE: "red bold",
    styles.BORDER: "dim",
    styles.EMPH1: "bright_cyan",
    styles.EMPH2: "bright_blue bold",
    styles.EMPH3: "bright_magenta",
    styles.SUCCESS: "bright_green",
    styles.INFO: "bright_yellow",
    styles.WARNING: "bright_yellow",
    styles.ERROR: "red",
}

THEMES_TABLE = {
    "light": THEME_LIGHT,
    "dark": THEME_DARK,
}


def configure(
    *,
    reset: bool = False,
    terminal_mode: TerminalMode = None,
    theme_name: str = None,
) -> None:
    """Change the apio console settings."""

    # -- Reset the state if requested.
    if reset:
        _state.reset()

    # -- Update terminal mode if specified.
    if terminal_mode is not None:
        assert terminal_mode in [
            FORCE_TERMINAL,
            FORCE_PIPE,
            AUTO_TERMINAL,
        ], terminal_mode
        _state.terminal_mode = terminal_mode

    # -- Update theme name if specified.
    if theme_name is not None:
        _state.theme_name = theme_name

    # -- Determine console color parameters.
    if _state.theme_name == "no-color":
        color_system = None
        theme_styles = THEME_LIGHT  # Arbitrary, ignored since colors are off.
    else:
        color_system = "auto"
        theme_styles = THEMES_TABLE.get(_state.theme_name, THEME_LIGHT)

    # -- Map the terminal mode to the console's force_terminal arg.
    if _state.terminal_mode == FORCE_TERMINAL:
        force_terminal = True
    elif _state.terminal_mode == FORCE_PIPE:
        force_terminal = False
    else:
        assert (
            _state.terminal_mode == AUTO_TERMINAL
        ), f"{_state.terminal_mode=}"
        force_terminal = None

    # -- Construct the new console.
    _state.console = Console(
        color_system=color_system,
        force_terminal=force_terminal,
        theme=Theme(theme_styles, inherit=False),
    )

    # -- Construct the helper decoder.
    _state.decoder = AnsiDecoder()


def is_colors_enabled() -> bool:
    """Returns True if colors are enabled."""
    return _state.theme_name != "no-color"


def theme() -> str:
    """Return the current theme name."""
    return _state.theme_name


def console():
    """Returns the underlying console. This value should not be cached as
    the console object changes when the configure() or reset() are called."""
    return _state.console


def cunstyle(text: str) -> str:
    """A replacement for click unstyle(). This function removes ansi colors
    from a string."""
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
        if not _state.console.color_system:
            text_line = cunstyle(text_line)

        # -- Determine end of line
        end = "\n" if nl else ""

        # -- Write it out using the given style.
        _state.console.out(text_line, style=style, highlight=False, end=end)


def cerror(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Error: ' and applying to all of them the red color."""
    # -- Output the first line.
    _state.console.out(f"Error: {text_lines[0]}", style=ERROR, highlight=False)
    # -- Output the rest of the lines.
    for text_line in text_lines[1:]:
        _state.console.out(text_line, highlight=False, style=ERROR)


def cwarning(*text_lines: str) -> None:
    """Prints one or more text lines, adding to the first one the prefix
    'Warning: ' and applying to all of them the yellow color."""
    # -- Emit first line.
    _state.console.out(
        f"Warning: {text_lines[0]}", style=WARNING, highlight=False
    )
    # -- Emit the rest of the lines
    for text_line in text_lines[1:]:
        _state.console.out(text_line, highlight=False, style=WARNING)


def cprint(
    markdown_text: str, *, style: Optional[str] = None, highlight: bool = False
) -> None:
    """Render the given markdown text. Applying optional style and if enabled,
    highlighting semantic elements such as strings if enabled."""
    _state.console.print(
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
        self._saved_file = _state.console.file
        self._buffer = StringIO()
        _state.console.file = self._buffer
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _state.console.file = self._saved_file

    @property
    def value(self):
        """Returns the captured text."""
        return self._buffer.getvalue()


def cstyle(text: str, style: Optional[str] = None) -> str:
    """Render the text to a string using an optional style."""
    with ConsoleCapture() as capture:
        _state.console.out(text, style=style, highlight=False, end="")
        return capture.value


def docs_text(
    markdown_text: str, width: int = DOCS_WIDTH, end: str = "\n"
) -> None:
    """A wrapper around Console.print that is specialized for rendering
    help and docs."""
    _state.console.print(markdown_text, highlight=True, width=width, end=end)


def docs_rule(width: int = DOCS_WIDTH):
    """Print a docs horizontal separator."""
    cout("─" * width, style=BORDER)


def is_terminal():
    """Returns True if the console writes to a terminal (vs a pipe)."""
    return _state.console.is_terminal


def cwidth():
    """Return the console width."""
    return _state.console.width
