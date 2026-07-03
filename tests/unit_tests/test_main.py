"""
Tests of apio's __main__.py entry point.
"""

import os
import sys
import subprocess
from subprocess import CompletedProcess
from tests.conftest import ApioRunner
from apio import __main__ as apio_main


def _run_apio_version(extra_env: dict) -> CompletedProcess:
    """Runs 'apio --version' in a fresh process with the given extra env
    vars."""
    return subprocess.run(
        [sys.executable, apio_main.__file__, "--version"],
        env={**os.environ, **extra_env},
        capture_output=True,
        encoding="utf-8",
        text=True,
        check=False,
    )


def test_apio_debug_env_var_values(apio_runner: ApioRunner):
    """Tests that malformed APIO_DEBUG values don't crash the apio entry
    point. It used to crash with an unhandled ValueError on every command."""

    with apio_runner.in_sandbox():

        # -- Malformed values should be tolerated (debug off).
        for value in ["x", "", "1.5", '"x"', '"']:
            result = _run_apio_version({"APIO_DEBUG": value})
            assert result.returncode == 0, result.stderr
            assert "Apio CLI version" in result.stdout, result.stdout
            assert "Traceback" not in result.stderr, result.stderr

        # -- Valid values, including windows style quoted values, should
        # -- work as before.
        for value in ["0", "1", '"2"']:
            result = _run_apio_version({"APIO_DEBUG": value})
            assert result.returncode == 0, result.stderr
            assert "Apio CLI version" in result.stdout, result.stdout
