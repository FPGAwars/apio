"""
  Test for the "apio format" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_format_without_apio_ini(apio_runner: ApioRunner):
    """Tests the apio format command with a missing apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio format" with no apio.ini
        result = sb.invoke_apio_cmd(apio, ["format"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output
