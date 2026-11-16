# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""
Tests of managers/downloader.py
"""

import gc
import json
from pathlib import Path
from unittest.mock import Mock
import click
import requests
from pytest import MonkeyPatch, raises, mark
from apio.managers.downloader import FileDownloader
from apio.common import apio_console
from apio.common.proto.stubs.apio_scons_pb2 import FORCE_PIPE
from apio.utils import progress_events


@mark.parametrize("package_name", [None, "oss-cad-suite"])
def test_download_events(
    tmp_path: Path, monkeypatch: MonkeyPatch, package_name: str | None
):
    """Progress is readable before a piped download finishes."""
    events_path = tmp_path / "events.jsonl"
    apio_console.configure(terminal_mode=FORCE_PIPE)
    monkeypatch.setenv("APIO_EVENTS_FILE", str(events_path))
    monkeypatch.setattr(
        progress_events, "monotonic", Mock(side_effect=[0, 1, 2])
    )

    def chunks(**_kwargs):
        yield b"a" * 1024
        events = [
            json.loads(line) for line in events_path.read_text().splitlines()
        ]
        assert events[0]["done"] == 0
        assert events[-1]["done"] == 1024
        yield b"b"

    response = Mock(status_code=200, headers={"content-length": "1025"})
    response.iter_content.side_effect = chunks
    monkeypatch.setattr(requests, "get", Mock(return_value=response))
    with click.Context(click.Command("download")):
        downloader = FileDownloader(
            "https://example.invalid/test.tgz", tmp_path
        )
        downloader.download(package_name)

    events = [
        json.loads(line) for line in events_path.read_text().splitlines()
    ]
    assert events[-1] == {
        "event": "progress",
        "task": "download",
        "item": package_name or "test.tgz",
        "done": 1025,
        "total": 1025,
    }
    assert downloader.destination.read_bytes() == b"a" * 1024 + b"b"


def test_download_incomplete(tmp_path: Path, monkeypatch: MonkeyPatch):
    """A short response must not produce a completion event."""
    apio_console.configure(terminal_mode=FORCE_PIPE)
    path = tmp_path / "events.jsonl"
    monkeypatch.setenv("APIO_EVENTS_FILE", str(path))
    response = Mock(status_code=200, headers={"content-length": "1024"})
    response.iter_content.return_value = iter([b"short"])
    monkeypatch.setattr(requests, "get", Mock(return_value=response))
    with click.Context(click.Command("test")):
        downloader = FileDownloader(
            "https://example.invalid/test.tgz", tmp_path
        )
        with raises(OSError, match="Content-Length"):
            downloader.download("test")
    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert all(event["done"] < event["total"] for event in events)


@mark.parametrize("fail_write", [False, True])
def test_download_empty(
    tmp_path: Path, monkeypatch: MonkeyPatch, fail_write: bool
):
    """An empty download completes only after its destination is written."""
    apio_console.configure(terminal_mode=FORCE_PIPE)
    path = tmp_path / "events.jsonl"
    monkeypatch.setenv("APIO_EVENTS_FILE", str(path))
    response = Mock(status_code=200, headers={"content-length": "0"})
    response.iter_content.return_value = iter([])
    monkeypatch.setattr(requests, "get", Mock(return_value=response))
    with click.Context(click.Command("test")):
        downloader = FileDownloader(
            "https://example.invalid/test.tgz", tmp_path
        )
        if fail_write:
            downloader.destination.mkdir()
            with raises(OSError):
                downloader.download()
        else:
            downloader.download()
    events = [json.loads(line) for line in path.read_text().splitlines()]
    if fail_write:
        assert not events
    else:
        assert len(events) == 1
        assert events[0]["done"] == events[0]["total"] == 0


def test_failed_construction_safe_finalizer(monkeypatch: MonkeyPatch):
    """Tests that a FileDownloader whose construction failed, e.g. on a
    connection timeout, does not raise from its __del__ finalizer. It used
    to raise an AttributeError at garbage collection time, at an arbitrary
    point of the program (pytest reports it as an 'unraisable exception'
    error on an arbitrary test)."""

    # -- Make requests.get raise a connect timeout, as when the server is
    # -- unreachable. We mock it to avoid a dependency on real networking.
    def mock_get(*_args, **_kwargs):
        raise requests.exceptions.ConnectTimeout("test timeout")

    monkeypatch.setattr(requests, "get", mock_get)

    # -- Construct a downloader. The construction should fail before the
    # -- request field is populated.
    with raises(requests.exceptions.ConnectTimeout):
        FileDownloader("http://localhost/no-such-file.tgz")

    # -- Force the collection of the partially constructed object. With a
    # -- broken finalizer, pytest flags an 'unraisable exception' error here.
    gc.collect()
