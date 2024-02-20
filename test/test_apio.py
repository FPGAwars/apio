"""
Test for command apio
"""
# -----------------------------------------------------------------------
#-- RUN manually:
#--   pytest -v test/test_apio.py
#--
#-- DEBUG: if you want to add print traces for debuggin, execute this:
#--   pytest -v -s test/test_apio.py
#--
#-- ONLY ONE TEST: You can invoke only one test funcion:
#--    For example, it will only execute the test_apio() function
#--   pytest -v -s test/test_apio.py::test_apio
#------------------------------------------------------------------------

from click.testing import CliRunner

# -- Import the cli entry point: apio/__main__.py
from apio.__main__ import cli as cmd_apio


def test_apio(clirunner: CliRunner, validate_cliresult, configenv):
    """Test command "apio" without arguments
    $ apio    
    Usage: apio [OPTIONS] COMMAND [ARGS]...
    [...]
    """

    with clirunner.isolated_filesystem():

        #-- Config the environment (conftest.configenv())
        configenv()

        #-- Invoke the apio command
        result = clirunner.invoke(cmd_apio)

        #-- Check that everything is ok
        validate_cliresult(result)


def test_apio_wrong_command(clirunner: CliRunner, configenv):
    """Test apio command with an invalid command
    $ apio wrong
    Usage: apio [OPTIONS] COMMAND [ARGS]...
    Try 'apio --help' for help.

    Error: No such command 'wrong'.
    """

    with clirunner.isolated_filesystem():

        #-- Config the environment
        configenv()

        #-- Execute "apio mmissing_command"
        result = clirunner.invoke(cmd_apio, ['wrong_command'])

        #-- Check the error code
        assert result.exit_code == 2

        #-- Check the error message
        assert 'Error: No such command' in result.output
