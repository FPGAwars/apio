"""
Tests of apio.managers.system.py
"""

from test.conftest import ApioRunner
from apio.managers.system import System
from apio.apio_context import ApioContext, ApioContextScope

# pylint: disable=fixme
# TODO: Add more tests.

# pylint: disable=protected-access
# pylint: disable=use-implicit-booleaness-not-comparison


def test_parse_lsftdi_devices(apio_runner: ApioRunner):
    """Test the parsing of the lsftdi command output."""

    with apio_runner.in_sandbox():

        # -- Setup a System object
        apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)
        sys = System(apio_ctx)

        # -- NOTE: The test text below was generated with 'apio raw -- lsftdi'.

        # -- Test with no devices.
        devices = sys._parse_lsftdi_devices("Number of FTDI devices found: 0")
        assert devices == []

        # -- Test with a single device.
        devices = sys._parse_lsftdi_devices(
            "Number of FTDI devices found: 1\n"
            "Checking device: 0\n"
            "Manufacturer: AlhambraBits, Description: Alhambra II v1.0A - "
            "B09-335\n"
        )
        assert devices == [
            {
                "description": "Alhambra II v1.0A - B09-335",
                "index": "0",
                "manufacturer": "AlhambraBits",
            }
        ]

        # -- Test with two devices.
        devices = sys._parse_lsftdi_devices(
            "Number of FTDI devices found: 2\n"
            "Checking device: 0\n"
            "Manufacturer: tinyVision.ai, Description: UPduino v3.1c\n"
            "\n"
            "Checking device: 1\n"
            "Manufacturer: AlhambraBits, Description: Alhambra II v1.0A - "
            "B09-335\n"
        )
        assert devices == [
            {
                "index": "0",
                "manufacturer": "tinyVision.ai",
                "description": "UPduino v3.1c",
            },
            {
                "index": "1",
                "manufacturer": "AlhambraBits",
                "description": "Alhambra II v1.0A - B09-335",
            },
        ]
