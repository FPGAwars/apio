"""
Tests of scons_util.py
"""

from apio.util import plurality

# pylint: disable=fixme
# TODO: Add more tests.


def test_pluraliry():
    """Tests the plurality function."""
    assert plurality(3, "file") == "3 files"
