from apio.commands.build import cli as cmd_build
from apio.commands.init import cli as cmd_init


def test_build(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_build)
        assert result.exit_code != 0
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_build_board(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()
        result = clirunner.invoke(cmd_build, ['--board', 'icezum'])
        assert result.exit_code != 0
        if result.exit_code == 1:
            assert 'install yosys' in result.output


def test_build_complete(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()

        # apio build --board icestick
        result = clirunner.invoke(cmd_build, ['--board', 'icestick'])
        assert result.exit_code != 0

        # apio build --fpga iCE40-HX1K-VQ100
        result = clirunner.invoke(cmd_build, ['--fpga', 'iCE40-HX1K-VQ100'])
        assert result.exit_code != 0

        # apio build --type lp --size 8k --pack cm225:4k
        result = clirunner.invoke(cmd_build, [
            '--type', 'lp', '--size', '8k', '--pack', 'cm225:4k'])
        assert result.exit_code != 0

        # apio build --board icezum --size 1k
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--size', '1k'])
        assert result.exit_code != 0
        assert 'Warning: redundant arguments: size' in result.output

        # apio build --board icezum --fpga iCE40-HX1K-TQ144 --type hx
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--fpga', 'iCE40-HX1K-TQ144', '--type', 'hx'])
        assert result.exit_code != 0
        assert 'Warning: redundant arguments: fpga, type' in result.output

        # apio build --board icezum --pack tq144
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--pack', 'tq144'])
        assert result.exit_code != 0
        assert 'Warning: redundant arguments: pack' in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --pack tq144 --size 1k
        result = clirunner.invoke(cmd_build, [
            '--fpga', 'iCE40-HX1K-TQ144', '--pack', 'tq144', '--size', '1k'])
        assert result.exit_code != 0
        assert 'Warning: redundant arguments: size, pack' in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --type hx
        result = clirunner.invoke(cmd_build, [
            '--fpga', 'iCE40-HX1K-TQ144', '--type', 'hx'])
        assert result.exit_code != 0
        assert 'Warning: redundant arguments: type' in result.output

        # apio build --board icezum --size 8k
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--size', '8k'])
        assert result.exit_code != 0
        assert 'Error: contradictory arguments: size' in result.output

        # apio build --board icezum --fpga iCE40-HX1K-TQ144 --type lp
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--fpga', 'iCE40-HX1K-TQ144', '--type', 'lp'])
        assert result.exit_code != 0
        assert 'Warning: redundant arguments: fpga' in result.output
        assert 'Error: contradictory arguments: type' in result.output

        # apio build --board icezum --fpga iCE40-HX1K-VQ100
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--fpga', 'iCE40-HX1K-VQ100'])
        assert result.exit_code != 0
        assert 'Error: contradictory arguments: fpga' in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --type lp --size 8k
        result = clirunner.invoke(cmd_build, [
            '--fpga', 'iCE40-HX1K-TQ144', '--type', 'lp', '--size', '8k'])
        assert result.exit_code != 0
        assert 'Error: contradictory arguments: size, type' in result.output

        # apio build --fpga iCE40-HX1K-TQ144 --pack vq100
        result = clirunner.invoke(cmd_build, [
            '--fpga', 'iCE40-HX1K-TQ144', '--pack', 'vq100'])
        assert result.exit_code != 0
        assert 'Error: contradictory arguments: pack' in result.output

        # apio build --board icezum --pack vq100
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--pack', 'vq100'])
        assert result.exit_code != 0
        assert 'Error: contradictory arguments: pack' in result.output

        # apio build --size 8k
        result = clirunner.invoke(cmd_build, ['--size', '8k'])
        assert result.exit_code != 0
        assert 'Error: insufficient arguments: missing type, pack' \
            in result.output

        # apio build --type lp
        result = clirunner.invoke(cmd_build, ['--type', 'lp'])
        assert result.exit_code != 0
        assert 'Error: insufficient arguments: missing size, pack' \
            in result.output

        # apio build --type lp --size 8k
        result = clirunner.invoke(cmd_build, ['--type', 'lp', '--size', '8k'])
        assert result.exit_code != 0
        assert 'Error: insufficient arguments: missing pack' in result.output

        # apio build --board icefake
        result = clirunner.invoke(cmd_build, ['--board', 'icefake'])
        assert result.exit_code != 0
        assert 'Error: unknown board: icefake' in result.output

        # apio build --board icefake --fpga iCE40-HX1K-TQ144
        result = clirunner.invoke(cmd_build, [
            '--board', 'icefake', '--fpga', 'iCE40-HX1K-TQ144'])
        assert result.exit_code != 0
        assert 'Error: unknown board: icefake' in result.output

        # apio build --fpga iCE40-FAKE
        result = clirunner.invoke(cmd_build, ['--fpga', 'iCE40-FAKE'])
        assert result.exit_code != 0
        assert 'Error: unknown FPGA: iCE40-FAKE' in result.output

        # apio build --fpga iCE40-FAKE --size 8k
        result = clirunner.invoke(cmd_build, [
            '--fpga', 'iCE40-FAKE', '--size', '8k'])
        assert result.exit_code != 0
        assert 'Error: unknown FPGA: iCE40-FAKE' in result.output

        # apio build --board icezum --fpga iCE40-FAKE
        result = clirunner.invoke(cmd_build, [
            '--board', 'icezum', '--fpga', 'iCE40-FAKE'])
        assert result.exit_code != 0
        assert 'Error: unknown FPGA: iCE40-FAKE' in result.output


def test_build_init(clirunner, configenv):
    with clirunner.isolated_filesystem():
        configenv()

        # apio init --board icezum
        result = clirunner.invoke(cmd_init, ['--board', 'icezum'])
        assert result.exit_code == 0
        assert 'Creating apio.ini file ...' in result.output
        assert 'has been successfully created!' in result.output

        # apio build
        result = clirunner.invoke(cmd_build)
        assert result.exit_code != 0

        # apio build --board icezum
        result = clirunner.invoke(cmd_build, ['--board', 'icestick'])
        assert result.exit_code != 0
        assert 'Info: ignore apio.ini board' in result.output

        # apio build --fpga iCE40-HX1K-VQ100
        result = clirunner.invoke(cmd_build, ['--fpga', 'iCE40-HX1K-VQ100'])
        assert result.exit_code != 0
        assert 'Info: ignore apio.ini board' in result.output

        # apio build --type lp --size 8k --pack cm225:4k
        result = clirunner.invoke(cmd_build, [
            '--type', 'lp', '--size', '8k', '--pack', 'cm225:4k'])
        assert result.exit_code != 0
        assert 'Info: ignore apio.ini board' in result.output

        # apio build --type lp --size 8k
        result = clirunner.invoke(cmd_build, ['--type', 'lp', '--size', '8k'])
        assert result.exit_code != 0
        assert 'Info: ignore apio.ini board' in result.output
        assert 'Error: insufficient arguments: missing pack' in result.output
