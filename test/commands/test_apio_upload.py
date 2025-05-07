"""
  Test for the "apio upload" command
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


# pylint: disable=duplicate-code
def test_upload_without_apio_ini(apio_runner: ApioRunner):
    """Test: apio upload
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio upload"
        result = sb.invoke_apio_cmd(apio, "upload")

        # -- Check the result
        assert result.exit_code == 1, result.output
        assert "Error: Missing project file apio.ini" in result.output
