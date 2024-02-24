"""
  Test for the "apio uninstall" command
"""

# -- apio uninstall entry point
from apio.commands.uninstall import cli as cmd_uninstall


def test_uninstall(clirunner, configenv, validate_cliresult):
    """Test "apio uninstall" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio uninstall"
        result = clirunner.invoke(cmd_uninstall)
        validate_cliresult(result)

        # -- Execute "apio uninstall --list"
        result = clirunner.invoke(cmd_uninstall, ['--list'])
        validate_cliresult(result)

        # -- Execute "apio uninstall missing_packge"
        result = clirunner.invoke(
            cmd_uninstall, ['missing_package'], input='y')
        assert result.exit_code == 1
        assert 'Do you want to continue?' in result.output
        assert 'Error: no such package' in result.output
