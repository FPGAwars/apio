"""
Tests of apio_context.py
"""

import re
from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope, RemoteConfigPolicy
from apio.utils.resources_util import (
    ProjectResources,
    validate_board_info,
    validate_fpga_info,
    validate_programmer_info,
    validate_project_resources,
)


def lc_part_num(part_num: str) -> str:
    """Convert an fpga part number to a lower-case id."""
    return part_num.lower().replace("/", "-")


def test_resources_references(apio_runner: ApioRunner):
    """Tests the consistency of the board references to fpgas and
    programmers."""

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(
            scope=ApioContextScope.NO_PROJECT,
            config_policy=RemoteConfigPolicy.NO_CONFIG,
        )

        unused_programmers = set(apio_ctx.programmers.keys())

        for board_id, board_info in apio_ctx.boards.items():
            # -- Prepare a context message for failing assertions.
            board_msg = f"While testing board {board_id}"

            # -- Assert that required fields exist.
            assert "fpga-id" in board_info, board_msg
            assert "programmer" in board_info, board_msg
            assert "id" in board_info["programmer"], board_msg

            # -- Check that the fpga exists.
            board_fpga_id = board_info["fpga-id"]
            assert apio_ctx.fpgas[board_fpga_id], board_msg

            # -- Check that the programmer exists.
            board_programmer_id = board_info["programmer"]["id"]
            assert apio_ctx.programmers[board_programmer_id], board_msg

            # -- Track unused programmers. Since a programmer may be used
            # -- by more than one board, it may already be removed.
            if board_programmer_id in unused_programmers:
                unused_programmers.remove(board_programmer_id)

        # -- We should end up with an empty set of unused programmers.
        assert not unused_programmers, unused_programmers


def test_resources_ids_and_order(apio_runner: ApioRunner):
    """Tests the formats of boards, fpgas, and programmers names."""

    # -- For boards we allow lower-case-0-9.
    board_id_regex = re.compile(r"^[a-z][a-z0-9-]*$")

    # -- For fpga ids we allow lower-case-0-9.
    fpga_id_regex = re.compile(r"^[a-z][a-z0-9-/]*$")

    # -- For programmer ids we allow lower-case-0-9.
    programmer_id_regex = re.compile(r"^[a-z][a-z0-9-]*$")

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(
            scope=ApioContextScope.NO_PROJECT,
            config_policy=RemoteConfigPolicy.NO_CONFIG,
        )

        # -- Test the format of the board ids.
        for board_id in apio_ctx.boards.keys():
            assert board_id_regex.match(board_id), f"{board_id=}"

        # -- Test the format of the fpgas ids and part numbers.
        for fpga_id, fgpa_info in apio_ctx.fpgas.items():
            assert fpga_id_regex.match(fpga_id), f"{fpga_id=}"
            # Fpga id is either the fpga part num converted to lower-case
            # or its the lower-case part num with a suffix that starts with
            # '-'. E.g, for part num 'PART-NUM', the fpga id can be 'part-num'
            # or 'part-num-somethings'
            lc_part = lc_part_num(fgpa_info["part-num"])
            assert fpga_id == lc_part or fpga_id.startswith(
                lc_part + "-"
            ), f"{fpga_id=}"

        # -- Test the format of the programmers ids.
        for programmer_id in apio_ctx.programmers.keys():
            assert programmer_id_regex.match(
                programmer_id
            ), f"{programmer_id=}"


def test_resources_validation(apio_runner: ApioRunner):
    """Validate resources against a schema."""
    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            scope=ApioContextScope.NO_PROJECT,
            config_policy=RemoteConfigPolicy.CACHED_OK,
        )

        for board_id, board_info in apio_ctx.boards.items():
            validate_board_info(board_id, board_info)

        for fpga_id, fpga_info in apio_ctx.fpgas.items():
            validate_fpga_info(fpga_id, fpga_info)

        for programmer_id, programmer_info in apio_ctx.programmers.items():
            validate_programmer_info(programmer_id, programmer_info)

        # Now tests matching board/fpga/programmer as a project
        for board_id, board_info in apio_ctx.boards.items():
            fpga_id = board_info["fpga-id"]
            fpga_info = apio_ctx.fpgas[fpga_id]
            programmer_id = board_info["programmer"]["id"]
            programmer_info = apio_ctx.programmers[programmer_id]
            project_resources = ProjectResources(
                board_id=board_id,
                board_info=board_info,
                fpga_id=fpga_id,
                fpga_info=fpga_info,
                programmer_id=programmer_id,
                programmer_info=programmer_info,
            )
            validate_project_resources(project_resources)


def test_fpga_definitions(apio_runner: ApioRunner):
    """Tests the fields of the fpga definitions."""

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(
            scope=ApioContextScope.NO_PROJECT,
            config_policy=RemoteConfigPolicy.CACHED_OK,
        )

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
