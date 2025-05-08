"""
Tests of the apio.managers.programmers.py module.
"""

from test.conftest import ApioRunner
from pytest import LogCaptureFixture, raises
from apio.apio_context import ApioContext, ApioContextScope
from apio.managers.programmers import _construct_programmer_cmd_template


def test_construct_programmer_cmd_template(apio_runner: ApioRunner):
    """Tests _construct_programmer_cmd_template() with default arguments."""

    with apio_runner.in_sandbox() as sb:

        # -- Construct an apio context.
        sb.write_apio_ini(
            {
                "[env]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                }
            }
        )
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        board_info = apio_ctx.boards.get(apio_ctx.project.get("board"))
        assert board_info["programmer"]["type"] == "iceprog"

        # -- Run the test with default arguments.
        programmer_cmd = _construct_programmer_cmd_template(
            apio_ctx=apio_ctx,
            board_info=board_info,
            sram=False,
        )

        # -- Check the command.
        assert (
            programmer_cmd
            == "iceprog -d i:0x${VID}:0x${PID}:${FTDI_IDX} $SOURCE"
        )


def test_construct_programmer_cmd_template_sram_ok(apio_runner: ApioRunner):
    """Tests _construct_programmer_cmd_template() with --sram ok."""

    with apio_runner.in_sandbox() as sb:

        # -- Construct an apio context.
        sb.write_apio_ini(
            {
                "[env]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                }
            }
        )
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        board_info = apio_ctx.boards.get(apio_ctx.project.get("board"))
        assert board_info["programmer"]["type"] == "iceprog"

        # -- Run the test with --sram.
        programmer_cmd = _construct_programmer_cmd_template(
            apio_ctx=apio_ctx,
            board_info=board_info,
            sram=True,  # -- SRAM is enabled
        )

        # Notice the additional -S for SRAM.
        assert (
            programmer_cmd
            == "iceprog -d i:0x${VID}:0x${PID}:${FTDI_IDX} $SOURCE -S"
        )


def test_construct_programmer_cmd_template_sram_error(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests _construct_programmer_cmd_template() with --sram error."""

    with apio_runner.in_sandbox() as sb:

        # -- Construct an apio context with a board that does not
        # -- support the flag --sram.
        sb.write_apio_ini(
            {
                "[env]": {
                    "board": "colorlight-5a-75b-v7",
                    "top-module": "my_module",
                }
            }
        )
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        board_info = apio_ctx.boards.get(apio_ctx.project.get("board"))
        assert board_info["programmer"]["type"] == "openfpgaloader"

        # -- Run the test with --sram.
        with raises(SystemExit) as e:
            _construct_programmer_cmd_template(
                apio_ctx=apio_ctx,
                board_info=board_info,
                sram=True,  # -- SRAM is enabled
            )

        # -- Check the error message.
        assert e.value.code == 1
        assert (
            "Error: The --sram flag is not available for the "
            "openfpgaloader programmer." in capsys.readouterr().out
        )
