"""
  Test for the "apio examples" command
"""

# -- apio examples entry point
from apio.commands.examples import cli as cmd_examples


def test_examples(clirunner, validate_cliresult, configenv):
    """Test "apio examples" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio examples"
        result = clirunner.invoke(cmd_examples)
        validate_cliresult(result)

        # -- Execute "apio examples --list"
        result = clirunner.invoke(cmd_examples, ['--list'])
        assert result.exit_code == 1
        assert 'apio install examples' in result.output

        # -- Execute "apio examples --dir dir"
        result = clirunner.invoke(cmd_examples, ['--dir', 'dir'])
        assert result.exit_code == 1
        assert 'apio install examples' in result.output

        # -- Execute "apio examples --files file"
        result = clirunner.invoke(cmd_examples, ['--files', 'file'])
        assert result.exit_code == 1
        assert 'apio install examples' in result.output
