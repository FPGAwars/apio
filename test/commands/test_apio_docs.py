"""
  Test for the "apio docs" command
"""

from test.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import cli as apio


def test_apio_docs(apio_runner: ApioRunner):
    """Tests the apio docs commands."""

    with apio_runner.in_sandbox() as sb:
        # -- Execute "apio docs"
        result = sb.invoke_apio_cmd(apio, ["docs"])
        sb.assert_ok(result)
        assert "apio docs apio.ini" in cunstyle(result.output)
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio docs"  (pipe mode)
        result = sb.invoke_apio_cmd(apio, ["docs"], terminal_mode=False)
        sb.assert_ok(result)
        assert "apio docs apio.ini" in cunstyle(result.output)
        assert result.output == cunstyle(result.output)  # Colored.

        # -- Execute "apio docs apio.ini"
        result = sb.invoke_apio_cmd(apio, ["docs", "apio.ini"])
        assert result.exit_code == 0
        assert "BOARD (REQUIRED)" in result.output
        assert "YOSYS-SYNTH-EXTRA-OPTIONS (OPTIONAL)" in result.output

        # # -- Execute "apio docs resources"
        result = sb.invoke_apio_cmd(apio, ["docs", "resources"])
        sb.assert_ok(result)
