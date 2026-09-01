"""
Tests related to the openxc7 package's PARTS-INDEX.json file.
"""

import json
from tests.conftest import ApioRunner
from apio.apio_context import (
    ApioContext,
    ProjectPolicy,
    RemoteConfigPolicy,
    PackagesPolicy,
)
from apio.common.proto.apio_common_pb2 import ApioArch


def test_fpgas_yosys_part_num(apio_runner: ApioRunner):
    """Tests that all xilinx fpgas has a valid yosys-part value, that is,
    it's listed on PARTS-INDEX.json as a generated part."""

    with apio_runner.in_sandbox():

        # -- Create an ApioContext with access to Apio packages.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Read the parts index of the Apio's openxc7 package
        index_path = apio_ctx.get_package_dir("openxc7") / "PARTS-INDEX.json"
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        assert index_data["schema"] == 5, index_data["schema"]
        parts = index_data["parts"]

        # -- Iterate FPGA definitions and verify
        verified = 0
        for fpga_id, fpga_definition in apio_ctx.definitions.fpgas.items():
            # -- Skip if not a xilinx fpga
            arch = fpga_definition.arch
            if arch != ApioArch.xilinx:
                continue

            # -- FPGA is a xilinx FPGA. Make sure it's listed in the parts
            # -- index.
            assert fpga_id in parts, fpga_id
            part_info = parts[fpga_id]

            # -- Check that the fpga is generated.
            assert part_info["generated"], (fpga_id, part_info)
            verified += 1

        # -- Sanity check for the number of xilinx fpgas we verified.
        assert verified > 10, verified
