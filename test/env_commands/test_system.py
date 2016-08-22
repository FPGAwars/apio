import apio


def test_apio_system_lsusb(clirunner):
    result = clirunner.invoke(apio.system, ['lsusb'])
    assert result.exit_code == 0


def test_apio_system_lsftdi(clirunner):
    result = clirunner.invoke(apio.system, ['lsftdi'])
    assert result.exit_code == 0


def test_apio_system_platform(clirunner):
    result = clirunner.invoke(apio.system, ['platform'])
    assert result.exit_code == 0
