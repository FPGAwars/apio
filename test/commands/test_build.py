"""
  Test for the "apio build" command
"""

from test.conftest import ApioRunner

# -- apio build entry point
from apio.commands.build import cli as apio_build


# pylint: disable=too-many-statements
def test_errors_without_apio_ini_1(apio_runner: ApioRunner):
    """Test: Various errors 1/2. All tests are without apio.ini and without
    apio packages installed."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio build"
        result = sb.invoke_apio_cmd(apio_build)
        assert result.exit_code != 0, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output
        assert "Error: Missing FPGA" in result.output

        # apio build --board icestick
        result = sb.invoke_apio_cmd(apio_build, ["--board", "icestick"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --fpga iCE40-HX1K-VQ100
        result = sb.invoke_apio_cmd(apio_build, ["--fpga", "iCE40-HX1K-VQ100"])
        assert result.exit_code == 1, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --type lp --size 8k --pack cm225:4k
        result = sb.invoke_apio_cmd(
            apio_build, ["--type", "lp", "--size", "8k", "--pack", "cm225:4k"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: insufficient arguments" in result.output

        # apio build --board icezum --size 1k
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icezum", "--size", "1k"]
        )
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --board icezum --fpga iCE40-HX1K-TQ144 --type hx
        result = sb.invoke_apio_cmd(
            apio_build,
            [
                "--board",
                "icezum",
                "--fpga",
                "iCE40-HX1K-TQ144",
                "--type",
                "hx",
            ],
        )
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --board icezum --pack tq144
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icezum", "--pack", "tq144"]
        )
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --pack tq144 --size 1k
        result = sb.invoke_apio_cmd(
            apio_build,
            ["--fpga", "iCE40-HX1K-TQ144", "--pack", "tq144", "--size", "1k"],
        )
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --type hx
        result = sb.invoke_apio_cmd(
            apio_build, ["--fpga", "iCE40-HX1K-TQ144", "--type", "hx"]
        )
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output

        # apio build --board icezum --size 8k
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icezum", "--size", "8k"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'size' = (1k vs 8k)"
            in result.output
        )

        # apio build --board icezum --fpga iCE40-HX1K-TQ144 --type lp
        result = sb.invoke_apio_cmd(
            apio_build,
            [
                "--board",
                "icezum",
                "--fpga",
                "iCE40-HX1K-TQ144",
                "--type",
                "lp",
            ],
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'type' = (hx vs lp)"
            in result.output
        )

        # apio build --board icezum --fpga iCE40-HX1K-VQ100
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icezum", "--fpga", "iCE40-HX1K-VQ100"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'fpga' = "
            "(iCE40-HX1K-TQ144 vs iCE40-HX1K-VQ100)" in result.output
        )

        # apio build --fpga iCE40-HX1K-TQ144 --type lp --size 8k
        result = sb.invoke_apio_cmd(
            apio_build,
            ["--fpga", "iCE40-HX1K-TQ144", "--type", "lp", "--size", "8k"],
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'type' = (hx vs lp)"
            in result.output
        )

        # apio build --fpga iCE40-HX1K-TQ144 --pack vq100
        result = sb.invoke_apio_cmd(
            apio_build, ["--fpga", "iCE40-HX1K-TQ144", "--pack", "vq100"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'pack' = (tq144 vs vq100)"
            in result.output
        )

        # apio build --board icezum --pack vq100
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icezum", "--pack", "vq100"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'pack' = (tq144 vs vq100)"
            in result.output
        )

        # apio build --size 8k
        result = sb.invoke_apio_cmd(apio_build, ["--size", "8k"])
        assert result.exit_code != 0, result.output
        assert "Error: insufficient arguments" in result.output


def test_errors_without_apio_ini_2(apio_runner: ApioRunner):
    """Test: Various errors 2/2. All tests are without apio.ini and without
    apio packages installed."""
    with apio_runner.in_sandbox() as sb:

        # apio build --type lp
        result = sb.invoke_apio_cmd(apio_build, ["--type", "lp"])
        assert result.exit_code != 0, result.output
        assert "Error: insufficient arguments" in result.output

        # apio build --type lp --size 8k
        result = sb.invoke_apio_cmd(
            apio_build, ["--type", "lp", "--size", "8k"]
        )
        assert result.exit_code != 0, result.output
        assert "Error: insufficient arguments" in result.output

        # apio build --board icefake
        result = sb.invoke_apio_cmd(apio_build, ["--board", "icefake"])
        assert result.exit_code != 0, result.output
        assert "Error: unknown board: icefake" in result.output

        # apio build --board icefake --fpga iCE40-HX1K-TQ144
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icefake", "--fpga", "iCE40-HX1K-TQ144"]
        )
        assert result.exit_code != 0, result.output
        assert "Error: unknown board: icefake" in result.output

        # apio build --fpga iCE40-FAKE
        result = sb.invoke_apio_cmd(apio_build, ["--fpga", "iCE40-FAKE"])
        assert result.exit_code != 0, result.output
        assert "Error: unknown FPGA: iCE40-FAKE" in result.output

        # apio build --fpga iCE40-FAKE --size 8k
        result = sb.invoke_apio_cmd(
            apio_build, ["--fpga", "iCE40-FAKE", "--size", "8k"]
        )
        assert result.exit_code != 0, result.output
        assert "Error: unknown FPGA: iCE40-FAKE" in result.output

        # apio build --board icezum --fpga iCE40-FAKE
        result = sb.invoke_apio_cmd(
            apio_build, ["--board", "icezum", "--fpga", "iCE40-FAKE"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'fpga' = "
            "(iCE40-HX1K-TQ144 vs iCE40-FAKE)" in result.output
        )


def test_errors_with_apio_ini(apio_runner: ApioRunner):
    """Test: apio build with apio create"""

    with apio_runner.in_sandbox() as sb:

        # -- Write apio.ini
        sb.write_apio_ini({"board": "icezum", "top-module": "main"})

        # apio build
        result = sb.invoke_apio_cmd(apio_build)
        assert result.exit_code != 0, result.output

        # apio build --board icestick
        result = sb.invoke_apio_cmd(apio_build, ["--board", "icestick"])
        assert result.exit_code != 0, result.output
        assert (
            "Info: ignoring board specification from apio.ini."
            in result.output
        )

        # apio build --fpga iCE40-HX1K-VQ100
        result = sb.invoke_apio_cmd(apio_build, ["--fpga", "iCE40-HX1K-VQ100"])
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'fpga' = "
            "(iCE40-HX1K-TQ144 vs iCE40-HX1K-VQ100)" in result.output
        )

        # apio build --type lp --size 8k --pack cm225:4k
        result = sb.invoke_apio_cmd(
            apio_build, ["--type", "lp", "--size", "8k", "--pack", "cm225:4k"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'type' = (hx vs lp)"
            in result.output
        )

        # apio build --type lp --size 8k
        result = sb.invoke_apio_cmd(
            apio_build, ["--type", "lp", "--size", "8k"]
        )
        assert result.exit_code != 0, result.output
        assert (
            "Error: contradictory argument values: 'type' = (hx vs lp)"
            in result.output
        )
