"""Test for the apio_console.py."""

import os
import pytest
from apio.common import apio_console
from tests.conftest import ApioRunner
from apio.common.apio_console import (
    FORCE_TERMINAL,
    cstyle,
    cunstyle,
    fatal_error,
)


def test_style_unstyle():
    """Test the styling and unstyling functions"""

    apio_console.configure(terminal_mode=FORCE_TERMINAL, theme_name="light")

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


def test_fatal_error(apio_runner: ApioRunner):
    """Test the fatal_error() function."""

    with apio_runner.in_sandbox():

        # -- Test with a single error line
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                fatal_error("test error line 1")
        assert e.value.code == 1
        assert "Error: test error line 1" in log.out
        assert "set env var APIO_DEBUG=1" in log.out

        # -- Test with a multiple error lines
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                fatal_error(
                    "test error line 1",
                    "test error line 2",
                )
        assert e.value.code == 1
        assert "Error: test error line 1" in log.out
        assert "test error line 2" in log.out
        assert "Error: test error line 2" not in log.out
        assert "set env var APIO_DEBUG=1" in log.out

        # -- Make an exception object with stack info.
        try:
            raise RuntimeError("my fake exception error")
        except RuntimeError as e:
            test_exc = e

        # -- Test with a cause exception.
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                fatal_error("test error line 1", cause=test_exc)
        assert e.value.code == 1
        assert "Error: test error line 1" in log.out
        assert "my fake exception error" in log.out
        assert "set env var APIO_DEBUG=1" in log.out

        # -- Test with a cause exception and APIO_DEBUG=1.
        os.environ["APIO_DEBUG"] = "1"
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                fatal_error("test error line 1", cause=test_exc)
        assert e.value.code == 1
        assert "Error: test error line 1" in log.out
        assert "my fake exception error" in log.out
        assert "tests/unit_tests/common/test_apio_console.py" in log.out
        assert "set env var APIO_DEBUG=1" not in log.out
