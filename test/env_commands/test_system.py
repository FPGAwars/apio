import apio
from click.testing import CliRunner


def test_apio_system_lsusb():
    runner = CliRunner()
    result = runner.invoke(apio.system, ['lsusb'])
    assert result.exit_code == 0


def test_apio_system_lsftdi():
    runner = CliRunner()
    result = runner.invoke(apio.system, ['lsftdi'])
    assert result.exit_code == 0


def test_apio_system_platform():
    runner = CliRunner()
    result = runner.invoke(apio.system, ['platform'])
    assert result.exit_code == 0
