"""
Tests of apio_context.py
"""

import re
from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope


# -- These programmers are known to be unused.
# -- https://github.com/FPGAwars/apio/issues/536
KNOWN_UNUSED_PROGRAMMERS = ["ujprog"]


def test_resources_references(apio_runner: ApioRunner):
    """Tests the consistency of the board references to fpgas and
    programmers."""

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

        unused_programmers = set(apio_ctx.programmers.keys())

        for board_name, board_info in apio_ctx.boards.items():
            # -- Prepare a context message for failing assertions.
            board_msg = f"While testing board {board_name}"

            # -- Assert that required fields exist.
            assert "fpga" in board_info, board_msg
            assert "programmer" in board_info, board_msg
            assert "type" in board_info["programmer"], board_msg

            # -- Check that the fpga exists.
            board_fpga = board_info["fpga"]
            assert apio_ctx.fpgas[board_fpga], board_msg

            # -- Check that the programmer exists.
            board_programmer_type = board_info["programmer"]["type"]
            assert apio_ctx.programmers[board_programmer_type], board_msg

            # -- Track unused programmers. Since a programmer may be used
            # -- by more than one board, it may already be removed.
            if board_programmer_type in unused_programmers:
                unused_programmers.remove(board_programmer_type)

        # -- Remove programmers that are known to be unused.
        for programmer in KNOWN_UNUSED_PROGRAMMERS:
            unused_programmers.remove(programmer)

        # -- We should end up with an empty set of unused programmers.
        assert not unused_programmers, unused_programmers


def test_resources_names(apio_runner: ApioRunner):
    """Tests the formats of boards, fpgas, and programmers names."""

    # -- For boards we allow lower-case-0-9.
    board_name_regex = re.compile(r"^[a-z][a-z0-9-]*$")

    # -- For fpga names we allow lower-case-0-9.
    fpga_name_regex = re.compile(r"^[a-z][a-z0-9-/]*$")

    # -- For programmer names we allow lower-case-0-9.
    programmer_name_regex = re.compile(r"^[a-z][a-z0-9-]*$")

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

        for board in apio_ctx.boards.keys():
            assert board_name_regex.match(board), f"{board=}"

        for fpga in apio_ctx.fpgas.keys():
            assert fpga_name_regex.match(fpga), f"{fpga=}"

        for programmer in apio_ctx.programmers.keys():
            assert programmer_name_regex.match(programmer), f"{programmer=}"


def test_fpga_definitions(apio_runner: ApioRunner):
    """Tests the fields of the fpga definitions."""

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

        for fpga_id, fpga_info in apio_ctx.fpgas.items():

            context = f"In fpga definition {fpga_id}"

            # -- Verify the "arch" field.
            assert "arch" in fpga_info, context
            arch = fpga_info["arch"]

            # -- Lattice
            if arch in ["ice40", "ecp5"]:
                assert fpga_info.keys() == {
                    "part_num",
                    "arch",
                    "size",
                    "type",
                    "pack",
                }, context
                assert fpga_info["part_num"], context
                assert fpga_info["arch"], context
                assert fpga_info["size"], context
                assert fpga_info["type"], context
                assert fpga_info["pack"], context
                continue

            # -- Gowin
            if arch == "gowin":
                assert fpga_info.keys() == {
                    "part_num",
                    "arch",
                    "size",
                    "type",
                }, context
                assert fpga_info["part_num"], context
                assert fpga_info["arch"], context
                assert fpga_info["size"], context
                assert fpga_info["type"], context
                continue

            # -- Unknown arch
            raise ValueError(f"Unknown arch value: {arch}")
