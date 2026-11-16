# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""
Tests of managers/package_manager.py
"""

import io
import json
import tarfile
from unittest.mock import Mock
import click
import pytest
from tests.conftest import ApioRunner
from apio.managers.package_manager import unpack_tgz
from apio.utils import progress_events


def test_unpack_tgz(apio_runner: ApioRunner, monkeypatch: pytest.MonkeyPatch):
    """Tests unpack_tgz()."""

    with apio_runner.in_sandbox() as sb:

        # -- Create the source files, one of them in a sub dir.
        src_dir = sb.proj_dir / "src"
        (src_dir / "bin").mkdir(parents=True)
        (src_dir / "readme.txt").write_text("readme", encoding="utf-8")
        (src_dir / "bin" / "tool").write_text("tool", encoding="utf-8")

        # -- Archive them.
        archive = sb.proj_dir / "package.tgz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(src_dir / "readme.txt", arcname="readme.txt")
            tar.add(src_dir / "bin" / "tool", arcname="bin/tool")

        # -- Case 1: Unpack to a new dir. Should extract all the files.
        dest_dir = sb.proj_dir / "dest1"
        events_path = sb.proj_dir / "events.jsonl"
        monkeypatch.setenv("APIO_EVENTS_FILE", str(events_path))
        monkeypatch.setattr(
            progress_events, "monotonic", Mock(side_effect=[0, 1, 2])
        )
        with click.Context(click.Command("test")):
            unpack_tgz(archive, dest_dir)
        events = [
            json.loads(line) for line in events_path.read_text().splitlines()
        ]
        assert [event["done"] for event in events] == [0, 1, 2]
        assert all(event["total"] == 2 for event in events)
        assert events[-1]["task"] == "unpack"
        assert events[-1]["item"] == "dest1"
        readme_text = (dest_dir / "readme.txt").read_text(encoding="utf-8")
        assert readme_text == "readme"
        tool_text = (dest_dir / "bin" / "tool").read_text(encoding="utf-8")
        assert tool_text == "tool"

        # -- Case 2: Unpack to an existing dir. Should extract all the files
        # -- and keep the existing ones.
        dest_dir = sb.proj_dir / "dest2"
        dest_dir.mkdir()
        (dest_dir / "existing.txt").write_text("existing", encoding="utf-8")
        unpack_tgz(archive, dest_dir)
        assert (dest_dir / "readme.txt").is_file()
        assert (dest_dir / "bin" / "tool").is_file()
        assert (dest_dir / "existing.txt").is_file()

        # -- Case 3: An archive without the .tgz extension. Should fail.
        archive_tar = sb.proj_dir / "package.tar"
        archive_tar.write_bytes(archive.read_bytes())
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                unpack_tgz(archive_tar, sb.proj_dir / "dest3")
        assert e.value.code == 1
        assert "it's not a .tgz file" in log.out
        assert not (sb.proj_dir / "dest3").exists()


def test_unpack_tgz_unsafe_item(
    apio_runner: ApioRunner, monkeypatch: pytest.MonkeyPatch
):
    """Tests that unpack_tgz() rejects an item outside of the dest dir."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an archive with a '../' item.
        archive = sb.proj_dir / "package.tgz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.addfile(tarfile.TarInfo("../escape.txt"), io.BytesIO())

        # -- Unpack. Should fail and not write the file.
        events_path = sb.proj_dir / "events.jsonl"
        monkeypatch.setenv("APIO_EVENTS_FILE", str(events_path))
        with apio_runner.with_logger() as log:
            with (
                pytest.raises(SystemExit) as e,
                click.Context(click.Command("test")),
            ):
                unpack_tgz(archive, sb.proj_dir / "dest")
        assert e.value.code == 1
        assert "Unsafe item '../escape.txt'" in log.out
        assert not (sb.proj_dir / "escape.txt").exists()
        assert not events_path.exists()


def test_unpack_tgz_empty(
    apio_runner: ApioRunner, monkeypatch: pytest.MonkeyPatch
):
    """An empty archive reports successful completion without an initial event."""
    with apio_runner.in_sandbox() as sb:
        archive = sb.proj_dir / "empty.tgz"
        with tarfile.open(archive, "w:gz"):
            pass
        events_path = sb.proj_dir / "events.jsonl"
        monkeypatch.setenv("APIO_EVENTS_FILE", str(events_path))
        with click.Context(click.Command("test")):
            unpack_tgz(archive, sb.proj_dir / "empty")
        assert [
            json.loads(line) for line in events_path.read_text().splitlines()
        ] == [
            {
                "event": "progress",
                "task": "unpack",
                "item": "empty",
                "done": 0,
                "total": 0,
            }
        ]
