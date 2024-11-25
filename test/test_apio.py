"""
Test for command apio
"""

from test.conftest import ApioRunner


# -----------------------------------------------------------------------
# -- RUN manually:
# --   pytest -v test/test_apio.py
# --
# -- DEBUG: if you want to add print traces for debuggin, execute this:
# --   pytest -v -s test/test_apio.py
# --
# -- ONLY ONE TEST: You can invoke only one test funcion:
# --    For example, it will only execute the test_apio() function
# --   pytest -v -s test/test_apio.py::test_apio
# ------------------------------------------------------------------------


# -- Import the cli entry point: apio/__main__.py
from apio.__main__ import cli as cmd_apio


def test_apio(apio_runner: ApioRunner):
    """Test command "apio" without arguments
    $ apio
    Usage: apio [OPTIONS] COMMAND [ARGS]...
    [...]
    """

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Invoke the apio command
        result = apio_runner.invoke(cmd_apio)

        # -- Check that everything is ok
        apio_runner.assert_ok(result)


def test_apio_wrong_command(apio_runner: ApioRunner):
    """Test apio command with an invalid command
    $ apio wrong
    Usage: apio [OPTIONS] COMMAND [ARGS]...
    Try 'apio --help' for help.

    Error: No such command 'wrong'.
    """

    with apio_runner.in_disposable_temp_dir():

        # -- Config the environment
        apio_runner.setup_env()

        # -- Execute "apio mmissing_command"
        result = apio_runner.invoke(cmd_apio, ["wrong_command"])

        # -- Check the error code
        assert result.exit_code == 2, result.output

        # -- Check the error message
        assert "Error: No such command" in result.output
