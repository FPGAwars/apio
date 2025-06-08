"""
Tests of apio_context.py
"""

import re
from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope


def lc_part_num(part_num: str) -> str:
    """Convert an fpga part number to a lower-case id."""
    return part_num.lower().replace("/", "-")


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

        for fpga_id, fgpa_info in apio_ctx.fpgas.items():
            assert fpga_name_regex.match(fpga_id), f"{fpga_id=}"
            # Fpga id is either the fpga part num converted to lower-case
            # or its the lower-case part num with a suffix that starts with
            # '-'. E.g, for part num 'PART-NUM', the fpga id can be 'part-num'
            # or 'part-num-somethings'
            lc_part = lc_part_num(fgpa_info["part-num"])
            assert fpga_id == lc_part or fpga_id.startswith(
                lc_part + "-"
            ), f"{fpga_id=}"

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

            # -- Ice40
            if arch == "ice40":
                assert fpga_info.keys() == {
                    "part-num",
                    "arch",
                    "size",
                    "type",
                    "pack",
                }, context
                assert fpga_info["part-num"], context
                assert fpga_info["arch"], context
                assert fpga_info["size"], context
                assert fpga_info["type"], context
                assert fpga_info["pack"], context
                continue

            # -- Ecp5
            if arch == "ecp5":
                assert set(fpga_info.keys()) == {
                    "part-num",
                    "arch",
                    "size",
                    "type",
                    "pack",
                    "speed",
                }, context
                assert fpga_info["part-num"], context
                assert fpga_info["arch"], context
                assert fpga_info["size"], context
                assert fpga_info["type"], context
                assert fpga_info["pack"], context
                assert fpga_info["speed"], context
                continue

            # -- Gowin
            if arch == "gowin":
                assert fpga_info.keys() == {
                    "part-num",
                    "arch",
                    "size",
                    "type",
                }, context
                assert fpga_info["part-num"], context
                assert fpga_info["arch"], context
                assert fpga_info["size"], context
                assert fpga_info["type"], context
                continue

            # -- Unknown arch
            raise ValueError(f"Unknown arch value: {arch}")
