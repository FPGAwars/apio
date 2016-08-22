import apio
from click.testing import CliRunner


def test_apio_clean():
    runner = CliRunner()
    result = runner.invoke(apio.clean)
    assert result.exit_code == 0
