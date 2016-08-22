import apio
from click.testing import CliRunner


def test_apio_time_board():
    runner = CliRunner()
    result = runner.invoke(apio.time, ['--board', 'icezum'])
    assert result.exit_code == 1
