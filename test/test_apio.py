# -----------------------------------------------------------------------
# - Tests for command "apio"
#-- 
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

# -- Import the cli entry point: apio/__main__.py
from click.testing import CliRunner
from apio.__main__ import cli as cmd_apio


def test_apio(clirunner: CliRunner, validate_cliresult, configenv):

    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_apio)
        print(result)
        print(f"{result.exit_code=}")
        validate_cliresult(result)


def test_apio_wrong_command(clirunner: CliRunner, validate_cliresult, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_apio, ['missing_command'])
        assert result.exit_code == 2
        assert 'Error: No such command' in result.output
