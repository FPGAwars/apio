"""Test for build_report.py."""

from pathlib import Path
import pytest
from pytest import LogCaptureFixture
from tests.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.common.build_report import (
    ResourceReport,
    ClockReport,
    BuildReport,
    read_build_report,
)

# -- Test json for ECP5. Having 'TRELLIS' in a utilization key indicates
# -- that's it's ECP5.
ECP5_TEST_SUMMARY = """
{
  "other-stuff": {
    "bla-bla": "bla-bla"
  },
  "utilization": {
    "SIOLOGIC": {
      "available": 69,
      "used": 0
    },
    "TRELLIS_COMB": {
      "available": 24288,
      "used": 12144
    },
    "TRELLIS_ECLKBUF": {
      "available": 8,
      "used": 0
    }
  },
  "fmax": {
    "$glbnet$MY_CLK$TRELLIS_IO_IN": {
      "achieved": 295.420,
      "constraint": 12
    }
  }
}
"""


# -- Test json for non ECP5. The utilization keys do not contain "TRELLIS".
# -- Note that the user clock name "CLK" is at different part of the fmax keys
# -- compared to ECP5 above.
NON_ECP5_TEST_SUMMARY = """
{
  "other-stuff": {
    "bla-bla": "bla-bla"
  },
  "utilization": {
    "ICESTORM_LC": {
      "available": 7680,
      "used": 27
    },
    "ICESTORM_PLL": {
      "available": 2,
      "used": 0
    }
  },
  "fmax": {
    "MY_CLK$SB_IO_IN_$glb_clk": {
      "achieved": 194.363,
      "constraint": 12
    }
  }
}
"""


def test_ecp5_read_build_report(apio_runner):
    """Tests the read_build_report() function for ECP 5 hardware.pnr."""

    with apio_runner.in_sandbox() as sb:

        file_path = Path("_build/default/hardware.pnr")

        sb.write_file(file_path, ECP5_TEST_SUMMARY)

        build_report = read_build_report(file_path)
        assert isinstance(build_report, BuildReport)

        print(build_report)

        assert build_report == BuildReport(
            resources=[
                ResourceReport(
                    name="SIOLOGIC", available=69, used=0, percentage=0.0
                ),
                ResourceReport(
                    name="TRELLIS_COMB",
                    available=24288,
                    used=12144,
                    percentage=50.0,
                ),
                ResourceReport(
                    name="TRELLIS_ECLKBUF", available=8, used=0, percentage=0.0
                ),
            ],
            clocks=[ClockReport(name="MY_CLK", fmax_mhz=295.420)],
        )


def test_non_ecp5_read_build_report(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests the read_build_report() function for non ECP 5 hardware.pnr."""

    with apio_runner.in_sandbox() as sb:

        file_path = Path("_build/default/hardware.pnr")

        sb.write_file(file_path, NON_ECP5_TEST_SUMMARY)

        build_report = read_build_report(file_path)
        assert isinstance(build_report, BuildReport)

        print(build_report)

        assert build_report == BuildReport(
            resources=[
                ResourceReport(
                    name="ICESTORM_LC",
                    available=7680,
                    used=27,
                    percentage=0.3515625,
                ),
                ResourceReport(
                    name="ICESTORM_PLL", available=2, used=0, percentage=0.0
                ),
            ],
            clocks=[ClockReport(name="MY_CLK", fmax_mhz=194.363)],
        )


def test_hardware_pnr_reading_failure(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests the case where reading hardware.pne fails."""
    with apio_runner.in_sandbox():
        file_path = Path("_build/default/hardware.pnr")
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            # -- Since we didn't create hardware.pnr, reading should fail.
            read_build_report(file_path)
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Failed to read" in cunstyle(captured.out)


def test_hardware_pnr_parsing_failure(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests the case where reading hardware.pne fails."""
    with apio_runner.in_sandbox() as sb:
        file_path = Path("_build/default/hardware.pnr")
        sb.write_file(file_path, "Broken JSON file")
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            # -- Since we didn't create hardware.pnr, reading should fail.
            read_build_report(file_path)
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Failed parsing json file" in cunstyle(captured.out)
