"""Test for build_report.py."""

import json
from pathlib import Path
import pytest
from tests.conftest import ApioRunner
from apio.common.proto.apio_common_pb2 import ApioArch
from apio.common.build_report import (
    ResourceReport,
    ClockReport,
    BuildReport,
    read_build_report,
)

# -- Simplified hardware.pnr for testing ICE40.
TEST_SUMMARY_ICE40 = {
    "other-stuff": {"bla-bla": "bla-bla"},
    "utilization": {
        "ICESTORM_PLL": {"available": 2, "used": 0},
        "ICESTORM_LC": {"available": 7680, "used": 27},
    },
    "fmax": {
        "my_clk$SB_IO_IN_$glb_clk": {"achieved": 194.363, "constraint": 12}
    },
}

# -- Simplified hardware.pnr for testing ECP5.
TEST_SUMMARY_ECP5 = {
    "other-stuff": {"bla-bla": "bla-bla"},
    "utilization": {
        "TRELLIS_ECLKBUF": {"available": 8, "used": 0},
        "SIOLOGIC": {"available": 69, "used": 0},
        "TRELLIS_COMB": {"available": 24288, "used": 12144},
    },
    "fmax": {
        "$glbnet$my_clk$TRELLIS_IO_IN": {"achieved": 295.420, "constraint": 12}
    },
}

# -- Simplified hardware.pnr for testing GOWIN.
TEST_SUMMARY_GOWIN = {
    "other-stuff": {"bla-bla": "bla-bla"},
    "utilization": {
        "IOB": {"available": 276, "used": 2},
        "IOLOGICI": {"available": 276, "used": 0},
        "LUT4": {"available": 8640, "used": 12},
    },
    "fmax": {"sys_clk_IBUF_I_O": {"achieved": 197.745, "constraint": 12}},
}

# -- Simplified hardware.pnr for testing Xilinx.
TEST_SUMMARY_XILINX = {
    "utilization": {
        "BUFGCTRL": {"available": 32, "used": 1},
        "PSEUDO_GND": {"available": 1, "used": 1},
        "SLICE_LUTX": {"available": 65200, "used": 48},
    },
    "fmax": {
        "$iopadmap$clk": {
            "achieved": 398.88311767578125,
            "constraint": 12,
        }
    },
}


def _resource(name: str, available: int, used: int) -> ResourceReport:
    """Construct a ResourceReport for testing."""
    return ResourceReport(
        name=name,
        available=available,
        used=used,
        percentage=100 * used / available,
    )


def test_read_build_report_ice40(apio_runner: ApioRunner):
    """Tests the read_build_report() function for ICE40 hardware.pnr."""

    with apio_runner.in_sandbox() as sb:

        file_path = Path("_build/default/hardware.pnr")

        sb.write_json_file(file_path, TEST_SUMMARY_ICE40)

        build_report = read_build_report(file_path)
        assert isinstance(build_report, BuildReport)

        print(build_report)

        assert build_report == BuildReport(
            arch=ApioArch.ice40,
            resources=[
                _resource("ICESTORM_LC", 7680, 27),
                _resource("ICESTORM_PLL", 2, 0),
            ],
            clocks=[ClockReport(name="my_clk", fmax_mhz=194.363)],
        )


def test_read_build_report_ecp5(apio_runner):
    """Tests the read_build_report() function for ECP5 hardware.pnr."""

    with apio_runner.in_sandbox() as sb:

        file_path = Path("_build/default/hardware.pnr")

        sb.write_json_file(file_path, TEST_SUMMARY_ECP5)

        build_report = read_build_report(file_path)
        assert isinstance(build_report, BuildReport)

        print(build_report)

        assert build_report == BuildReport(
            arch=ApioArch.ecp5,
            resources=[
                _resource("SIOLOGIC", 69, 0),
                _resource("TRELLIS_COMB", 24288, 12144),
                _resource("TRELLIS_ECLKBUF", 8, 0),
            ],
            clocks=[ClockReport(name="my_clk", fmax_mhz=295.420)],
        )


def test_read_build_report_gowin(apio_runner):
    """Tests the read_build_report() function for GOWIN hardware.pnr."""

    with apio_runner.in_sandbox() as sb:

        file_path = Path("_build/default/hardware.pnr")

        sb.write_json_file(file_path, TEST_SUMMARY_GOWIN)

        build_report = read_build_report(file_path)
        assert isinstance(build_report, BuildReport)

        print(build_report)

        assert build_report == BuildReport(
            arch=ApioArch.gowin,
            resources=[
                _resource("IOB", 276, 2),
                _resource("IOLOGICI", 276, 0),
                _resource("LUT4", 8640, 12),
            ],
            clocks=[ClockReport(name="sys_clk", fmax_mhz=197.745)],
        )


def test_read_build_report_xilinx(apio_runner):
    """Tests the read_build_report() function for XILINX hardware.pnr."""
    with apio_runner.in_sandbox() as sb:
        file_path = Path("_build/default/hardware.pnr")
        sb.write_json_file(file_path, TEST_SUMMARY_XILINX)

        build_report = read_build_report(file_path)

        assert build_report == BuildReport(
            arch=ApioArch.xilinx,
            resources=[
                _resource("BUFGCTRL", 32, 1),
                _resource("PSEUDO_GND", 1, 1),
                _resource("SLICE_LUTX", 65200, 48),
            ],
            clocks=[
                ClockReport(name="clk", fmax_mhz=398.88311767578125),
            ],
        )
        assert build_report.clocks[0].name != ""


def test_hardware_pnr_reading_failure(apio_runner: ApioRunner):
    """Tests the case where reading hardware.pne fails."""
    with apio_runner.in_sandbox():
        file_path = Path("_build/default/hardware.pnr")
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                # -- Since we didn't create hardware.pnr, reading should fail.
                read_build_report(file_path)
        assert e.value.code == 1
        assert "Error: Failed to read" in log.out


def test_hardware_pnr_parsing_failure(apio_runner: ApioRunner):
    """Tests the case where reading hardware.pne fails."""
    with apio_runner.in_sandbox() as sb:
        file_path = Path("_build/default/hardware.pnr")
        sb.write_file(file_path, "Broken JSON file")
        with apio_runner.with_logger() as log:
            with pytest.raises(SystemExit) as e:
                # -- Since we didn't create hardware.pnr, reading should fail.
                read_build_report(file_path)
        assert e.value.code == 1
        assert "Error: Failed parsing json file" in log.out
