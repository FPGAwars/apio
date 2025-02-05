"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

# pylint: disable=fixme
# TODO: Implement range detectors for Fumo, Tinyprog, and Iceprog, similar to
# the pnr detector. This will avoid matching of output from other programs.

# TODO: Use apio_console.is_terminal() to determine if the output goes to a
# terminal or a pipe and have an alternative handling for the cursor commands
# when writing to a pipe.

import re
from enum import Enum
from typing import List, Optional, Tuple
from apio.common.apio_console import cout
from apio.common.apio_styles import INFO, WARNING, SUCCESS, ERROR


# -- Terminal cursor commands.
CURSOR_UP = "\033[F"
ERASE_LINE = "\033[K"

# -- A regex to detect iverilog warnings we want to filter out, per
# -- https://github.com/FPGAwars/apio/issues/557
IVERILOG_TIMING_WARNING_REGEX = re.compile(
    r"oss-cad-suite/share/yosys.*warning.*Timing checks are not supported",
    re.IGNORECASE,
)


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
    ) -> Optional[RangeEvents]:
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


class IVerilogRangeDetector(RangeDetector):
    """Implements a RangeDetector for the iverolog command output."""

    def classify_line(self, pipe_id: PipeId, line: str) -> RangeEvents:
        # -- Range start: an iverolog command on stdout.
        if pipe_id == PipeId.STDOUT and line.startswith("iverilog"):
            return RangeEvents.START_AFTER

        # Range end: The end message of nextnpr.
        if pipe_id == PipeId.STDOUT and line.startswith("gtkwave"):
            return RangeEvents.END_BEFORE

        return None


class IceProgRangeDetector(RangeDetector):
    """Implements a RangeDetector for the iceprog command output."""

    def __init__(self):
        super().__init__()
        # -- Indicates if the last line should be erased before printing the
        # -- next one. This happens with interactive progress meters.
        self.pending_erasure = False

    def classify_line(self, pipe_id: PipeId, line: str) -> RangeEvents:
        # -- Range start: A nextpnr command on stdout without
        # -- the -q (quiet) flag.
        if pipe_id == PipeId.STDOUT and line.startswith("iceprog"):
            self.pending_erasure = False
            return RangeEvents.START_AFTER

        # Range end: The end message of nextnpr.
        if pipe_id == PipeId.STDERR and line.startswith("Bye."):
            return RangeEvents.END_AFTER

        return None


class SconsFilter:
    """Implements the filtering and printing of the stdout/err streams of the
    scons subprocess. Accepts a line one at a time, detects lines ranges of
    intereset, mutates and colors the lines where applicable, and print to
    stdout."""

    def __init__(self, colors_enabled: bool):
        self.colors_enabled = colors_enabled
        self._pnr_detector = PnrRangeDetector()
        self._iverilog_detector = IVerilogRangeDetector()
        self._iceprog_detector = IceProgRangeDetector()

    def on_stdout_line(self, line: str) -> None:
        """Stdout pipe calls this on each line."""
        self.on_line(PipeId.STDOUT, line)

    def on_stderr_line(self, line: str) -> None:
        """Stderr pipe calls this on each line."""
        self.on_line(PipeId.STDERR, line)

    @staticmethod
    def _assign_line_color(
        line: str, patterns: List[Tuple[str, str]], default_color: str = None
    ) -> Optional[str]:
        """Assigns a color for a given line using a list of (regex, color)
        pairs. Returns the color of the first matching regex or default_color
        if none match.
        """
        for regex, color in patterns:
            if re.search(regex, line):
                return color
        return default_color

    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    def on_line(self, pipe_id: PipeId, line: str) -> None:
        """A shared handler for stdout/err lines from the scons sub process.
        The handler writes both stdout and stderr lines to stdout, possibly
        with modifications such as text deletion, coloring, and cursor
        directives.

        NOTE: Ideally, the program specific patterns such as for Fumo and
        Iceprog should should be condition by a range detector for lines that
        came from that program. That is to minimize the risk of matching lines
        from other programs. See the PNR detector for an example.
        """

        # -- Update the range detectors.
        in_pnr_verbose_range = self._pnr_detector.update(pipe_id, line)
        in_iverolog_range = self._iverilog_detector.update(pipe_id, line)
        in_iceprog_range = self._iceprog_detector.update(pipe_id, line)

        # -- For debugging.
        # cout(
        #     f"{'P' if in_pnr_verbose_range else '-'}"
        #     f"{'V' if in_iverolog_range else '-'}"
        #     f"{'I' if in_iverolog_range else '-'}"
        #     f" {pipe_id} : {line}"
        # )

        # -- Handle the line while in the nextpnr verbose log range.
        if pipe_id == PipeId.STDERR and in_pnr_verbose_range:

            # -- Remove the 'Info: ' prefix. Nextpnr write a long log where
            # -- each line starts with "Info: "
            if line.startswith("Info: "):
                line = line[6:]

            # -- Assign line color.
            line_color = self._assign_line_color(
                line.lower(),
                [
                    (r"^warning:", WARNING),
                    (r"^error:", ERROR),
                    (r"^fatal error:", ERROR),
                ],
            )
            cout(line, style=line_color)
            return

        # -- Special handling of iverilog lines. We drop warning line spam
        # -- per Per https://github.com/FPGAwars/apio/issues/530
        if (
            in_iverolog_range
            and pipe_id == PipeId.STDERR
            and "cells_sim.v" in line
            and "Timing checks are not supported" in line
        ):
            # -- Drop the line.
            return

        # -- Special handling for iceprog line range.
        if pipe_id == PipeId.STDERR and in_iceprog_range:
            # -- Iceprog prints blank likes that are used as line erasers.
            # -- We don't need them here.
            if len(line) == 0:
                return

            # -- If the last iceprog line was a to-be-erased line, erase it
            # -- now and clear the flag.
            if self._iceprog_detector.pending_erasure:
                print(
                    CURSOR_UP + ERASE_LINE,
                    end="",
                    flush=True,
                )
                self._iceprog_detector.pending_erasure = False

            # -- Determine if the current line should be erased before we will
            # -- print the next line.
            # --
            # -- Match outputs like these "addr 0x001400  3%"
            # -- Regular expression remainder:
            # -- ^ --> Match the begining of the line
            # -- \s --> Match one blank space
            # -- [0-9A-F]+ one or more hexadecimal digit
            # -- \d{1,2} one or two decimal digits
            pattern = r"^addr\s0x[0-9A-F]+\s+\d{1,2}%"

            # -- Calculate if there is a match!
            match = re.search(pattern, line)

            # -- If the line is to be erased set the flag.
            if match:
                self._iceprog_detector.pending_erasure = True

            # -- Determine line color by its content and print it.
            line_color = self._assign_line_color(
                line,
                [
                    (r"^done.", "green"),
                    (r"^VERIFY OK", "green"),
                ],
            )
            cout(line, style=line_color)
            return

        # -- Special handling for Fumo lines.
        if pipe_id == PipeId.STDOUT:
            pattern_fomu = r"^Download\s*\[=*"
            match = re.search(pattern_fomu, line)
            if match:
                # -- Delete the previous line
                #
                # -- NOTE: If the progress line will scroll instead of
                # -- overwriting each other, try to add erasure of a second
                # -- line. This is due to the commit below which restored
                # -- empty lines.
                # -  Commit 93fc9bc4f3bfd21568e2d66f11976831467e3b97.
                #
                print(CURSOR_UP + ERASE_LINE, end="", flush=True)
                cout(line, style=SUCCESS)
                return

        # -- Special handling for tinyprog lines.
        if pipe_id == PipeId.STDERR:
            # -- Check if the line correspond to an output of
            # -- the tinyprog programmer (TinyFPGA board)
            # -- Match outputs like these " 97%|█████████▋| "
            # -- Regular expression remainder:
            # -- \s --> Match one blank space
            # -- \d{1,3} one, two or three decimal digits
            pattern_tinyprog = r"\s\d{1,3}%\|█*"

            # -- Calculate if there is a match
            match_tinyprog = re.search(pattern_tinyprog, line)

            # -- Match all the progress bar lines except the
            # -- initial one (when it is 0%)
            if match_tinyprog and " 0%|" not in line:
                # -- Delete the previous line.
                #
                # -- NOTE: If the progress line will scroll instead of
                # -- overwriting each other, try to add erasure of a second
                # -- line. This is due to the commit below which restored
                # -- empty lines.
                # -  Commit 93fc9bc4f3bfd21568e2d66f11976831467e3b97.
                #
                print(CURSOR_UP + ERASE_LINE, end="", flush=True)
                cout(line)
                return

        # -- Special filter for https://github.com/FPGAwars/apio/issues/557
        if IVERILOG_TIMING_WARNING_REGEX.search(line):
            # -- Ignore this line.
            # cout(line, style=WARNING)
            return

        # -- Handling the rest of the stdout lines.
        if pipe_id == PipeId.STDOUT:
            # -- Default stdout line coloring.
            line_color = self._assign_line_color(
                line.lower(),
                [
                    (r"is up to date", SUCCESS),
                    (r"^warning:", WARNING),
                    (r"^error:", ERROR),
                ],
            )
            cout(line, style=line_color)
            return

        # Handling the rest of stderr the lines.
        line_color = self._assign_line_color(
            line.lower(),
            [
                (r"^info:", INFO),
                (r"^warning:", WARNING),
                (r"^error:", ERROR),
            ],
        )
        cout(line, style=line_color)
