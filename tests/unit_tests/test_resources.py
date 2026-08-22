"""
Tests of apio_context.py
"""

from tests.conftest import ApioRunner
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils.resource_util import validate_config, validate_packages


def test_resources_references(apio_runner: ApioRunner):
    """Tests the consistency of the board references to fpgas and
    programmers."""

    with apio_runner.in_sandbox():

        # -- Create an apio context so we can access the resources.
        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        unused_programmers = set(apio_ctx.definitions.programmers.keys())

        for board_id, board_info in apio_ctx.definitions.boards.items():
            # -- Prepare a context message for failing assertions.
            board_msg = f"While testing board {board_id}"

            # -- Assert that required fields exist.
            assert "fpga-id" in board_info, board_msg
            assert "programmer" in board_info, board_msg
            assert "id" in board_info["programmer"], board_msg

            # -- Check that the fpga exists.
            board_fpga_id = board_info["fpga-id"]
            assert apio_ctx.definitions.fpgas[board_fpga_id], board_msg

            # -- Check that the programmer exists.
            board_programmer_id = board_info["programmer"]["id"]
            assert apio_ctx.definitions.programmers[
                board_programmer_id
            ], board_msg

            # -- Track unused programmers. Since a programmer may be used
            # -- by more than one board, it may already be removed.
            if board_programmer_id in unused_programmers:
                unused_programmers.remove(board_programmer_id)

        # -- We should end up with an empty set of unused programmers.
        assert not unused_programmers, unused_programmers


def test_resources_are_valid(apio_runner: ApioRunner):
    """Validate resources against a schema."""
    with apio_runner.in_sandbox():

        apio_ctx = ApioContext(
            project_policy=ProjectPolicy.NO_PROJECT,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        validate_config(apio_ctx.config)
        validate_packages(apio_ctx.all_packages)
