"""
  Test for the "apio boards" command
"""

# -- apio boards entry point
from apio.commands.boards import cli as cmd_boards


def test_boards(clirunner, configenv, validate_cliresult):
    """Test "apio boards" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio boards"
        result = clirunner.invoke(cmd_boards)
        validate_cliresult(result)

        # -- Execute "apio boards --list"
        result = clirunner.invoke(cmd_boards, ['--list'])
        validate_cliresult(result)

        # -- Execute "apio boards --fpga"
        result = clirunner.invoke(cmd_boards, ['--fpga'])
        validate_cliresult(result)
