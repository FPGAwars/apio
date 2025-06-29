"""A test program to test OS pipe blocking which affects the 'smoothness'
of programmers progress bar under Apio scons."""

# Usage:
#  python parent.py

import subprocess
import threading
import _io
from typing import Optional, List
from enum import Enum


class StreamId(Enum):
    STDOUT = 1
    STDERR = 2


thread_lock = threading.Lock()


def handle_incoming_line(stream_id: StreamId, bfr: bytearray, terminator: str):
    """Called on each new line."""
    with thread_lock:
        # -- Convert the line's bytes to a string. Replace invalid utf-8
        # -- chars with "�"
        line = bfr.decode("utf-8", errors="replace")

        # print(f"*** LINE [{stream_id}]: [{repr(line)}], [{repr(terminator)}]")
        print(line + terminator, end="", flush=True)


def pipe_reader_task_body(pipe: _io.FileIO, stream_id: StreamId):
    """Task body to read and process the bytes from a single
    stream."""

    assert isinstance(pipe, _io.FileIO), type(pipe)

    bfr = bytearray()

    while True:
        b: Optional[bytearray] = pipe.read(1)

        assert isinstance(b, bytes), type(b)
        assert len(b) <= 1

        # -- Handle end of file
        if not b:
            if bfr:
                handle_incoming_line(stream_id, bfr, "")
            return

        # -- Handle \r terminator
        if b == b"\r":
            handle_incoming_line(stream_id, bfr, "\r")
            bfr.clear()
            continue

        # -- Handle \n terminator
        if b == b"\n":
            handle_incoming_line(stream_id, bfr, "\n")
            bfr.clear()
            continue

        # -- Handle a regular character
        bfr.append(b[0])


def run_cmd(cmd: List[str]):
    # Start the sub process.
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
    )

    # Start threads to process stdout and stderr
    t1 = threading.Thread(
        target=pipe_reader_task_body, args=(process.stdout, StreamId.STDOUT)
    )
    t2 = threading.Thread(
        target=pipe_reader_task_body, args=(process.stderr, StreamId.STDERR)
    )
    t1.start()
    t2.start()

    # Wait for process and threads to finish
    process.wait()
    t1.join()
    t2.join()

    return process.returncode


# Adjust the iceprog command as needed. May need to set the shell envs based
# on the setting info from 'apio raw -v'.
# exit_code = run_cmd(["iceprog.exe", "-d", "d:2/7", "_build/default/hardware.bin"])

exit_code = run_cmd(["python", "child.py"])
print(f"{exit_code=}")
