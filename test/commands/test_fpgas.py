"""
  Test for the "apio boards" command
"""

# -- apio fpgas entry point
from apio.commands.fpgas import cli as cmd_fpgas


def test_boards(clirunner, configenv, validate_cliresult):
    """Test "apio fpgas" command."""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio fpgas"
        result = clirunner.invoke(cmd_fpgas)
        validate_cliresult(result)
        assert "iCE40-HX4K-TQ144" in result.output
