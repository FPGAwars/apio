from apio.commands.system import cli as cmd_system


def test_apio_system_lsftdi(clirunner):
    result = clirunner.invoke(cmd_system, ['--lsftdi'])
    assert result.exit_code == 0


def test_apio_system_lsusb(clirunner):
    result = clirunner.invoke(cmd_system, ['--lsusb'])
    assert result.exit_code == 0


def test_apio_system_info(clirunner):
    result = clirunner.invoke(cmd_system, ['--info'])
    assert result.exit_code == 0
