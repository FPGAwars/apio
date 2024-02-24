"""
  Test for the "apio install" command
"""

# -- apio install entry point
from apio.commands.install import cli as cmd_install


def test_install(clirunner, configenv, validate_cliresult):
    """Test "apio install" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio install"
        result = clirunner.invoke(cmd_install)
        validate_cliresult(result)

        # -- Execute "apio install --list"
        result = clirunner.invoke(cmd_install, ['--list'])
        validate_cliresult(result)

        # -- Execute "apio install missing_package"
        result = clirunner.invoke(cmd_install, ['missing_package'])
        assert result.exit_code == 1
        assert 'Error: no such package' in result.output
