"""
Tests of the scons ApioEnv.
"""

from tests.unit_tests.scons.testing import make_test_apio_env


def test_env_platform_id():
    """Tests the env handling of the platform_id param."""

    # -- Test with a non windows platform id.
    env = make_test_apio_env(platform_id="darwin-arm64", is_windows=False)
    assert not env.is_windows

    # -- Test with a windows platform id.
    env = make_test_apio_env(platform_id="windows-amd64", is_windows=True)
    assert env.is_windows


def test_targeting_one_if():
    """Test the targeting_one_if() method."""

    # -- The test env targets 'build'.
    apio_env = make_test_apio_env()

    assert apio_env.targeting_one_of("build")
    assert apio_env.targeting_one_of("upload", "build")
    assert not apio_env.targeting_one_of("upload")
