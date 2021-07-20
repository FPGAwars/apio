from apio.commands.system import cli as cmd_system


def test_system(clirunner, validate_cliresult, configenv):
    result = clirunner.invoke(cmd_system)
    validate_cliresult(result)


def test_system_lsftdi(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_system, ['--lsftdi'])
        assert result.exit_code == 1
        assert 'apio install oss-cad-suite' in result.output


def test_system_lsusb(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_system, ['--lsusb'])
        assert result.exit_code == 1
        assert 'apio install oss-cad-suite' in result.output


def test_system_lsserial(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        clirunner.invoke(cmd_system, ['--lsserial'])


def test_system_info(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_system, ['--info'])
        assert result.exit_code == 0
