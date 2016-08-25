import os

from apio.commands.install import cli as cmd_install
from apio.commands.uninstall import cli as cmd_uninstall


def test_install(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_install)
    validate_cliresult(result)


def test_install_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_install, ['--list'])
    validate_cliresult(result)


def test_install_wrong_package(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_install, ['missing_package'])
    assert result.exit_code == 0
    assert 'Error: No such package' in result.output


def test_uninstall(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall)
    validate_cliresult(result)


def test_uninstall_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_uninstall, ['--list'])
    validate_cliresult(result)


def test_uninstall_examples(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        os.environ["APIO_HOME_DIR"] = os.getcwd()
        result = clirunner.invoke(cmd_uninstall, ['examples'])
        validate_cliresult(result)
        assert 'Do you want to continue?' in result.output
        # TODO: [y/N] test


def test_complex(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        os.environ["APIO_HOME_DIR"] = os.getcwd()

        # apio install examples
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert all([
                    s in result.output
                    for s in ('Installing examples package', 'Downloading',
                              'Unpacking', 'has been successfully installed!')
        ])

        # apio install examples
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert all([
                    s in result.output
                    for s in ('Installing examples package',
                              'Already installed. Version')
        ])

        # apio uninstall examples
        result = clirunner.invoke(cmd_uninstall, ['examples'])
        validate_cliresult(result)
        assert 'Do you want to continue?' in result.output
        # TODO: [y/N] test
