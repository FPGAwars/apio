"""
Tests of scons_filters.py
"""

from apio.managers.scons_filter import PnrRangeDetector, PipeId

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
