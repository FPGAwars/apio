"""
Tests of the scons plugin_xilinx.py place and route builder.
"""

from google.protobuf import text_format
from tests.unit_tests.scons.testing import make_test_apio_env
from tests.conftest import ApioRunner
from apio.common.proto.apio_common_pb2 import ApioArch
from apio.common.proto.apio_scons_pb2 import FpgaInfo
from apio.scons.plugin_xilinx import PluginXilinx

# -- An xc7vx485t (Virtex-7, VC707) FPGA info. pnr_tool is left for each test.
XILINX_FPGA_INFO = """
fpga_id: "xc7vx485tffg1761-2"
part_num: "XC7VX485T-2FFG1761"
size: "485k"
xilinx_params {
  yosys_family: "virtex7"
  yosys_arch: "xc7"
  yosys_part: "xc7vx485tffg1761-2"
  chipdb_file_path: "/chipdb/xc7vx485t.bin"
}
"""


def _pnr_action(apio_runner: ApioRunner, pnr_tool: str) -> str:
    """Returns the pnr command of a xilinx env using the given tool
    ('' for none, as a parts index without the field gives)."""
    with apio_runner.in_sandbox() as sb:
        sb.write_file("vc707.xdc", "")
        apio_env = make_test_apio_env()
        apio_env.params.arch = ApioArch.xilinx
        apio_env.params.fpga_info.CopyFrom(
            text_format.Parse(XILINX_FPGA_INFO, FpgaInfo())
        )
        if pnr_tool:
            apio_env.params.fpga_info.xilinx_params.pnr_tool = pnr_tool
        builder = PluginXilinx(apio_env).make_pnr_builder()
        return str(builder.action)


def test_pnr_builder_himbaechel(apio_runner: ApioRunner):
    """A part whose chipdb is for nextpnr-himbaechel runs that tool, with the
    full part as --device and the xilinx outputs as uarch options."""
    action = _pnr_action(apio_runner, "nextpnr-himbaechel")
    assert action.startswith("nextpnr-himbaechel ")
    assert "--chipdb /chipdb/xc7vx485t.bin" in action
    assert "--device xc7vx485tffg1761-2" in action
    assert "-o xdc=vc707.xdc" in action
    assert "-o fasm=$TARGET" in action
    assert "--xdc" not in action
    assert "--fasm" not in action


def test_pnr_builder_legacy_default(apio_runner: ApioRunner):
    """A part whose index entry names no tool keeps nextpnr-xilinx, with
    exactly the command line apio has always used."""
    for pnr_tool in ("", "nextpnr-xilinx"):
        action = _pnr_action(apio_runner, pnr_tool)
        assert action.startswith(
            "nextpnr-xilinx --chipdb /chipdb/xc7vx485t.bin "
        )
        assert "--xdc vc707.xdc" in action
        assert "--fasm $TARGET" in action
        assert "--device" not in action
