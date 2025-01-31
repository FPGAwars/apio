"""Test for the apio_console.py."""

from apio.common.apio_console import cstyle, cunstyle


def test_style_unstyle():
    """Test the styling and unstyling functions"""

    # -- Test cstyle()
    assert cstyle("") == ""
    assert cstyle("", style="red") == ""
    assert cstyle("abc xyz", style="red") == "\x1b[31mabc xyz\x1b[0m"
    assert cstyle("abc xyz", style="cyan bold") == "\x1b[1;36mabc xyz\x1b[0m"
    assert cstyle("ab \n xy", style="cyan bold") == "\x1b[1;36mab \n xy\x1b[0m"

    # -- Test cunstyle() with plain text.
    assert cunstyle("") == ""
    assert cunstyle("abc xyz") == "abc xyz"

    # -- Test cunstyle() with colored text.
    assert cunstyle(cstyle("")) == ""
    assert cunstyle(cstyle("abc xyz")) == "abc xyz"
    assert cunstyle(cstyle("ab \n xy")) == "ab \n xy"
