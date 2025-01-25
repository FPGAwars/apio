"""
  Test for the "apio lint" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_lint_apio_init(apio_runner: ApioRunner):
    """Test: apio lint without an apio.ini project file."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio lint"
        result = sb.invoke_apio_cmd(apio, ["lint"])
        assert result.exit_code == 1, result.output
        assert "Error: Missing project file apio.ini" in result.output
