import apio


def test_apio_install_list(clirunner):
    result = clirunner.invoke(apio.install, ['--list'])
    assert result.exit_code == 0
