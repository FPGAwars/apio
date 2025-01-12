"""
Tests of apio_context.py
"""

import os
import re
from pathlib import Path
from test.conftest import ApioRunner
from pytest import LogCaptureFixture, raises
from apio.apio_context import ApioContext, ApioContextScope

# pylint: disable=fixme
# TODO: Add more tests.


def test_init(apio_runner: ApioRunner):
    """Tests the initialization of the apio context."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini file.
        sb.write_default_apio_ini()

        # -- Default init.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        assert apio_ctx.has_project

        # -- Verify context's project dir.
        assert str(apio_ctx.project_dir) == "."
        assert apio_ctx.project_dir.samefile(Path.cwd())
        assert apio_ctx.project_dir.samefile(sb.proj_dir)

        # -- Verify context's home and packages dirs.
        assert apio_ctx.home_dir == sb.home_dir
        assert apio_ctx.packages_dir == sb.packages_dir


def _test_home_dir_with_a_bad_character(
    invalid_char: str, apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """A helper function to test the initialization of the apio context with an
    invalid char in the home dir path."""

    with apio_runner.in_sandbox() as sb:

        # -- Make up a home dir path with the invalid char.
        invalid_home_dir = sb.sandbox_dir / f"apio-{invalid_char}-home"
        os.environ["APIO_HOME_DIR"] = str(invalid_home_dir)

        # -- Initialize an apio context. It shoudl exit with an error.
        with raises(SystemExit) as e:
            ApioContext(scope=ApioContextScope.NO_PROJECT)
        assert e.value.code == 1
        assert (
            f"Unsupported character [{invalid_char}]"
            in capsys.readouterr().out
        )


def test_home_dir_with_a_bad_character(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests the initialization of the apio context with home dirs that
    contain invalid chars."""
    for invalid_char in ["ó", "ñ", " ", "😼"]:
        _test_home_dir_with_a_bad_character(invalid_char, apio_runner, capsys)


def test_home_dir_with_relative_path(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Apio context should fail if the apio home dir is a relative path"""

    with apio_runner.in_sandbox():

        # -- Make up a home dir path with the invalid char.
        invalid_home_dir = Path("./aa/bb")
        os.environ["APIO_HOME_DIR"] = str(invalid_home_dir)

        # -- Initialize an apio context. It shoudl exit with an error.
        with raises(SystemExit) as e:
            ApioContext(scope=ApioContextScope.NO_PROJECT)
        assert e.value.code == 1
        assert (
            "Error: apio home dir should be an absolute path"
            in capsys.readouterr().out
        )


# -- This board is known to be problematic so we skip it.
# -- See https://github.com/FPGAwars/apio/issues/535
KNOWN_BAD_BOARDS = ["odt-rpga-feather"]

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
            # -- Skip boards that are known to be problematic.
            if board_name in KNOWN_BAD_BOARDS:
                continue

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
