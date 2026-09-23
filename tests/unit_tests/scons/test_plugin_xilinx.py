"""
Tests of the scons plugin_xilinx.py place and route builder.
"""

from google.protobuf import text_format
from tests.unit_tests.scons.testing import make_test_apio_env
from tests.conftest import ApioRunner
from apio.common.proto.apio_common_pb2 import ApioArch
from apio.common.proto.apio_scons_pb2 import FpgaInfo
from apio.scons.plugin_xilinx import PluginXilinx

# -- An xc7a35t (Artix-7, Arty A7-35T) FPGA info. chipdb_file_path is the
# -- file the parts index names for the part's die.
XILINX_FPGA_INFO = """
fpga_id: "xc7a35tcsg324-1"
part_num: "XC7A35T-1CSG324C"
size: "35k"
xilinx_params {
  yosys_family: "artix7"
  yosys_arch: "xc7"
  yosys_part: "xc7a35tcsg324-1"
  chipdb_file_path: "/chipdb/chipdb-xc7a50t.bin"
}
"""


def _pnr_action(
    apio_runner: ApioRunner,
    *,
    pnr_verbose: bool = False,
    extra_options: list[str] | None = None,
) -> str:
    """Returns the pnr command of a xilinx env."""
    with apio_runner.in_sandbox() as sb:
        sb.write_file("arty.xdc", "")
        apio_env = make_test_apio_env()
        apio_env.params.arch = ApioArch.xilinx
        apio_env.params.fpga_info.CopyFrom(
            text_format.Parse(XILINX_FPGA_INFO, FpgaInfo())
        )
        apio_env.params.verbosity.pnr = pnr_verbose
        if extra_options:
            apio_env.params.apio_env_params.nextpnr_extra_options.extend(
                extra_options
            )
        builder = PluginXilinx(apio_env).make_pnr_builder()
        return str(builder.action)


def test_pnr_builder(apio_runner: ApioRunner):
    """nextpnr-xilinx takes the full part as --device, the chipdb file of
    the part's die, and the xilinx outputs as uarch options."""
    action = _pnr_action(apio_runner)
    assert action.startswith(
        "nextpnr-xilinx --device xc7a35tcsg324-1 "
        "--chipdb /chipdb/chipdb-xc7a50t.bin "
    )
    assert "-o xdc=arty.xdc" in action
    assert "-o fasm=$TARGET" in action
    assert "--json $SOURCE" in action
    assert "--report _build/default/hardware.pnr" in action
    assert action.split()[-1] == "-q"
    assert "--xdc" not in action
    assert "--fasm" not in action


def test_pnr_builder_verbose(apio_runner: ApioRunner):
    """With pnr verbosity the command line has no -q."""
    action = _pnr_action(apio_runner, pnr_verbose=True)
    assert "-q" not in action.split()


def test_pnr_builder_extra_options(apio_runner: ApioRunner):
    """nextpnr-extra-options from apio.ini go at the end of the command."""
    action = _pnr_action(
        apio_runner, extra_options=["--seed", "7", "--router", "router2"]
    )
    assert action.endswith("-q --seed 7 --router router2")
