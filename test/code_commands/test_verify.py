import apio


def test_apio_verify(clirunner):
    result = clirunner.invoke(apio.verify)
    assert result.exit_code == 1
