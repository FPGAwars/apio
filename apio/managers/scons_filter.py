"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2


import re
import threading
from enum import Enum
from typing import List, Optional, Tuple
from apio.common.apio_console import cout, cunstyle, cwrite, cstyle
from apio.common.apio_styles import INFO, WARNING, SUCCESS, ERROR
from apio.utils import util


# -- A table with line coloring rules. If a line matches any regex, it gets
# -- The style of the first regex it matches.
LINE_COLORING_TABLE = [
    # -- Info patterns
    (r"^info:", INFO),
    # -- Warning patterns
    (r"^warning:", WARNING),
    # -- Error patterns.
    (r"^error:", ERROR),
    (r"fail: ", ERROR),
    (r"fatal: ", ERROR),
    (r"^fatal error:", ERROR),
    (r"assertion failed", ERROR),
    # -- Success patterns
    (r"is up to date", SUCCESS),
    (r"[$]finish called", SUCCESS),
    (r"^verify ok$", SUCCESS),
    (r"^done$", SUCCESS),
]


class PipeId(Enum):
    """Represent the two output streams from the scons subprocess."""

    STDOUT = 1
    STDERR = 2


class RangeEvents(Enum):
    """An stdout/err line can trigger one of these events, when detecting a
    range of lines."""

    START_BEFORE = 1  # Range starts before the current line.
    START_AFTER = 2  # Range starts after the current line.
    END_BEFORE = 3  # Range ends before the current line.
    END_AFTER = 4  # Range ends, after the current line.


class RangeDetector:
    """Base detector of a range of lines within the sequence of stdout/err
    lines recieves from the scons subprocess."""

    def __init__(self):
        self._in_range = False

    def update(self, pipe_id: PipeId, line: str) -> bool:
        """Updates the range detector with the next stdout/err line.
        return True iff detector classified this line to be within a range."""

        prev_state = self._in_range
        event = self.classify_line(pipe_id, line)

        if event == RangeEvents.START_BEFORE:
            self._in_range = True
            return self._in_range

        if event == RangeEvents.START_AFTER:
            self._in_range = True
            return prev_state

        if event == RangeEvents.END_BEFORE:
            self._in_range = False
            return self._in_range

        if event == RangeEvents.END_AFTER:
            self._in_range = False
            return prev_state

        assert event is None, event
        return self._in_range

    def classify_line(
        self, pipe_id: PipeId, line: str
    ) -> Optional[RangeEvents]:  # pragma: no cover
        """Tests if the next stdout/err line affects the range begin/end.
        Subclasses should implement this with the necessary logic for the
        range that is being detected.
        Returns the event of None if no event."""
        raise NotImplementedError("Should be implemented by a subclass")


class PnrRangeDetector(RangeDetector):
    """Implements a RangeDetector for the nextpnr command verbose
    log lines."""

    def classify_line(self, pipe_id: PipeId, line: str) -> RangeEvents:
        # -- Break line into words.
        tokens = line.split()

        # -- Range start: A nextpnr command on stdout without
        # -- the -q (quiet) flag.
        # --
        # -- IMPORTANT: Each of the supported architecture has a different
        # -- nextpnr command, including 'nextpnr', 'nextpnr-ecp5', and
        # -- 'nextpnr-himbaechel'.
        if (
            pipe_id == PipeId.STDOUT
            and line.startswith("nextpnr")
            and "-q" not in tokens
        ):
            return RangeEvents.START_AFTER

        # Range end: The end message of nextnpr.
        if pipe_id == PipeId.STDERR and "Program finished normally." in line:
            return RangeEvents.END_AFTER

        return None


class SconsFilter:
    """Implements the filtering and printing of the stdout/err streams of the
    scons subprocess. Accepts a line one at a time, detects lines ranges of
    interest, mutates and colors the lines where applicable, and print to
    stdout."""

    def __init__(self, colors_enabled: bool):
        self.colors_enabled = colors_enabled
        self._pnr_detector = PnrRangeDetector()

        # self._iverilog_detector = IVerilogRangeDetector()
        # self._iceprog_detector = IceProgRangeDetector()

        # -- We cache the values to avoid reevaluating sys env.
        self._is_debug = util.is_debug(1)
        self._is_verbose_debug = util.is_debug(5)

        # -- Accumulates string pieces until we write and flush them. This
        # -- mechanism is used to display progress bar correctly, Writing the
        # -- erasure string only when a new value is available.
        self._output_bfr: str = ""

        # -- The stdout and stderr are called from independent threads, so we
        # -- protect the handling method with this lock.
        # --
        # -- We don't protect the third thread which is main(). We hope that
        # -- it doesn't any print console output while these two threads are
        # -- active, otherwise it can mingle the output.
        self._thread_lock = threading.Lock()

    def on_stdout_line(self, line: str, terminator: str) -> None:
        """Stdout pipe calls this on each line. Called from the stdout thread
        in AsyncPipe."""
        with self._thread_lock:
            self.on_line(PipeId.STDOUT, line, terminator)

    def on_stderr_line(self, line: str, terminator: str) -> None:
        """Stderr pipe calls this on each line. Called from the stderr thread
        in AsyncPipe."""
        with self._thread_lock:
            self.on_line(PipeId.STDERR, line, terminator)

    @staticmethod
    def _assign_line_color(
        line: str, patterns: List[Tuple[str, str]], default_color: str = None
    ) -> Optional[str]:
        """Assigns a color for a given line using a list of (regex, color)
        pairs. Returns the color of the first matching regex (case
        insensitive), or default_color if none match.
        """
        for regex, color in patterns:
            if re.search(regex, line, re.IGNORECASE):
                return color
        return default_color

    def _output_line(
        self, line: str, style: Optional[str], terminator: str
    ) -> None:
        """Output a line. If a style is given, force that style, otherwise,
        pass on any color information it may have. The implementation takes
        into consideration progress bars such as when uploading with the
        iceprog programmer. These progress bar require certain timing between
        the chars to have sufficient time to display the text before erasing
        it."""

        # -- Apply style if needed.
        if style:
            line_part = cstyle(cunstyle(line), style=style)
        else:
            line_part = line

        # -- Get line conditions.
        is_white = len(line.strip()) == 0
        is_cr = terminator == "\r"

        if not is_cr:
            # -- Terminator is EOF or \n. We flush everything.
            self._output_bfr += line_part + terminator
            leftover = ""
            flush = True
        elif is_white:
            # -- Terminator is \r and line is white space (progress bar
            # -- eraser). We queue and and wait for the updated text.
            self._output_bfr += line_part + terminator
            leftover = ""
            flush = False
        else:
            # -- Terminator is \r and line has actual text, we flush it out
            # -- but save queue the \r because on windows 10 cmd it clears the
            # -- line(?)
            self._output_bfr += line_part
            leftover = terminator
            flush = True

        if flush:
            # -- Flush the buffer and queue the optional leftover terminator.
            cwrite(self._output_bfr)
            self._output_bfr = leftover
        else:
            # -- We just queued. Should have no leftover here.
            assert not leftover

    def _ignore_line(self, line: str) -> None:
        """Handle an ignored line. It's dumped if in debug mode."""
        if self._is_debug:
            cout(f"IGNORED: {line}")

    def on_line(self, pipe_id: PipeId, line: str, terminator) -> None:
        """A shared handler for stdout/err lines from the scons sub process.
        The handler writes both stdout and stderr lines to stdout, possibly
        with modifications such as text deletion, coloring, and cursor
        directives.

        For the possible values of terminator, see AsyncPipe.__init__().

        NOTE: Ideally, the program specific patterns such as for Fumo and
        Iceprog should should be condition by a range detector for lines that
        came from that program. That is to minimize the risk of matching lines
        from other programs. See the PNR detector for an example.
        """

        if self._is_verbose_debug:
            cout(
                f"*** LINE: [{pipe_id}], [{repr(line)}], [{repr(terminator)}]",
                style=INFO,
            )

        # -- Update the range detectors.
        in_pnr_verbose_range = self._pnr_detector.update(pipe_id, line)

        # -- Remove the 'Info: ' prefix. Nextpnr write a long log where
        # -- each line starts with "Info: "
        if (
            pipe_id == PipeId.STDERR
            and in_pnr_verbose_range
            and line.startswith("Info: ")
        ):
            line = line[6:]

        # -- Output the line in the appropriate style.
        line_color = self._assign_line_color(line, LINE_COLORING_TABLE)
        self._output_line(line, line_color, terminator)
