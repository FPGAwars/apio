from apio.commands.uninstall import cli as cmd_uninstall


def test_uninstall(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall)
    validate_cliresult(result)


def test_uninstall_list(clirunner, validate_cliresult, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_uninstall, ['--list'])
        validate_cliresult(result)


def test_uninstall_wrong_package(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(
            cmd_uninstall, ['missing_package'], input='y')
        assert result.exit_code == 1
        assert 'Do you want to continue?' in result.output
        assert 'Error: no such package' in result.output
