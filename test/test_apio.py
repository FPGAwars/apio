"""
Test for command apio
"""

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

from click.testing import CliRunner

# -- Import the cli entry point: apio/__main__.py
from apio.__main__ import cli as cmd_apio


def test_apio(
    click_cmd_runner: CliRunner, assert_apio_cmd_ok, setup_apio_test_env
):
    """Test command "apio" without arguments
    $ apio
    Usage: apio [OPTIONS] COMMAND [ARGS]...
    [...]
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Invoke the apio command
        result = click_cmd_runner.invoke(cmd_apio)

        # -- Check that everything is ok
        assert_apio_cmd_ok(result)


def test_apio_wrong_command(click_cmd_runner: CliRunner, setup_apio_test_env):
    """Test apio command with an invalid command
    $ apio wrong
    Usage: apio [OPTIONS] COMMAND [ARGS]...
    Try 'apio --help' for help.

    Error: No such command 'wrong'.
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the environment
        setup_apio_test_env()

        # -- Execute "apio mmissing_command"
        result = click_cmd_runner.invoke(cmd_apio, ["wrong_command"])

        # -- Check the error code
        assert result.exit_code == 2, result.output

        # -- Check the error message
        assert "Error: No such command" in result.output
