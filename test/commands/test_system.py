"""
  Test for the "apio system" command
"""

# -- apio system entry point
from apio.commands.system import cli as cmd_system


def test_system(clirunner, validate_cliresult, configenv):
    """Test "apio system" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio system"
        result = clirunner.invoke(cmd_system)
        validate_cliresult(result)

        # -- Execute "apio system --lsftdi"
        result = clirunner.invoke(cmd_system, ['--lsftdi'])
        assert result.exit_code == 1
        assert 'apio install oss-cad-suite' in result.output

        # -- Execute "apio system --lsusb"
        result = clirunner.invoke(cmd_system, ['--lsusb'])
        assert result.exit_code == 1
        assert 'apio install oss-cad-suite' in result.output

        # -- Execute "apio system --lsserial"
        clirunner.invoke(cmd_system, ['--lsserial'])
        assert result.exit_code == 1
        assert 'apio install oss-cad-suite' in result.output

        # -- Execute "apio system --info"
        result = clirunner.invoke(cmd_system, ['--info'])
        assert result.exit_code == 0
        assert "Platform:" in result.output
