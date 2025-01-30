"""
Helpers for apio's scons testing."""

from typing import Dict, Optional, List
import SCons.Script.SConsOptions
import SCons.Node.FS
import SCons.Environment
import SCons.Defaults
import SCons.Script.Main
from google.protobuf import text_format
from apio.scons.apio_env import ApioEnv
from apio.common.proto.apio_pb2 import SconsParams, TargetParams

# R0801: Similar lines in 2 files
# pylint: disable=R0801

TEST_PARAMS = """
timestamp: "20123412052"
arch: ICE40
fpga_info {
  fpga_id: "ice40hx4k-tq144-8k"
  part_num: "ICE40HX4K-TQ144"
  size: "8k"
  ice40 {
    type: "hx8k"
    pack: "tq144:4k"
  }
}
verbosity {
  all: false
  synth: false
  pnr: false
}
envrionment {
  platform_id: "darwin_arm64"
  is_debug: true
  yosys_path: "/Users/user/.apio/packages/oss-cad-suite/share/yosys"
  trellis_path: "/Users/user/.apio/packages/oss-cad-suite/share/trellis"
}
project {
  board_id: "alhambra-ii"
  top_module: "main"
}
"""


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


def make_test_scons_params() -> SconsParams:
    """Create a frake scons params for testing."""
    return text_format.Parse(TEST_PARAMS, SconsParams())


def make_test_apio_env(
    *,
    targets: Optional[List[str]] = None,
    platform_id: str = None,
    is_windows: bool = None,
    is_debug: bool = None,
    target_params: TargetParams = None,
) -> ApioEnv:
    """Creates a fresh apio env for testing. The env is created
    with the current directory as the root dir.
    """
    # -- Specify both or nither.
    assert (platform_id is None) == (is_windows is None)

    # -- Bring scons to a starting state.
    SconsHacks.reset_scons_state()

    # -- Create default params.
    scons_params = make_test_scons_params()

    # -- Apply user overrides.
    if platform_id is not None:
        scons_params.envrionment.platform_id = platform_id
    if is_windows is not None:
        scons_params.envrionment.is_windows = is_windows
    if is_debug is not None:
        scons_params.envrionment.is_debug = is_debug
    if target_params is not None:
        scons_params.target.MergeFrom(target_params)

    # -- Determine scons target.
    if targets is not None:
        command_line_targets = targets
    else:
        command_line_targets = ["build"]

    # -- Create and return the apio env.
    return ApioEnv(
        command_line_targets=command_line_targets, scons_params=scons_params
    )
