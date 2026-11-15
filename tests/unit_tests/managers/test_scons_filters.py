# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""
Tests of scons_filters.py
"""

from apio.managers.scons_filter import (
    PnrRangeDetector,
    GtkwaveRangeDetector,
    PipeId,
    SconsFilter,
)
from tests.conftest import ApioRunner

# TODO: Add testing of on_line() including line coloring and line ignoring.


def test_pnr_range_detector():
    """Tests the pnr range class."""

    # -- Create a PNR range detector.
    rd = PnrRangeDetector()

    # -- Starting out of range
    assert not rd.update(PipeId.STDOUT, "hello world")
    assert not rd.update(PipeId.STDOUT, "hello world")

    # -- Start of range trigger (from next line)
    assert not rd.update(PipeId.STDOUT, "nextpnr-ice40 bla bla")

    # -- In range.
    assert rd.update(PipeId.STDOUT, "bla bla")
    assert rd.update(PipeId.STDOUT, "info: bla bla")

    # -- End of range trigger. (from next line)
    assert rd.update(PipeId.STDERR, "Program finished normally.")

    # -- out of range.
    assert not rd.update(PipeId.STDOUT, "bla bla")


def test_gtkwave_range_detector():
    """Tests the gtkwave range class."""

    # -- Create a gtkwave range detector.
    rd = GtkwaveRangeDetector()

    # -- Starting out of range. Gtkwave on stderr doesn't start the range.
    assert not rd.update(PipeId.STDOUT, "hello world")
    assert not rd.update(PipeId.STDERR, "gtkwave bla bla")

    # -- Start of range trigger (from next line)
    assert not rd.update(PipeId.STDOUT, "gtkwave bla bla")

    # -- In range, to the end.
    assert rd.update(PipeId.STDOUT, "bla bla")
    assert rd.update(PipeId.STDERR, "bla bla")


def test_gtkwave_spam_filter(apio_runner: ApioRunner):
    """Tests that gtkwave spam and empty lines are dropped, while other
    lines, including empty lines before gtkwave starts, pass through."""

    with apio_runner.in_sandbox():

        spam = (
            "(gtkwave:68068): Gdk-CRITICAL **: 12:58:39.197: "
            "gdk_atom_intern: assertion 'atom_name != NULL' failed"
        )

        with apio_runner.with_logger() as log:
            scons_filter = SconsFilter(colors_enabled=False)

            # -- Before gtkwave. Empty lines are kept.
            scons_filter.on_stdout_line("line1", "\n")
            scons_filter.on_stderr_line("", "\n")
            scons_filter.on_stdout_line("gtkwave a.vcd a.gtkw", "\n")

            # -- Gtkwave output. Spam and empty lines are dropped.
            scons_filter.on_stderr_line("", "\n")
            scons_filter.on_stderr_line(spam, "\n")
            scons_filter.on_stderr_line("  ", "\n")
            scons_filter.on_stderr_line(spam, "\n")
            scons_filter.on_stderr_line("line2", "\n")

        assert log.out == "line1\n\ngtkwave a.vcd a.gtkw\nline2\n"
