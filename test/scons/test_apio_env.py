"""
Tests of the scons ApioEnv.
"""

from test.scons.testing import make_test_apio_env


def test_env_is_debug():
    """Tests the env handling of the in_debug var."""

    env = make_test_apio_env(is_debug=True)
    assert env.is_debug

    env = make_test_apio_env(is_debug=False)
    assert not env.is_debug


def test_env_platform_id():
    """Tests the env handling of the paltform_id param."""

    # -- Test with a non windows platform id.
    env = make_test_apio_env(platform_id="darwin_arm64")
    assert not env.is_windows

    # -- Test with a windows platform id.
    env = make_test_apio_env(platform_id="windows_amd64")
    assert env.is_windows


def test_targeting():
    """Test the targeting() method."""

    # -- The test env targets 'build'.
    apio_env = make_test_apio_env()

    assert apio_env.targeting("build")
    assert apio_env.targeting("upload", "build")
    assert not apio_env.targeting("upload")
