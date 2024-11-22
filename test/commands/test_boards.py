"""
  Test for the "apio boards" command
"""

# -- apio boards entry point
from apio.commands.boards import cli as cmd_boards

CUSTOM_BOARDS = """
{
  "my_custom_board": {
    "name": "My Custom Board v3.1c",
    "fpga": "iCE40-UP5K-SG48",
    "programmer": {
      "type": "iceprog"
    },
    "usb": {
      "vid": "0403",
      "pid": "6010"
    },
    "ftdi": {
      "desc": "My Custom Board"
    }
  }
}
"""


def test_list_ok(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test normal board listing with the apio's boards.json."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio boards"
        result = click_cmd_runner.invoke(cmd_boards)
        assert_apio_cmd_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'boards.json'" not in result.output
        assert "alhambra-ii" in result.output
        assert "my_custom_board" not in result.output
        assert "Total of 1 board" not in result.output


def test_custom_board(
    click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok
):
    """Test boards listing with a custom boards.json file."""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Write a custom boards.json file in the project's directory.
        with open("boards.json", "w", encoding="utf-8") as f:
            f.write(CUSTOM_BOARDS)

        # -- Execute "apio boards"
        result = click_cmd_runner.invoke(cmd_boards)
        assert_apio_cmd_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'boards.json'" in result.output
        assert "alhambra-ii" not in result.output
        assert "my_custom_board" in result.output
        assert "Total of 1 board" in result.output
