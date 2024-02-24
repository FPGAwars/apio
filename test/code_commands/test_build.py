"""
  Test for the "apio build" command
"""

# -- apio build entry point
from apio.commands.build import cli as cmd_build

# -- This is for testing "apio init"
from apio.commands.init import cli as cmd_init


def test_build(clirunner, configenv):
    """Test: apio build
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio build"
        result = clirunner.invoke(cmd_build)

        # -- It is an error. Exit code should not be 0
        assert result.exit_code != 0

        # -- Messages thtat should appear
        assert "Info: No apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output
        assert "Error: Missing FPGA" in result.output


def test_build_board(clirunner, configenv):
    """Test: apio build --board icezum
    No oss-cad-suite package is installed
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio build --board icezum"
        result = clirunner.invoke(cmd_build, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code != 0
        assert "install oss-cad-suite" in result.output


def test_build_complete1(clirunner, configenv):
    """Test: apio build with different arguments. Part 1/2"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # apio build --board icestick
        result = clirunner.invoke(cmd_build, ["--board", "icestick"])
        assert result.exit_code == 1
        assert "install oss-cad-suite" in result.output

        # apio build --fpga iCE40-HX1K-VQ100
        result = clirunner.invoke(cmd_build, ["--fpga", "iCE40-HX1K-VQ100"])
        assert result.exit_code == 1
        assert "install oss-cad-suite" in result.output

        # apio build --type lp --size 8k --pack cm225:4k
        result = clirunner.invoke(
            cmd_build, ["--type", "lp", "--size", "8k", "--pack", "cm225:4k"]
        )
        assert result.exit_code == 1
        assert "Error: insufficient arguments" in result.output

        # apio build --board icezum --size 1k
        result = clirunner.invoke(
            cmd_build, ["--board", "icezum", "--size", "1k"]
        )
        assert result.exit_code != 0
        assert "install oss-cad-suite" in result.output

        # apio build --board icezum --fpga iCE40-HX1K-TQ144 --type hx
        result = clirunner.invoke(
            cmd_build,
            [
                "--board",
                "icezum",
                "--fpga",
                "iCE40-HX1K-TQ144",
                "--type",
                "hx",
            ],
        )
        assert result.exit_code != 0
        assert "install oss-cad-suite" in result.output

        # apio build --board icezum --pack tq144
        result = clirunner.invoke(
            cmd_build, ["--board", "icezum", "--pack", "tq144"]
        )
        assert result.exit_code != 0
        assert "install oss-cad-suite" in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --pack tq144 --size 1k
        result = clirunner.invoke(
            cmd_build,
            ["--fpga", "iCE40-HX1K-TQ144", "--pack", "tq144", "--size", "1k"],
        )
        assert result.exit_code != 0
        assert "install oss-cad-suite" in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --type hx
        result = clirunner.invoke(
            cmd_build, ["--fpga", "iCE40-HX1K-TQ144", "--type", "hx"]
        )
        assert result.exit_code != 0
        assert "install oss-cad-suite" in result.output

        # apio build --board icezum --size 8k
        result = clirunner.invoke(
            cmd_build, ["--board", "icezum", "--size", "8k"]
        )
        assert result.exit_code != 0
        assert "Error: contradictory arguments: ('1k', '8k')" in result.output

        # apio build --board icezum --fpga iCE40-HX1K-TQ144 --type lp
        result = clirunner.invoke(
            cmd_build,
            [
                "--board",
                "icezum",
                "--fpga",
                "iCE40-HX1K-TQ144",
                "--type",
                "lp",
            ],
        )
        assert result.exit_code != 0
        assert "Error: contradictory arguments: ('hx', 'lp')" in result.output

        # apio build --board icezum --fpga iCE40-HX1K-VQ100
        result = clirunner.invoke(
            cmd_build, ["--board", "icezum", "--fpga", "iCE40-HX1K-VQ100"]
        )
        assert result.exit_code != 0
        assert (
            "Error: contradictory arguments: ('iCE40-HX1K-TQ144', "
            "'iCE40-HX1K-VQ100')" in result.output
        )

        # apio build --fpga iCE40-HX1K-TQ144 --type lp --size 8k
        result = clirunner.invoke(
            cmd_build,
            ["--fpga", "iCE40-HX1K-TQ144", "--type", "lp", "--size", "8k"],
        )
        assert result.exit_code != 0
        assert "Error: contradictory arguments: ('hx', 'lp')" in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --pack vq100
        result = clirunner.invoke(
            cmd_build, ["--fpga", "iCE40-HX1K-TQ144", "--pack", "vq100"]
        )
        assert result.exit_code != 0
        assert (
            "Error: contradictory arguments: ('tq144', 'vq100')"
            in result.output
        )

        # apio build --board icezum --pack vq100
        result = clirunner.invoke(
            cmd_build, ["--board", "icezum", "--pack", "vq100"]
        )
        assert result.exit_code != 0
        assert (
            "Error: contradictory arguments: ('tq144', 'vq100')"
            in result.output
        )

        # apio build --size 8k
        result = clirunner.invoke(cmd_build, ["--size", "8k"])
        assert result.exit_code != 0
        assert "Error: insufficient arguments" in result.output


def test_build_complete2(clirunner, configenv):
    """Test: apio build with different arguments. Part 2/2"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # apio build --type lp
        result = clirunner.invoke(cmd_build, ["--type", "lp"])
        assert result.exit_code != 0
        assert "Error: insufficient arguments" in result.output

        # apio build --type lp --size 8k
        result = clirunner.invoke(cmd_build, ["--type", "lp", "--size", "8k"])
        assert result.exit_code != 0
        assert "Error: insufficient arguments" in result.output

        # apio build --board icefake
        result = clirunner.invoke(cmd_build, ["--board", "icefake"])
        assert result.exit_code != 0
        assert "Error: unknown board: icefake" in result.output

        # apio build --board icefake --fpga iCE40-HX1K-TQ144
        result = clirunner.invoke(
            cmd_build, ["--board", "icefake", "--fpga", "iCE40-HX1K-TQ144"]
        )
        assert result.exit_code != 0
        assert "Error: unknown board: icefake" in result.output

        # apio build --fpga iCE40-FAKE
        result = clirunner.invoke(cmd_build, ["--fpga", "iCE40-FAKE"])
        assert result.exit_code != 0
        assert "Error: unknown FPGA: iCE40-FAKE" in result.output

        # apio build --fpga iCE40-FAKE --size 8k
        result = clirunner.invoke(
            cmd_build, ["--fpga", "iCE40-FAKE", "--size", "8k"]
        )
        assert result.exit_code != 0
        assert "Error: unknown FPGA: iCE40-FAKE" in result.output

        # apio build --board icezum --fpga iCE40-FAKE
        result = clirunner.invoke(
            cmd_build, ["--board", "icezum", "--fpga", "iCE40-FAKE"]
        )
        assert result.exit_code != 0
        assert (
            "Error: contradictory arguments: ('iCE40-HX1K-TQ144', 'iCE40-FAKE')"
            in result.output
        )


def test_build_init(clirunner, configenv):
    """Test: apio build with apio init"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # apio init --board icezum
        result = clirunner.invoke(cmd_init, ["--board", "icezum"])
        assert result.exit_code == 0
        assert "Creating apio.ini file ..." in result.output
        assert "has been successfully created!" in result.output

        # apio build
        result = clirunner.invoke(cmd_build)
        assert result.exit_code != 0

        # apio build --board icezum
        result = clirunner.invoke(cmd_build, ["--board", "icestick"])
        assert result.exit_code != 0
        assert "Info: ignore apio.ini board" in result.output

        # apio build --fpga iCE40-HX1K-VQ100
        result = clirunner.invoke(cmd_build, ["--fpga", "iCE40-HX1K-VQ100"])
        assert result.exit_code != 0
        assert (
            "Error: contradictory arguments: ('iCE40-HX1K-TQ144', 'iCE40-HX1K-VQ100')"
            in result.output
        )

        # apio build --type lp --size 8k --pack cm225:4k
        result = clirunner.invoke(
            cmd_build, ["--type", "lp", "--size", "8k", "--pack", "cm225:4k"]
        )
        assert result.exit_code != 0
        assert "Error: contradictory arguments: ('hx', 'lp')" in result.output

        # apio build --type lp --size 8k
        result = clirunner.invoke(cmd_build, ["--type", "lp", "--size", "8k"])
        assert result.exit_code != 0
        assert "Error: contradictory arguments: ('hx', 'lp')" in result.output
