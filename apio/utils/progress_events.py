"""Optional package progress events for host applications."""

import json
from time import monotonic
from typing import BinaryIO
import click
from apio.common.apio_console import fatal_error
from apio.utils import env_options


class ProgressEvents:
    """Emit progress at most four times per second, plus start and finish."""

    def __init__(self, task: str, item: str, total: int):
        self._task = task
        self._item = item
        self._total = total
        self._next_update = 0.0
        self._stream: BinaryIO | None = None
        path = env_options.get(env_options.APIO_EVENTS_FILE)
        ctx = click.get_current_context(silent=True)
        if path is not None and ctx is not None:
            # Keep pipes connected until the entire command exits.
            root = ctx.find_root()
            self._stream = root.meta.get("apio_events_stream")
            if self._stream is None:
                try:
                    self._stream = root.with_resource(
                        # Click owns the stream until the command exits.
                        # pylint: disable-next=consider-using-with
                        open(path, "ab", buffering=0)
                    )
                except OSError as exc:
                    fatal_error("Cannot open Apio events file.", cause=exc)
                root.meta["apio_events_stream"] = self._stream
        if total:
            self.update(0)

    def update(self, done: int) -> None:
        """Report completed bytes or archive entries, flushing immediately."""
        if self._stream is None:
            return
        now = monotonic()
        if done != self._total and now < self._next_update:
            return
        event = {
            "event": "progress",
            "task": self._task,
            "item": self._item,
            "done": done,
            "total": self._total,
        }
        line = (json.dumps(event) + "\n").encode("utf-8")
        try:
            # Unbuffered writes make each JSON line available to the host.
            if self._stream.write(line) != len(line):
                raise OSError("Incomplete event write")
        except OSError as exc:
            fatal_error("Cannot write Apio events file.", cause=exc)
        self._next_update = now + 0.25
