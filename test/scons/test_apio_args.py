"""
Tests of the scons apio_args.py functions.
"""

import os
from test.conftest import ApioRunner
import pytest
from pytest import LogCaptureFixture
from apio.scons.apio_args import ApioArgs

# -- Allow assertions such as xyz == []
# pylint: disable=use-implicit-booleaness-not-comparison


def test_apio_args_with_values(apio_runner: ApioRunner):
    """Tests all args with actual values."""

    with apio_runner.in_sandbox():

        scons_args = {
            "prog": "programmer",
            "platform_id": "platform123",
            "fpga_arch": "arch1",
            "fpga_part_num": "part_num_0001",
            "fpga_type": "type1",
            "fpga_pack": "pack1",
            "fpga_speed": "7",
            "top_module": "top1",
            "testbench": "testbench1",
            "nowarn": "warn1,warn2",
            "warn": "warn3,warn4",
            "graph_spec": "spec1",
            "verbose_all": "True",
            "verbose_synth": "True",
            "verbose_pnr": "True",
            "force_sim": "True",
            "all": "True",
            "nostyle": "True",
        }

        os.environ["YOSYS_LIB"] = "yosys_path"
        os.environ["TRELLIS"] = "trellis_path"

        apio_args = ApioArgs.make(scons_args, is_debug=False)

        assert apio_args.PLATFORM_ID == "platform123"
        assert apio_args.PROG == "programmer"
        assert apio_args.FPGA_ARCH == "arch1"
        assert apio_args.FPGA_PART_NUM == "part_num_0001"
        assert apio_args.FPGA_TYPE == "type1"
        assert apio_args.FPGA_PACK == "pack1"
        assert apio_args.FPGA_SPEED == "7"
        assert apio_args.TOP_MODULE == "top1"
        assert apio_args.TESTBENCH == "testbench1"
        assert apio_args.VERILATOR_NOWARNS == ["warn1", "warn2"]
        assert apio_args.VERILATOR_WARNS == ["warn3", "warn4"]
        assert apio_args.GRAPH_SPEC == "spec1"
        assert apio_args.VERBOSE_ALL is True
        assert apio_args.VERBOSE_SYNTH is True
        assert apio_args.VERBOSE_PNR is True
        assert apio_args.FORCE_SIM is True
        assert apio_args.VERILATOR_ALL is True
        assert apio_args.VERILATOR_NO_STYLE is True
        assert apio_args.YOSYS_PATH == "yosys_path"
        assert apio_args.TRELLIS_PATH == "trellis_path"


def test_apio_args_no_values(apio_runner: ApioRunner):
    """Tests all args, but the required ones, with default values."""

    with apio_runner.in_sandbox():

        scons_args = {
            "platform_id": "platform123",
        }

        # -- Required env vars.
        os.environ["YOSYS_LIB"] = "yosys_path"
        os.environ["TRELLIS"] = "trellis_path"

        apio_args = ApioArgs.make(scons_args, is_debug=False)

        assert apio_args.PLATFORM_ID == "platform123"
        assert apio_args.PROG == ""
        assert apio_args.FPGA_ARCH == ""
        assert apio_args.FPGA_PART_NUM == ""
        assert apio_args.FPGA_TYPE == ""
        assert apio_args.FPGA_PACK == ""
        assert apio_args.FPGA_SPEED == ""
        assert apio_args.TOP_MODULE == ""
        assert apio_args.TESTBENCH == ""
        assert apio_args.VERILATOR_NOWARNS == []
        assert apio_args.VERILATOR_WARNS == []
        assert apio_args.GRAPH_SPEC == ""
        assert apio_args.VERBOSE_ALL is False
        assert apio_args.VERBOSE_SYNTH is False
        assert apio_args.VERBOSE_PNR is False
        assert apio_args.FORCE_SIM is False
        assert apio_args.VERILATOR_ALL is False
        assert apio_args.VERILATOR_NO_STYLE is False
        assert apio_args.YOSYS_PATH == "yosys_path"
        assert apio_args.TRELLIS_PATH == "trellis_path"


def test_ignored_arg(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Tests the error message when an unknown arg is passed."""
    with apio_runner.in_sandbox():

        # -- Scons args with an unknown arg
        scons_args = {
            "platform_id": "platform123",
            "no_such_arg": "value",
        }

        # -- Required env vars.
        os.environ["YOSYS_LIB"] = "yosys_path"
        os.environ["TRELLIS"] = "trellis_path"

        # -- Run the function, expecting an exit with an error.
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            ApioArgs.make(scons_args, is_debug=True)
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Unknown scons args: ['no_such_arg']" in captured.out


def test_missing_required_arg(apio_runner: ApioRunner):
    """Tests the error message when a require arg is missing"""
    with apio_runner.in_sandbox():

        # -- Required arg "platform_id" is missing.
        scons_args = {
            "prog": "programmer",
            "fpga_arch": "arch1",
            "fpga_part_num": "part_num_0001",
        }

        # -- Required env vars.
        os.environ["YOSYS_LIB"] = "yosys_path"
        os.environ["TRELLIS"] = "trellis_path"

        # -- Run the function, expecting an exit with an error.
        with pytest.raises(AssertionError) as e:
            ApioArgs.make(scons_args, is_debug=False)
        assert "platform_id scons arg is required" in str(e)


def test_missing_required_env_var(apio_runner: ApioRunner):
    """Tests the error message when a required env var is
    missing."""

    with apio_runner.in_sandbox():

        scons_args = {
            "platform_id": "platform123",
        }

        # -- Required env YOSYS_LIB is missing.
        os.environ["TRELLIS"] = "trellis_path"

        # -- Run the function, expecting an exit with an error.
        with pytest.raises(AssertionError) as e:
            ApioArgs.make(scons_args, is_debug=False)
        assert "YOSYS_PATH env var is required" in str(e)
