"""Test for the "apio boards" command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio

CUSTOM_BOARDS = """
{
  "my_custom_board": {
    "description": "My description",
    "fpga-id": "ice40up5k-sg48",
    "programmer": {
      "id": "iceprog"
    },
    "usb": {
      "vid": "0403",
      "pid": "6010",
      "product-regex": "^My Custom Board"
    }
  },
  "icebreaker": {
    "description": "iCEBreaker",
    "fpga-id": "custom-fpga",
    "programmer": {
      "id": "iceprog"
    },
    "usb": {
      "vid": "0403",
      "pid": "6010",
      "product-regex": "^(Dual RS232-HS)|(iCEBreaker.*)"
    }
  }
}
"""

CUSTOM_FPGAS = """
{
  "custom-fpga": {
    "part-num": "CUSTOM-FPGA",
    "arch": "ice40",
    "size": "5k",
    "type": "up5k",
    "pack": "sg48"
  }
}
"""


def test_boards_custom_board(apio_runner: ApioRunner):
    """Test boards listing with a custom boards.jsonc file."""

    with apio_runner.in_sandbox() as sb:

        # -- Write a custom boards.jsonc file in the project's directory.
        sb.write_file("fpgas.jsonc", CUSTOM_FPGAS)
        sb.write_file("boards.jsonc", CUSTOM_BOARDS)

        # -- Write an apio.ini file with the custom board.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "my_custom_board",
                    "top-module": "main",
                }
            }
        )

        # -- Execute "apio boards".
        # -- We should see also the custom board and the modified board..
        result = sb.invoke_apio_cmd(apio, ["boards"])
        sb.assert_result_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        assert "Loading custom 'boards.jsonc'" in result.output
        assert "alhambra-ii" in result.output
        assert "icebreaker" in result.output
        assert "my_custom_board" in result.output
        assert "CUSTOM-FPGA" in result.output

        # -- Execute "apio boards --docs"
        # -- With the --docs flag we ignore the custom board.
        result = sb.invoke_apio_cmd(apio, ["boards", "--docs"])
        sb.assert_result_ok(result)
        assert "Loading custom 'boards.jsonc'" not in result.output
        assert "FPGA" in result.output
        assert "alhambra-ii" in result.output
        assert "CUSTOM-FPGA" not in result.output


def test_boards_list_ok(apio_runner: ApioRunner):
    """Test normal board listing with the apio's boards.jsonc."""

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio boards'
        result = sb.invoke_apio_cmd(apio, ["boards"])
        sb.assert_result_ok(result)
        assert "Loading custom 'boards.jsonc'" not in result.output
        assert "FPGA-ID" not in result.output
        assert "alhambra-ii" in result.output
        assert "my_custom_board" not in result.output
        assert "Total of 1 board" not in result.output

        # -- Run 'apio boards -v'
        result = sb.invoke_apio_cmd(apio, ["boards", "-v"])
        sb.assert_result_ok(result)
        assert "Loading custom 'boards.jsonc'" not in result.output
        assert "FPGA-ID" in result.output
        assert "alhambra-ii" in result.output
        assert "my_custom_board" not in result.output
        assert "Total of 1 board" not in result.output

        # -- Run 'apio boards --docs'
        result = sb.invoke_apio_cmd(apio, ["boards", "--docs"])
        sb.assert_result_ok(result)
        assert "Loading custom 'boards.jsonc'" not in result.output
        assert "FPGA" in result.output
        assert "alhambra-ii" in result.output
        assert "my_custom_board" not in result.output
        assert "Total of 1 board" not in result.output
