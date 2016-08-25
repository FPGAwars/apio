import os

from apio.commands.install import cli as cmd_install


def test_install_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_install, ['--list'])
    validate_cliresult(result)


def test_install_examples(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        os.environ["APIO_HOME_DIR"] = os.getcwd()
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert all([
                    s in result.output
                    for s in ('Installing examples package', 'Downloading',
                              'Unpacking', 'has been successfully installed!')
        ])
