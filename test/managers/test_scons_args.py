"""
Tests of scons_args.py
"""

from apio.managers.scons_args import Arg

# pylint: disable=fixme
# TODO: Add more tests.


def test_arg():
    """Tests the Arg class."""

    # -- Test an arg that is mapped to an scons varible.
    arg = Arg("arg1", "var1")
    assert not arg.has_value
    assert not arg.has_var_value
    arg.set("val1")
    assert arg.has_value
    assert arg.has_var_value
    assert arg.value == "val1"
    assert arg.var_name == "var1"
