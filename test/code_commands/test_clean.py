import apio


def test_apio_clean(clirunner):
    result = clirunner.invoke(apio.clean)
    assert result.exit_code == 0
