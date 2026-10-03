"""
Tests board/fpga/programmer definitions.
"""

import json
from tests.conftest import ApioRunner
from apio.common.proto.stubs.apio_common_pb2 import ApioArch
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)


def test_definitions_references(apio_runner: ApioRunner):
    """Tests the consistency of the board references to fpgas and
    programmers."""

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )
        assert apio_ctx.definitions is not None

        unused_programmers = set(apio_ctx.definitions.programmers.keys())

        for board_id, board_definition in apio_ctx.definitions.boards.items():
            # -- Prepare a context message for failing assertions.
            board_msg = f"While testing board {board_id}"

            # -- Check that the fpga exists.
            board_fpga_id = board_definition.fpga_id
            assert apio_ctx.definitions.fpgas[board_fpga_id], board_msg

            # -- Check that the programmer exists.
            board_programmer_id = board_definition.programmer.id
            assert apio_ctx.definitions.programmers[
                board_programmer_id
            ], board_msg

            # -- Track unused programmers. Since a programmer may be used
            # -- by more than one board, it may already be removed.
            if board_programmer_id in unused_programmers:
                unused_programmers.remove(board_programmer_id)

        # -- We should end up with an empty set of unused programmers.
        assert not unused_programmers, unused_programmers


def test_fpgas_yosys_part_num(apio_runner: ApioRunner):
    """Tests that all xilinx fpgas has a valid yosys-part value, that is,
    it's listed on XILINX-PARTS-INDEX.json as a generated part."""

    with apio_runner.in_sandbox():

        # -- Create an ApioContext with access to Apio packages.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        # -- Read the parts index of the Apio's openxc7 package
        index_path = (
            apio_ctx.get_package_dir("openxc7") / "XILINX-PARTS-INDEX.json"
        )
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
        assert index_data["schema"] == 8, index_data["schema"]
        parts = index_data["parts"]

        # -- Iterate FPGA definitions and verify
        verified = 0
        assert apio_ctx.definitions is not None
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
