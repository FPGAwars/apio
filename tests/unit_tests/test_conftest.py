"""
Tests of the functionality of the pytest helper conftest.py
"""

import sys
from dataclasses import dataclass
from tests.conftest import ApioRunner
from apio.common.apio_console import cout, console, cstyle
from apio.apio_context import (
    ApioContext,
    ProjectPolicy,
    RemoteConfigPolicy,
    PackagesPolicy,
)


@dataclass(frozen=True)
class State:
    """Capture the I/O state for verification."""

    stdout_id: int
    stderr_id: int
    console_id: int
    console_file_id: int

    @classmethod
    def snapshot(cls) -> "State":
        """Snapshot the current state"""
        c = console()
        return State(
            stdout_id=id(sys.stdout),
            stderr_id=id(sys.stderr),
            console_id=id(c),
            console_file_id=id(c.file),
        )


def test_logger_minimal(apio_runner: ApioRunner):
    """Tests ApioRunner logger functionality with minimal configuration
    with no sandbox, no apio context, and no apio_console.py output."""

    # -- Test
    print("print-test-before")

    with apio_runner.with_logger() as log:
        print("print-test-inside")

    print("print-test-after")

    # -- Verify
    assert "print-test-before" not in log.out
    assert "print-test-inside" in log.out
    assert "print-test-after" not in log.out


def test_logger_with_console(apio_runner: ApioRunner):
    """Tests ApioRunner logger functionality with sandbox only and
    no apio context, and no apio_console.py output."""

    with apio_runner.in_sandbox():

        state1 = State.snapshot()

        # -- Test
        print("print-test-before")
        cout("cout-test-before")

        state2 = State.snapshot()

        with apio_runner.with_logger() as log:
            state3 = State.snapshot()
            print("print-test-inside")
            cout("cout-test-inside")

        state4 = State.snapshot()

        print("\n*** LOG:")
        print(log.out)
        print()

        print("print-test-after")
        cout("cout-test-after")

        # -- Dump state snapshots
        print(f"{state1=}")
        print(f"{state2=}")
        print(f"{state3=}")
        print(f"{state4=}")

        # -- Verify log
        assert "print-test-before" not in log.out
        assert "cout-test-before" not in log.out

        assert "print-test-inside" in log.out
        assert "cout-test-inside" in log.out

        assert "print-test-after" not in log.out
        assert "cout-test-after" not in log.out


def test_logger_with_cstyle(apio_runner: ApioRunner):
    """Tests ApioRunner logger functionality with sandbox and ,
    apio_console.py cstyle and cout but no ApioContext."""

    with apio_runner.in_sandbox():

        state1 = State.snapshot()

        # -- Invoke cstyle, in the past in interfered with the logger.
        text = "red-text"
        styled_text = cstyle(text, style="red")
        print(styled_text)
        print(repr(styled_text))
        assert len(styled_text) > len(text)
        assert text in styled_text

        state2 = State.snapshot()

        # -- Test
        print("print-test-before")
        cout("cout-test-before")

        state3 = State.snapshot()

        with apio_runner.with_logger() as log:
            state4 = State.snapshot()

            print("print-test-inside")
            cout("cout-test-inside")

        state5 = State.snapshot()

        print("\n*** LOG:")
        print(log.out)
        print()

        print("print-test-after")
        cout("cout-test-after")

        # -- Dump state snapshots
        print(f"{state1=}")
        print(f"{state2=}")
        print(f"{state3=}")
        print(f"{state4=}")
        print(f"{state5=}")

        # -- Verify
        assert "print-test-before" not in log.out
        assert "cout-test-before" not in log.out

        assert "print-test-inside" in log.out
        assert "cout-test-inside" in log.out

        assert "print-test-after" not in log.out
        assert "cout-test-after" not in log.out


def test_logger_with_apio_ctx(apio_runner: ApioRunner):
    """Tests ApioRunner logger functionality with sandbox and ,
    apio context. This is the most typical test configuration."""

    with apio_runner.in_sandbox() as sb:

        state1 = State.snapshot()

        # -- Create an apio context with a fake project.
        sb.write_default_apio_ini()
        _ = ApioContext(
            project_policy=ProjectPolicy.PROJECT_REQUIRED,
            remote_config_policy=RemoteConfigPolicy.CACHED_OK,
            packages_policy=PackagesPolicy.ENSURE_PACKAGES,
        )

        state2 = State.snapshot()

        # -- Test
        print("print-test-before")
        cout("cout-test-before")

        state3 = State.snapshot()

        with apio_runner.with_logger() as log:
            state4 = State.snapshot()

            print("print-test-inside")
            cout("cout-test-inside")

        state5 = State.snapshot()

        print("\n*** LOG:")
        print(log.out)
        print()

        print("print-test-after")
        cout("cout-test-after")

        # -- Dump state snapshots
        print(f"{state1=}")
        print(f"{state2=}")
        print(f"{state3=}")
        print(f"{state4=}")
        print(f"{state5=}")

        # -- Verify
        assert "print-test-before" not in log.out
        assert "cout-test-before" not in log.out

        assert "print-test-inside" in log.out
        assert "cout-test-inside" in log.out

        assert "print-test-after" not in log.out
        assert "cout-test-after" not in log.out
