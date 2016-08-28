from os import environ, getcwd
from apio.commands.examples import cli as cmd_examples


def test_examples(clirunner, validate_cliresult):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_examples)
        validate_cliresult(result)


def test_examples_list(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_examples, ['--list'])
        assert result.exit_code == 1
        assert 'apio install examples' in result.output


def test_examples_dir(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_examples, ['--dir', 'dir'])
        assert result.exit_code == 1
        assert 'apio install examples' in result.output


def test_examples_files(clirunner):
    with clirunner.isolated_filesystem():
        environ['APIO_HOME_DIR'] = getcwd()
        result = clirunner.invoke(cmd_examples, ['--files', 'file'])
        assert result.exit_code == 1
        assert 'apio install examples' in result.output
