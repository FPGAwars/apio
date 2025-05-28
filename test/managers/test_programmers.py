"""
Tests of the apio.managers.programmers.py module.
"""

from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope
from apio.managers.programmers import _construct_programmer_cmd_template


def test_construct_programmer_cmd_template(apio_runner: ApioRunner):
    """Tests _construct_programmer_cmd_template() with default arguments."""

    with apio_runner.in_sandbox() as sb:

        # -- Construct an apio context.
        sb.write_apio_ini(
            {
                "[env:default]": {
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
        )

        # -- Check the command.
        assert programmer_cmd == "iceprog -d i:0x${VID}:0x${PID} $SOURCE"
