"""
Tests of cmd_util.py
"""

import sys
import pytest
import click
from apio.cmd_util import (
    ApioCommand,
    ApioOption,
    check_at_most_one_param,
)

# pylint: disable=fixme
# TODO: Add more tests.


# -- A fake command for testing.
@click.command("fake_cmd", cls=ApioCommand)
@click.option("_opt1", "--opt1", is_flag=True, cls=ApioOption)
@click.option("_opt2", "--opt2", is_flag=True, cls=ApioOption)
@click.option("_opt3", "--opt3", is_flag=True, cls=ApioOption)
@click.option("_opt4", "--opt4", is_flag=True, cls=ApioOption)
def fake_cmd(_opt1, _opt2, _opt3, _opt4):
    """Fake click command for testing."""
    sys.exit(0)


def test_check_at_most_one_param(capsys):
    """Tests the check_at_most_one_param() function."""

    # -- No option is specified. Should be ok.
    cmd_ctx = click.Context(fake_cmd)
    fake_cmd.parse_args(cmd_ctx, [])
    check_at_most_one_param(cmd_ctx, ["_opt1", "_opt2", "_opt3"])

    # -- One option is specified. Should be ok.
    cmd_ctx = click.Context(fake_cmd)
    fake_cmd.parse_args(cmd_ctx, ["--opt1"])
    check_at_most_one_param(cmd_ctx, ["_opt1", "_opt2", "_opt3"])

    # -- Another option is specified. Should be ok.
    cmd_ctx = click.Context(fake_cmd)
    fake_cmd.parse_args(cmd_ctx, ["--opt2"])
    check_at_most_one_param(cmd_ctx, ["_opt1", "_opt2", "_opt3"])

    # -- Two options but one is non related to the check. Should be ok.
    cmd_ctx = click.Context(fake_cmd)
    fake_cmd.parse_args(cmd_ctx, ["--opt1", "--opt4"])
    check_at_most_one_param(cmd_ctx, ["_opt1", "_opt2", "_opt3"])

    # -- Two options are specifies. Should fail.
    cmd_ctx = click.Context(fake_cmd)
    fake_cmd.parse_args(cmd_ctx, ["--opt1", "--opt2"])
    capsys.readouterr()  # Reset capture.
    with pytest.raises(SystemExit) as e:
        check_at_most_one_param(cmd_ctx, ["_opt1", "_opt2", "_opt3"])
    captured = capsys.readouterr()
    assert e.value.code == 1
    assert "--opt1 and --opt2 cannot be combined together" in captured.out
