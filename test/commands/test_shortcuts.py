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
        assert "Theme" in result.output
        assert "light" in result.output

        # -- Run 'apio pr list -xyz'
        # -- Unique match.
        result = sb.invoke_apio_cmd(apio, "pr", "list", "-xyz")
        assert result.exit_code != 0
        assert "Usage: apio preferences list" in result.output

        # -- Run 'apio pr li -h'
        # -- Help text should contain full commands..
        result = sb.invoke_apio_cmd(apio, "pr", "li", "-h")
        sb.assert_ok(result)
        assert "Usage: apio preferences list" in result.output

        # -- Run 'apio p list'
        # -- Ambiguous match
        result = sb.invoke_apio_cmd(apio, "p", "list")
        assert result.exit_code != 0
        assert "'p' is ambagious: ['packages', 'preferences']" in result.output

        # -- Run 'apio xyz list'
        # -- No match
        result = sb.invoke_apio_cmd(apio, "xyz", "list")
        assert result.exit_code != 0
        assert "No such command 'xyz'" in result.output
