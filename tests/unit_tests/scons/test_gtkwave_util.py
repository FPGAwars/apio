"""
Tests of gtkwave_util.py
"""

from pathlib import Path
from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio
from apio.scons.gtkwave_util import create_gtkwave_file, _signal_sort_key

# Expected default gtkw file lines for the examples we use below.
EXPECTED_GTKW_LINES = [
    "# GTKWave display configuration for 'apio sim main_tb.v'",
    "# THIS FILE WAS GENERATED AUTOMATICALLY BY APIO.",
    "# DO NOT EDIT IT MANUALLY!",
    "# To customize this file, run 'apio sim main_tb.v'",
    "# and save the file from GTKWave.",
    "",
    "[*] GTKWave Analyzer v3.4.0 (w)1999-2022 BSI",
    "",
    "[*]",
    "testbench.CLK",
    "testbench.expected_led",
    "testbench.i[31:0]",
    "testbench.LED1",
    "testbench.LED2",
    "",
]


def test_signal_sort_key():
    """Test the default signals sorting heuristic."""

    # -- Priority 1: clock.
    assert _signal_sort_key("tb.clk") == ("tb", 1, "clk")
    assert _signal_sort_key("tb.Clk") == ("tb", 1, "clk")
    assert _signal_sort_key("tb.sys_clk") == ("tb", 1, "sys_clk")
    assert _signal_sort_key("tb.clock1") == ("tb", 1, "clock1")
    assert _signal_sort_key("tb.CLOCK1") == ("tb", 1, "clock1")

    # -- Priority 2: reset.
    assert _signal_sort_key("tb.rst") == ("tb", 2, "rst")
    assert _signal_sort_key("tb.RST") == ("tb", 2, "rst")
    assert _signal_sort_key("tb.Reset") == ("tb", 2, "reset")
    assert _signal_sort_key("tb.reset") == ("tb", 2, "reset")
    assert _signal_sort_key("tb.reset_n") == ("tb", 2, "reset_n")
    assert _signal_sort_key("tb.sys_rst") == ("tb", 2, "sys_rst")
    assert _signal_sort_key("tb.sys_reset") == ("tb", 2, "sys_reset")
    assert _signal_sort_key("tb.RESET_N") == ("tb", 2, "reset_n")

    # -- Priority 3: all other signals.
    assert _signal_sort_key("tb.other") == ("tb", 3, "other")
    assert _signal_sort_key("tb.Other") == ("tb", 3, "other")
    assert _signal_sort_key("tb.OTHER") == ("tb", 3, "other")


def test_create_gtkwave_file(apio_runner: ApioRunner):
    """Test the create_gtkwave_file() function"""

    with apio_runner.in_sandbox() as sb:

        # -- Create relative paths to the .gtkw and .vcd files
        gtkw_path = Path("main_tb.gtkw")
        vcd_path = Path("_build/blink-slow/main_tb.vcd")

        # -- Execute "apio examples fetch alhambra-ii/getting-started"
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "alhambra-ii/getting-started"]
        )
        sb.assert_result_ok(result)

        # -- Execute "apio test main_tb.v" to create the .vcd file
        result = sb.invoke_apio_cmd(apio, ["test", "main_tb.v"])
        sb.assert_result_ok(result)

        # -- Verify that the .vcd file exists.
        assert vcd_path.is_file()

        # -- Delete the file main_tb.gtkw
        assert gtkw_path.is_file()
        gtkw_path.unlink()
        assert not gtkw_path.exists()

        # -- Create the default .gtkw file
        create_gtkwave_file("main_tb.v", str(vcd_path), str(gtkw_path))
        assert gtkw_path.is_file()

        # -- Test the generated .gtkw file.
        text = sb.read_file(gtkw_path)
        lines = text.split("\n")
        print(f"Actual {gtkw_path} lines:")
        for line in lines:
            print(f'    "{line}",')

        assert lines == EXPECTED_GTKW_LINES


def test_default_signals_creation(apio_runner: ApioRunner):
    """Test the automatic .gtkw file creation by 'apio sim'."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio examples fetch alhambra-ii/getting-started"
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "alhambra-ii/getting-started"]
        )
        sb.assert_result_ok(result)

        # -- Delete the file main_tb.gtkw
        gtkw_path = Path("main_tb.gtkw")
        assert gtkw_path.exists()
        gtkw_path.unlink()
        assert not gtkw_path.exists()

        # -- Execute "apio sim --no-gtkwave main_tb.v"
        result = sb.invoke_apio_cmd(apio, ["sim", "--no-gtkwave", "main_tb.v"])
        sb.assert_result_ok(result)
        assert gtkw_path.exists()

        # -- Test the generated .gtkw file.
        text = sb.read_file(gtkw_path)
        lines = text.split("\n")
        print(f"Actual {gtkw_path} lines:")
        for line in lines:
            print(f'    "{line}",')

        assert lines == EXPECTED_GTKW_LINES


def test_user_gtkw_file_protection(apio_runner: ApioRunner):
    """Test that a user's .gtkw file is not overwritten by apio'."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio examples fetch alhambra-ii/getting-started"
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "alhambra-ii/getting-started"]
        )
        sb.assert_result_ok(result)

        # -- Read the user's .gtkw file
        gtkw_path = Path("main_tb.gtkw")
        assert gtkw_path.exists()
        text_before = sb.read_file(gtkw_path)

        # gtkw_path.unlink()
        # assert not gtkw_path.exists()

        # -- Execute "apio sim --no-gtkwave main_tb.v"
        result = sb.invoke_apio_cmd(apio, ["sim", "--no-gtkwave", "main_tb.v"])
        sb.assert_result_ok(result)
        assert gtkw_path.exists()

        # -- Read the .gtkw file after the operation.
        assert gtkw_path.exists()
        text_after = sb.read_file(gtkw_path)

        # -- Verify that apio didn't change it.
        assert text_after == text_before
