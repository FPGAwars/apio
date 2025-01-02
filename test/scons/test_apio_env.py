"""
Tests of the scons ApioEnv.
"""

import os
from typing import Dict
import SCons.Script.SConsOptions
import SCons.Node.FS
import SCons.Environment
import SCons.Defaults
import SCons.Script.Main
from apio.scons.apio_env import ApioEnv

# pylint: disable=fixme
# TODO: Move SconsHacks and make_test_apio_env to a share testing file.


class SconsHacks:
    """A collection of staticmethods that encapsulate scons access outside of
    the official scons API. Hopefully this will not be too difficult to adapt
    in future versions of SCons."""

    @staticmethod
    def reset_scons_state() -> None:
        """Reset the relevant SCons global variables. וUnfurtunally scons
        uses a few global variables to hold its state. This works well in
        normal operation where an scons process contains a single scons
        session but with pytest testing, where multiple independent tests
        are running in the same process, we need to reset though variables
        before each test."""

        # -- The Cons.Script.Main.OptionsParser variables contains the command
        # -- line options of scons. We reset them here and tests can access
        # -- them using SetOption() and GetOption().

        parser = SCons.Script.SConsOptions.Parser("my_fake_version")
        values = SCons.Script.SConsOptions.SConsValues(
            parser.get_default_values()
        )
        parser.parse_args(args=[], values=values)
        SCons.Script.Main.OptionsParser = parser

        # -- Reset the scons target list variable.
        SCons.Node.FS.default_fs = None

        # -- Clear the SCons targets
        SCons.Environment.CleanTargets = {}

    @staticmethod
    def get_targets() -> Dict:
        """Get the scons {target -> dependencies} dictionary."""
        return SCons.Environment.CleanTargets


def make_test_apio_env(
    args: Dict[str, str] = None, extra_args: Dict[str, str] = None
) -> ApioEnv:
    """Creates a fresh apio env with given args. The env is created
    with the current directory as the root dir.
    """

    # -- Bring scons to a starting state.
    SconsHacks.reset_scons_state()

    # -- Default, when we don't really care about the content.
    if args is None:
        args = {
            "platform_id": "darwin_arm64",
        }

    # -- If specified, overite/add extra args.
    if extra_args:
        args.update(extra_args)

    # -- Setup required env vars.
    os.environ["YOSYS_LIB"] = "fake yosys lib"
    os.environ["TRELLIS"] = "fake trelis"

    # -- Create and return the apio env.
    return ApioEnv(
        scons_args=args,
        command_line_targets=["build"],
        is_debug=False,
    )


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
