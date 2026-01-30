"""Test for the "apio api" command."""

# NOTE: 'apio api scan-devices' require apio packages (for libusb1 lib)
# and thus, is tested in the integration tests.

import json
import os
from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio

# TODO: Add more tests


def test_apio_api_get_boards(apio_runner: ApioRunner):
    """Test "apio api get-boards" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-boards -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-boards", "-t", "xyz"])
        sb.assert_result_ok(result)
        assert "xyz" in result.output
        assert "alhambra-ii" in result.output

        # -- Execute "apio api get-boards -t xyz -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-boards", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

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


def test_apio_api_get_fpgas(apio_runner: ApioRunner):
    """Test "apio api get-fpgas" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-fpgas -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-fpgas", "-t", "xyz"])
        sb.assert_result_ok(result)
        assert "xyz" in result.output
        assert "ice40hx4k-tq144-8k" in result.output

        # -- Execute "apio api get-fpgas -t xyz -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-fpgas", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert data["fpgas"]["ice40hx4k-tq144-8k"] == {
            "part-num": "ICE40HX4K-TQ144",
            "arch": "ice40",
            "size": "8k",
        }


def test_apio_api_get_programmers(apio_runner: ApioRunner):
    """Test "apio api get-programmers" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-programmers -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-programmers", "-t", "xyz"]
        )
        sb.assert_result_ok(result)
        assert "xyz" in result.output
        assert "openfpgaloader" in result.output

        # -- Execute "apio api get-programmers -t xyz -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-programmers", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert data["programmers"]["openfpgaloader"] == {
            "command": "openFPGALoader",
            "args": "",
        }


def test_apio_api_get_commands(apio_runner: ApioRunner):
    """Test "apio api get-commands" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-commands -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-commands", "-t", "xyz"])
        sb.assert_result_ok(result)
        assert "xyz" in result.output
        assert '"apio"' in result.output
        assert '"api"' in result.output
        assert '"get-boards"' in result.output

        # -- Execute "apio api get-boards -t xyz -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-commands", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert (
            data["commands"]["apio"]["commands"]["api"]["commands"][
                "get-boards"
            ]
            == {}
        )


def test_apio_api_get_system(apio_runner: ApioRunner):
    """Test "apio api get-system" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-system -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-system", "-t", "xyz"])
        sb.assert_result_ok(result)
        assert "xyz" in result.output
        assert '"apio-cli-version"' in result.output
        assert '"python-version"' in result.output

        # -- Execute "apio api get-system -t xyz -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-system", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert data["system"]["remote-config-url"].endswith(".jsonc")


def test_apio_api_get_project(apio_runner: ApioRunner):
    """Test "apio api get-project" """

    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio project
        sb.write_default_apio_ini()

        sb.write_file("synth0.v", "")
        sb.write_file("tb_0.sv", "")

        os.makedirs("src1")
        sb.write_file("src1/synth1.sv", "")
        sb.write_file("src1/synth2.sv", "")
        sb.write_file("src1/tb1_tb.sv", "")

        # -- Execute "apio api get-project -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-project", "-t", "xyz"])
        sb.assert_result_ok(result)
        assert '"default"' in result.output
        assert '"envs"' in result.output

        # -- Execute "apio api get-project -t xyz  -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-project", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)

        assert data == {
            "timestamp": "xyz",
            "project": {
                "active-env": {
                    "name": "default",
                    "options": {
                        "board": "alhambra-ii",
                        "top-module": "main",
                    },
                },
                "envs": [
                    "default",
                ],
                "synth-files": [
                    "synth0.v",
                    "tb_0.sv",
                    f"src1{os.sep}synth1.sv",
                    f"src1{os.sep}synth2.sv",
                ],
                "test-benches": [
                    f"src1{os.sep}tb1_tb.sv",
                ],
                "board": {
                    "id": "alhambra-ii",
                    "description": "Alhambra II",
                    "fpga-id": "ice40hx4k-tq144-8k",
                    "programmer": {
                        "extra-args": "--verify -b ice40_generic"
                        + " --vid ${VID} --pid ${PID} "
                        "--busdev-num ${BUS}:${DEV}",
                        "id": "openfpgaloader",
                    },
                    "usb": {
                        "pid": "6010",
                        "product-regex": "^Alhambra II.*",
                        "vid": "0403",
                    },
                },
                "fpga": {
                    "id": "ice40hx4k-tq144-8k",
                    "arch": "ice40",
                    "pack": "tq144:4k",
                    "part-num": "ICE40HX4K-TQ144",
                    "size": "8k",
                    "type": "hx8k",
                },
                "programmer": {
                    "id": "openfpgaloader",
                    "args": "",
                    "command": "openFPGALoader",
                },
            },
        }


def test_apio_api_get_examples(apio_runner: ApioRunner):
    """Test "apio api get-examples" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api get-examples -t xyz"  (stdout)
        result = sb.invoke_apio_cmd(apio, ["api", "get-examples", "-t", "xyz"])
        sb.assert_result_ok(result)
        assert "xyz" in result.output
        assert '"alhambra-ii"' in result.output
        assert '"blinky"' in result.output

        # -- Execute "apio api get-examples -t xyz -s boards -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"
        result = sb.invoke_apio_cmd(
            apio, ["api", "get-examples", "-t", "xyz", "-o", str(path)]
        )
        sb.assert_result_ok(result)

        # -- Read and verify the file.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert (
            data["examples"]["alhambra-ii"]["blinky"]["description"]
            == "Blinking led"
        )


def test_apio_api_scan_devices(apio_runner: ApioRunner):
    """Test "apio api scan-devices" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api scan-devices -t xyz". We run it in a
        # -- subprocess such that it releases the libusb1 file it uses.
        # -- This also means that it's not included in the pytest test
        # -- coverage report.
        result = sb.invoke_apio_cmd(
            apio, ["api", "scan-devices", "-t", "xyz"], in_subprocess=True
        )
        sb.assert_result_ok(result)

        assert "xyz" in result.output
        assert "usb-devices" in result.output
        assert "serial-devices" in result.output

        # -- Execute "apio api get-boards -t xyz -s boards -o <dir>"  (file)
        path = sb.proj_dir / "apio.json"

        result = sb.invoke_apio_cmd(
            apio,
            ["api", "scan-devices", "-t", "xyz", "-o", str(path)],
            in_subprocess=True,
        )
        sb.assert_result_ok(result)

        # -- Read and verify the output file. Since we don't know what
        # -- devices the platform has, we just check for the section keys.
        text = sb.read_file(path)
        data = json.loads(text)
        assert data["timestamp"] == "xyz"
        assert "usb-devices" in data
        assert "serial-devices" in data


def test_apio_api_echo(apio_runner: ApioRunner):
    """Test "apio api echo" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio api scan-devices -t xyz". We run it in a
        # -- subprocess such that it releases the libusb1 file it uses.
        # -- This also means that it's not included in the pytest test
        # -- coverage report.
        result = sb.invoke_apio_cmd(
            apio,
            ["api", "echo", "-t", "Hello world", "-s", "OK"],
            in_subprocess=True,
        )
        sb.assert_result_ok(result)

        assert "Hello world" in result.output
