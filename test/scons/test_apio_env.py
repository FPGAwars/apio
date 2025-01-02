"""
Tests of the scons ApioEnv.
"""

from test.scons.testing import make_test_apio_env


def test_env_args():
    """Tests the scons env args retrieval."""

    env = make_test_apio_env(
        args={
            "platform_id": "my_platform",
            "verbose_all": "True",
        }
    )

    # -- String args
    assert env.args.PLATFORM_ID == "my_platform"
    assert env.args.GRAPH_SPEC == ""

    # -- Bool args.
    assert env.args.VERBOSE_ALL
    assert not env.args.VERBOSE_YOSYS

    # -- Env var strings
    assert env.args.YOSYS_PATH == "fake yosys lib"
    assert env.args.TRELLIS_PATH == "fake trelis"


def test_env_platform_id():
    """Tests the env handling of the paltform_id var."""

    # -- Test with a non windows platform id.
    env = make_test_apio_env({"platform_id": "darwin_arm64"})
    assert not env.is_windows

    # -- Test with a windows platform id.
    env = make_test_apio_env({"platform_id": "windows_amd64"})
    assert env.is_windows


def test_targeting():
    """Test the targeting() method."""

    # -- The test env targets 'build'.
    apio_env = make_test_apio_env()

    assert apio_env.targeting("build")
    assert not apio_env.targeting("upload")
