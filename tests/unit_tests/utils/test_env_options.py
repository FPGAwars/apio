"""
Tests of env_options.py
"""

import os
import pytest
from tests.conftest import ApioRunner
from apio.utils import env_options
from apio.utils.env_options import (
    APIO_HOME,
    APIO_PLATFORM,
    APIO_DEBUG,
)


def test_get_all():
    """Tests the list of supported env vars."""
    # -- Make an independent copy so the test doesn't rely on get_all()
    # -- returning a copy.
    all_vars = env_options.get_all().copy()

    # -- Spot check a few vars.
    assert APIO_HOME in all_vars
    assert APIO_DEBUG in all_vars

    # -- All vars have the apio prefix.
    for var in all_vars:
        assert var.startswith("APIO_"), var

    # -- There are no duplicates.
    assert len(set(all_vars)) == len(all_vars)

    # -- The returned list is a copy, mutating it has no effect.
    env_options.get_all().clear()
    assert env_options.get_all() == all_vars


def test_get(apio_runner: ApioRunner):
    """Tests the get() function."""

    # -- The sandbox restores the system env on exit.
    with apio_runner.in_sandbox():

        # -- Undefined var returns the default.
        os.environ.pop(APIO_HOME, None)
        assert env_options.get(APIO_HOME) is None
        assert env_options.get(APIO_HOME, "my-default") == "my-default"

        # -- Defined var returns its value, ignoring the default.
        os.environ[APIO_HOME] = "/my/home"
        assert env_options.get(APIO_HOME) == "/my/home"
        assert env_options.get(APIO_HOME, "my-default") == "/my/home"

        # -- Surrounding quotes are removed (for the benefit of Windows).
        os.environ[APIO_HOME] = '"/my/home"'
        assert env_options.get(APIO_HOME) == "/my/home"


def test_get_unbalanced_quotes(apio_runner: ApioRunner):
    """Tests that a value with a leading double quote and no trailing one,
    or a trailing double quote and no leading one, is an error."""

    # -- The sandbox restores the system env on exit.
    with apio_runner.in_sandbox():
        for value in ['"', '"aa', '"aa"bb', 'aa"', 'bb"aa"']:
            os.environ[APIO_HOME] = value
            with apio_runner.with_logger() as log:
                with pytest.raises(SystemExit) as e:
                    env_options.get(APIO_HOME)
            assert e.value.code == 1, value
            assert (
                "Env var APIO_HOME has unbalanced double quotes" in log.out
            ), value


def test_get_unknown_var():
    """Tests that get() rejects vars that apio doesn't know about."""
    with pytest.raises(AssertionError, match="Unknown apio env var"):
        env_options.get("APIO_NO_SUCH_VAR")


def test_is_defined(apio_runner: ApioRunner):
    """Tests the is_defined() function."""

    # -- The sandbox restores the system env on exit.
    with apio_runner.in_sandbox():

        # -- Undefined var.
        os.environ.pop(APIO_PLATFORM, None)
        assert not env_options.is_defined(APIO_PLATFORM)

        # -- Defined var.
        os.environ[APIO_PLATFORM] = "linux-x86-64"
        assert env_options.is_defined(APIO_PLATFORM)

        # -- An empty value still counts as defined.
        os.environ[APIO_PLATFORM] = ""
        assert env_options.is_defined(APIO_PLATFORM)


def test_get_defined(apio_runner: ApioRunner):
    """Tests the get_defined() function."""

    # -- The sandbox restores the system env on exit.
    with apio_runner.in_sandbox():

        # -- Start with all the apio vars undefined. The sandbox defines
        # -- some of them.
        for var in env_options.get_all():
            os.environ.pop(var, None)
        assert not env_options.get_defined()

        # -- Define two vars. They are returned in the order of get_all().
        os.environ[APIO_DEBUG] = "1"
        os.environ[APIO_HOME] = "/my/home"
        assert env_options.get_defined() == [APIO_HOME, APIO_DEBUG]
