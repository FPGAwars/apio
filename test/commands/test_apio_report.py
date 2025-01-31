"""
  Test for the "apio report" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_report_no_apio(apio_runner: ApioRunner):
    """Tests the apio report command without an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio report" without apio.ini
        result = sb.invoke_apio_cmd(apio, ["report"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output
