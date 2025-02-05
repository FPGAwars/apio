"""
  Test for the "apio api" command
"""

import json
from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_apio_info(apio_runner: ApioRunner):
    """Test "apio api info" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api info -t xyz -s boards"  (stdout)
        result = sb.invoke_apio_cmd(
            apio, "api", "info", "-t", "xyz", "-s", "boards"
        )
        sb.assert_ok(result)
        assert "xyz" in result.output
        assert "alhambra-ii" in result.output

        # -- Execute "apio api info -t xyz -s boards -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, "api", "info", "-t", "xyz", "-s", "boards", "-o", str(path)
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
            },
            "programmer": {"id": "iceprog"},
        }
