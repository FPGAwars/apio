"""
Tests of the scons ApioEnv.
"""

from test.scons.testing import make_test_apio_env
from test.conftest import ApioRunner


def test_env_is_debug(apio_runner: ApioRunner):
    """Tests the env handling of the in_debug var."""

    with apio_runner.in_sandbox():

        env = make_test_apio_env(is_debug=True)
        assert env.is_debug

        env = make_test_apio_env(is_debug=False)
        assert not env.is_debug


def test_env_platform_id():
    """Tests the env handling of the platform_id param."""

    # -- Test with a non windows platform id.
    env = make_test_apio_env(platform_id="darwin_arm64", is_windows=False)
    assert not env.is_windows

    # -- Test with a windows platform id.
    env = make_test_apio_env(platform_id="windows_amd64", is_windows=True)
    assert env.is_windows


def test_targeting():
    """Test the targeting() method."""

    # -- The test env targets 'build'.
    apio_env = make_test_apio_env()

    assert apio_env.targeting("build")
    assert apio_env.targeting("upload", "build")
    assert not apio_env.targeting("upload")
