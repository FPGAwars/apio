"""Tests for the host application's progress stream."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock
import click
import pytest
from apio.common import apio_console
from apio.common.proto.stubs.apio_scons_pb2 import FORCE_PIPE
from apio.utils import progress_events
from apio.utils.progress_events import ProgressEvents


def test_progress_disabled(monkeypatch: pytest.MonkeyPatch):
    """Without the opt-in variable, no file is opened."""
    monkeypatch.delenv("APIO_EVENTS_FILE", raising=False)
    open_file = Mock(side_effect=AssertionError("Unexpected file access"))
    monkeypatch.setattr("builtins.open", open_file)
    with click.Context(click.Command("test")):
        ProgressEvents("download", "package", 10).update(10)
    open_file.assert_not_called()


def test_progress_stream(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Append, flush, throttle, reuse, and close the command's stream."""
    path = tmp_path / "events.jsonl"
    path.write_text('{"existing": true}\n', encoding="utf-8")
    monkeypatch.setenv("APIO_EVENTS_FILE", str(path))
    monkeypatch.setattr(
        progress_events,
        "monotonic",
        Mock(side_effect=[10, 10.1, 10.3, 10.4, 11]),
    )
    with click.Context(click.Command("test")) as ctx:
        progress = ProgressEvents("download", "pkg\nλ", 3)
        stream = ctx.meta["apio_events_stream"]
        progress.update(1)
        progress.update(2)
        progress.update(3)
        ProgressEvents("unpack", "empty", 0).update(0)
        assert ctx.meta["apio_events_stream"] is stream
        events = [json.loads(line) for line in path.read_text().splitlines()]
        assert events[0] == {"existing": True}
        assert [event["done"] for event in events[1:]] == [0, 2, 3, 0]
        assert events[1]["item"] == "pkg\nλ"
        assert events[-1]["task"] == "unpack"
        assert not stream.closed
    assert stream.closed


def test_progress_new_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A later invocation must not reuse a closed stream or old path."""
    for name in ("first", "second"):
        path = tmp_path / name
        monkeypatch.setenv("APIO_EVENTS_FILE", str(path))
        with click.Context(click.Command("test")):
            ProgressEvents("unpack", name, 0).update(0)
        assert json.loads(path.read_text())["item"] == name


def test_progress_open_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """An invalid destination fails clearly rather than losing events."""
    apio_console.configure(terminal_mode=FORCE_PIPE)
    monkeypatch.setenv("APIO_EVENTS_FILE", str(tmp_path))
    with click.Context(click.Command("test")):
        with pytest.raises(SystemExit) as exc:
            ProgressEvents("download", "package", 10)
    assert exc.value.code == 1


@pytest.mark.parametrize("short_write", [False, True])
def test_progress_broken_pipe(
    monkeypatch: pytest.MonkeyPatch, short_write: bool
):
    """A closed reader causes a clean failure and releases the handle."""
    apio_console.configure(terminal_mode=FORCE_PIPE)
    monkeypatch.setenv("APIO_EVENTS_FILE", "unused")
    stream = MagicMock()
    stream.__enter__.return_value = stream
    if short_write:
        stream.write.return_value = 0
    else:
        stream.write.side_effect = BrokenPipeError("reader closed")
    monkeypatch.setattr("builtins.open", Mock(return_value=stream))
    with pytest.raises(SystemExit) as exc:
        with click.Context(click.Command("test")):
            ProgressEvents("download", "package", 10)
    assert exc.value.code == 1
    stream.__exit__.assert_called_once()


@pytest.mark.skipif(os.name == "nt", reason="POSIX named pipe")
def test_progress_fifo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A FIFO reader gets whole events and EOF only at command exit."""
    if sys.platform == "win32":
        pytest.skip("POSIX named pipe")
    path = tmp_path / "events.fifo"
    os.mkfifo(path)  # pylint: disable=no-member
    monkeypatch.setenv("APIO_EVENTS_FILE", str(path))
    reader = os.open(
        path,
        os.O_RDONLY | os.O_NONBLOCK,  # pylint: disable=no-member
    )
    try:
        with click.Context(click.Command("test")):
            ProgressEvents("download", "test", 1).update(1)
            events = os.read(reader, 4096).splitlines()
            assert [json.loads(line)["done"] for line in events] == [0, 1]
            with pytest.raises(BlockingIOError):
                os.read(reader, 4096)
            ProgressEvents("unpack", "test", 1).update(1)
            events = os.read(reader, 4096).splitlines()
            assert [json.loads(line)["task"] for line in events] == [
                "unpack"
            ] * 2
        assert os.read(reader, 4096) == b""
    finally:
        os.close(reader)
