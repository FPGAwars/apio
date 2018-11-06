from apio.commands.install import cli as cmd_install


def test_install(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_install)
    validate_cliresult(result)


def test_install_list(clirunner, validate_cliresult, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_install, ['--list'])
        validate_cliresult(result)


def test_install_wrong_package(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_install, ['missing_package'])
        assert result.exit_code == 1
        assert 'Error: no such package' in result.output
