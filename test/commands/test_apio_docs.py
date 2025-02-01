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
        result = sb.invoke_apio_cmd(apio, "docs")
        sb.assert_ok(result)
        assert "apio docs options" in cunstyle(result.output)
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio docs"  (pipe mode)
        result = sb.invoke_apio_cmd(apio, "docs", terminal_mode=False)
        sb.assert_ok(result)
        assert "apio docs options" in cunstyle(result.output)
        assert result.output == cunstyle(result.output)  # Colored.

        # -- Execute "apio docs options"
        result = sb.invoke_apio_cmd(apio, "docs", "options")
        assert result.exit_code == 0
        assert "BOARD (REQUIRED)" in cunstyle(result.output)
        assert "YOSYS-SYNTH-EXTRA-OPTIONS (OPTIONAL)" in cunstyle(
            result.output
        )
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio docs options board"
        result = sb.invoke_apio_cmd(apio, "docs", "options", "board")
        assert result.exit_code == 0
        assert "BOARD (REQUIRED)" in cunstyle(result.output)
        assert "YOSYS-SYNTH-EXTRA-OPTIONS (OPTIONAL)" not in cunstyle(
            result.output
        )
        assert result.output != cunstyle(result.output)  # Colored.

        # # -- Execute "apio docs resources"
        result = sb.invoke_apio_cmd(apio, "docs", "resources")
        assert result.exit_code == 0
        assert "Apio documentation" in result.output
        assert result.output != cunstyle(result.output)  # Colored.
