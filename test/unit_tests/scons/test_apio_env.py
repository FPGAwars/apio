"""
Tests of the scons ApioEnv.
"""

from test.unit_tests.scons.testing import make_test_apio_env
from test.conftest import ApioRunner
from apio.scons.apio_env import ApioEnv


def test_env_is_debug(apio_runner: ApioRunner):
    """Tests the env handling of the in_debug var."""

    with apio_runner.in_sandbox():

        env: ApioEnv = make_test_apio_env(debug_level=2)
        assert env.is_debug(1)
        assert env.is_debug(2)
        assert not env.is_debug(3)

        env: ApioEnv = make_test_apio_env(debug_level=0)
        assert not env.is_debug(1)
        assert not env.is_debug(2)
        assert not env.is_debug(3)


def test_env_platform_id():
    """Tests the env handling of the platform_id param."""

    # -- Test with a non windows platform id.
    env = make_test_apio_env(platform_id="darwin-arm64", is_windows=False)
    assert not env.is_windows

    # -- Test with a windows platform id.
    env = make_test_apio_env(platform_id="windows-amd64", is_windows=True)
    assert env.is_windows


def test_targeting():
    """Test the targeting() method."""

    # -- The test env targets 'build'.
    apio_env = make_test_apio_env()

    assert apio_env.targeting("build")
    assert apio_env.targeting("upload", "build")
    assert not apio_env.targeting("upload")
