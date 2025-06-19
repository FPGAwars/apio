"""Test for the "apio api" command."""

# NOTE: 'apio api scan-devices' require apio packages (for libusb1 lib)
# and thus, is tested in the integration tests.

import json
from test.conftest import ApioRunner
from apio.commands.apio import cli as apio

# TODO: Add more tests


def test_apio_api_get_boards(apio_runner: ApioRunner):
    """Test "apio api get-boards" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-boards -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-boards", "-t", "xyz"])
        sb.assert_ok(result)
        assert "xyz" in result.output
        assert "alhambra-ii" in result.output

        # -- Execute "apio api get-boards -t xyz -s boards -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-boards", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert data["boards"]["alhambra-ii"] == {
            "description": "Alhambra II",
            "fpga": {
                "id": "ice40hx4k-tq144-8k",
                "part-num": "ICE40HX4K-TQ144",
                "arch": "ice40",
                "size": "8k",
            },
            "programmer": {"id": "openfpgaloader"},
        }


def test_apio_api_get_commands(apio_runner: ApioRunner):
    """Test "apio api get-commands" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-commands -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-commands", "-t", "xyz"])
        sb.assert_ok(result)
        assert "xyz" in result.output
        assert '"apio"' in result.output
        assert '"api"' in result.output
        assert '"get-boards"' in result.output

        # -- Execute "apio api get-boards -t xyz -s boards -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-commands", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert (
            data["apio"]["groups"]["Utility commands"]["api"]["groups"][
                "Subcommands"
            ]["get-boards"]
            == {}
        )
