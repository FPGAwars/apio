import apio


def test_apio_uninstall_list(clirunner):
    result = clirunner.invoke(apio.uninstall, ['--list'])
    assert result.exit_code == 0
