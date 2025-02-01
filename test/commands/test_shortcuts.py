"""
  Test command shortcuts.
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_command_shortcuts(apio_runner: ApioRunner):
    """Test the apio root command."""

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio preferences list'
        # -- Exact match.
        result = sb.invoke_apio_cmd(apio, "preferences", "list")
        sb.assert_ok(result)
        assert "Colors" in result.output

        # -- Run 'apio pr list'
        # -- Unique match.
        result = sb.invoke_apio_cmd(apio, "pr", "list")
        sb.assert_ok(result)
        assert "Colors" in result.output

        # -- Run 'apio p list'
        # -- Ambagious match
        result = sb.invoke_apio_cmd(apio, "p", "list")
        assert result.exit_code != 0
        assert "'p' is ambagious: ['packages', 'preferences']" in result.output

        # -- Run 'apio xyz list'
        # -- No match
        result = sb.invoke_apio_cmd(apio, "xyz", "list")
        assert result.exit_code != 0
        assert "No such command 'xyz'" in result.output
