"""
Tests of the scons manager scons.py
"""

from test.conftest import ApioRunner
from google.protobuf import text_format
from apio.common.proto.apio_pb2 import (
    SconsParams,
    Verbosity,
    TargetParams,
    LintParams,
)
from apio.apio_context import ApioContext, ApioContextScope
from apio.managers.scons import SCons


TEST_APIO_INI_DICT = {
    "[env:default]": {
        # -- Required.
        "board": "alhambra-ii",
        # -- Optional.
        "top-module": "my_module",
        "format-verible-options": "\n  --aaa bbb\n  --ccc ddd",
        "yosys-synth-extra-options": "-dsp -xyz",
    }
}

# -- The non determinisitc values marked with TBD are patched by the test
# -- at runtime.
EXPECTED1 = """
timestamp: "TBD"
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
environment {
  platform_id: "TBD"
  is_windows: true  # TBD
  terminal_mode: FORCE_TERMINAL
  theme_name: "light"
  debug_level: 0
  yosys_path: "TBD"
  trellis_path: "TBD"
}
apio_env_params {
  env_name: "default"
  board_id: "alhambra-ii"
  top_module: "my_module"
  yosys_synth_extra_options: "-dsp -xyz"
}
"""

EXPECTED2 = """
timestamp: "TBD"
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
  all: true
  synth: true
  pnr: true
}
environment {
  platform_id: "TBD"
  is_windows: true  # TBD
  terminal_mode: FORCE_TERMINAL
  theme_name: "light"
  debug_level: 0
  yosys_path: "TBD"
  trellis_path: "TBD"
}
apio_env_params {
  env_name: "default"
  board_id: "alhambra-ii"
  top_module: "my_module"
  yosys_synth_extra_options: "-dsp -xyz"
}
target {
  lint {
    top_module: "my_module"
    verilator_all: true
    verilator_no_style: true
    verilator_no_warns: "aa"
    verilator_no_warns: "bb"
    verilator_warns: "cc"
    verilator_warns: "dd"
  }
}
"""


def test_default_params(apio_runner: ApioRunner):
    """Tests the construct_scons_params() with default values."""

    with apio_runner.in_sandbox() as sb:

        # -- Setup a Scons object.
        sb.write_apio_ini(TEST_APIO_INI_DICT)
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        scons = SCons(apio_ctx)

        # -- Get the actual value.
        scons_params = scons.construct_scons_params()

        # -- Construct the expected value. We fill in non deterministic values.
        expected = text_format.Parse(EXPECTED1, SconsParams())
        expected.timestamp = scons_params.timestamp
        expected.environment.platform_id = apio_ctx.platform_id
        expected.environment.is_windows = apio_ctx.is_windows
        expected.environment.yosys_path = str(
            sb.packages_dir / "oss-cad-suite/share/yosys"
        )
        expected.environment.trellis_path = str(
            sb.packages_dir / "oss-cad-suite/share/trellis"
        )

        # The field rich_lib_windows_params is too dynamic so we just assert
        # for its existence and remove it from the comparison.
        # if apio_ctx.is_windows:
        #     assert scons_params.HasField(
        #         "rich_lib_windows_params"
        #     ), scons_params
        # else:
        #     assert not scons_params.HasField(
        #         "rich_lib_windows_params"
        #     ), scons_params
        # scons_params.ClearField("rich_lib_windows_params")

        # -- Compare actual to expected values.
        assert str(scons_params) == str(expected)


def test_explicit_params(apio_runner: ApioRunner):
    """Tests the construct_scons_params() method with values override.."""

    with apio_runner.in_sandbox() as sb:

        # -- Setup a Scons object.
        sb.write_apio_ini(TEST_APIO_INI_DICT)
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        scons = SCons(apio_ctx)

        # -- Get the actual value.
        target_params = TargetParams(
            lint=LintParams(
                top_module="my_module",
                verilator_all=True,
                verilator_no_style=True,
                verilator_no_warns=["aa", "bb"],
                verilator_warns=["cc", "dd"],
            )
        )
        verbosity = Verbosity(all=True, synth=True, pnr=True)
        scons_params = scons.construct_scons_params(
            verbosity=verbosity, target_params=target_params
        )

        # -- Construct the expected value. We fill in non deterministic values.
        expected = text_format.Parse(EXPECTED2, SconsParams())
        expected.timestamp = scons_params.timestamp
        expected.environment.platform_id = apio_ctx.platform_id
        expected.environment.is_windows = apio_ctx.is_windows
        expected.environment.yosys_path = str(
            sb.packages_dir / "oss-cad-suite/share/yosys"
        )
        expected.environment.trellis_path = str(
            sb.packages_dir / "oss-cad-suite/share/trellis"
        )

        # The field rich_lib_windows_params is too dynamic so we just assert
        # for its existence and remove it from the comparison.
        # if apio_ctx.is_windows:
        #     assert scons_params.HasField(
        #         "rich_lib_windows_params"
        #     ), scons_params
        # else:
        #     assert not scons_params.HasField(
        #         "rich_lib_windows_params"
        #     ), scons_params
        # scons_params.ClearField("rich_lib_windows_params")

        # -- Compare actual to expected values.
        assert str(scons_params) == str(expected)
