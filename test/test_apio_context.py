"""
Tests of apio_context.py
"""

import os
from pathlib import Path
from test.conftest import ApioRunner
from pytest import LogCaptureFixture, raises
from apio.apio_context import ApioContext, ApioContextScope

# pylint: disable=fixme
# TODO: Add more tests.


def test_init(apio_runner: ApioRunner):
    """Tests the initialization of the apio context."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini file.
        sb.write_default_apio_ini()

        # -- Default init.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        assert apio_ctx.has_project

        # -- Verify context's project dir.
        assert str(apio_ctx.project_dir) == "."
        assert apio_ctx.project_dir.samefile(Path.cwd())
        assert apio_ctx.project_dir.samefile(sb.proj_dir)

        # -- Verify context's home and packages dirs.
        assert apio_ctx.home_dir == sb.home_dir
        assert apio_ctx.packages_dir == sb.packages_dir


def _test_invalid_home_dir(
    invalid_char: str, apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """A helper function to test the initialization of the apio context with an
    invalid char in the home dir path."""

    with apio_runner.in_sandbox() as sb:

        # -- Make up a home dir path with the invalid char.
        invalid_home_dir = sb.sandbox_dir / f"apio-{invalid_char}-home"
        os.environ["APIO_HOME_DIR"] = str(invalid_home_dir)

        # -- Initialize an apio context. It shoudl exit with an error.
        with raises(SystemExit) as e:
            ApioContext(scope=ApioContextScope.NO_PROJECT)
        assert e.value.code == 1
        assert (
            f"non supported character [{invalid_char}]"
            in capsys.readouterr().out
        )


def test_invalid_home_dir(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests the initialization of the apio context with home dirs that
    contain invalid chars."""
    for invalid_char in ["ó", "ñ", " ", "😼"]:
        _test_invalid_home_dir(invalid_char, apio_runner, capsys)
