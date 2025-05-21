"""
Tests of ftd_util.py
"""

from typing import List
from apio.utils.ftdi_util import (
    FtdiDeviceInfo,
    FtdiDeviceFilter,
    _get_devices_from_text,
)

# Ignore long lines.
# flake8: noqa: E501

# -- Simulated 'openFPGALoader --scan-usb' output text.
TEXT_WITH_DEVICES = """
empty
Bus device vid:pid       probe_type manufacturer     serial    product
000 001    0x0403:0x6010 FTDI2232   AlhambraBits     none      Alhambra II v1.0A - B09-335
001 001    0x0403:0x6010 FTDI2232   tinyVision.ai    FT94RQ8V  UPduino v3.1c
002 001    0x0403:0x6010 FTDI2232   tinyVision.ai.v3 FT94RQ8V  UPduino v3.1c
"""

# -- Text when no device is connected.
TEXT_NO_DEVICES = """
empty
No USB devices found
Bus device vid:pid  probe_type  manufacturer serial  product
"""


def test_text_with_devices():
    """Test parsing of 'openFPGALoader --scan-usb' text that contains devices."""

    devices = _get_devices_from_text(TEXT_WITH_DEVICES)

    expected = [
        FtdiDeviceInfo(
            bus=0,
            device=1,
            vendor_id="0403",
            product_id="6010",
            type="FTDI2232",
            manufacturer="AlhambraBits",
            serial_number="",
            description="Alhambra II v1.0A - B09-335",
        ),
        FtdiDeviceInfo(
            bus=1,
            device=1,
            vendor_id="0403",
            product_id="6010",
            type="FTDI2232",
            manufacturer="tinyVision.ai",
            serial_number="FT94RQ8V",
            description="UPduino v3.1c",
        ),
        FtdiDeviceInfo(
            bus=2,
            device=1,
            vendor_id="0403",
            product_id="6010",
            type="FTDI2232",
            manufacturer="tinyVision.ai.v3",
            serial_number="FT94RQ8V",
            description="UPduino v3.1c",
        ),
    ]

    assert devices == expected


def test_text_without_devices():
    """Test parsing of 'openFPGALoader --scan-usb' text that contains
    no devices."""

    # pylint: disable=use-implicit-booleaness-not-comparison

    devices = _get_devices_from_text(TEXT_NO_DEVICES)

    assert devices == []


def test_filter_ftdi_devices():
    """Test the filtering function."""
    last_bus = -1

    # -- A helper function to generate fake devices.
    def device(
        vendor_id: str,
        product_id: str,
        serial_number: str,
        description: str,
    ) -> FtdiDeviceInfo:
        """A helper function to create fake a FtdiDeviceInfo."""
        nonlocal last_bus
        last_bus += 1
        return FtdiDeviceInfo(
            bus=last_bus,
            device=0,
            vendor_id=vendor_id,
            product_id=product_id,
            type="Fake Type",
            manufacturer="Fake Manufacturer",
            serial_number=serial_number,
            description=description,
        )

    # -- Create a list of fake devices.
    devs: List[FtdiDeviceInfo] = [
        device("0403", "6010", "SER01", "Description 0001"),  # devs[0]
        device("0410", "6020", "SER02", "Description 0002"),  # devs[1]
        device("0403", "6020", "SER03", "Description 0003"),  # devs[2]
        device("0403", "6010", "SER04", "Description 0001"),  # devs[3]
        device("0410", "6020", "SER05", "Description 0002"),  # devs[4]
        device("0403", "6020", "SER06", "Description 0003"),  # devs[5]
        device("0403", "6010", "SER07", "Description 0001"),  # devs[6]
        device("0410", "6020", "SER08", "Description 0002"),  # devs[7]
        device("0403", "6020", "SER09", "Description 0003"),  # devs[8]
    ]

    # -- All filtering disabled.
    filtered = FtdiDeviceFilter().filter(devs)
    assert filtered == devs

    # -- Filter by VID.
    filtered = FtdiDeviceFilter().vendor_id("9999").filter(devs)
    assert filtered == []

    filtered = FtdiDeviceFilter().vendor_id("0403").filter(devs)
    assert filtered == [devs[0], devs[2], devs[3], devs[5], devs[6], devs[8]]

    # # -- Filter by PID
    filtered = FtdiDeviceFilter().product_id("9999").filter(devs)
    assert filtered == []

    filtered = FtdiDeviceFilter().product_id("6020").filter(devs)
    assert filtered == [devs[1], devs[2], devs[4], devs[5], devs[7], devs[8]]

    # -- Filter by serial code.
    filtered = FtdiDeviceFilter().serial_number("9999").filter(devs)
    assert filtered == []

    filtered = FtdiDeviceFilter().serial_number("SER05").filter(devs)
    assert filtered == [devs[4]]

    # -- Filter by description regex. Note that the regex need to match
    # -- from the begining of the description.
    filtered = FtdiDeviceFilter().description_regex("scription").filter(devs)
    assert filtered == devs

    filtered = (
        FtdiDeviceFilter().description_regex("^Description 0003").filter(devs)
    )
    assert filtered == [devs[2], devs[5], devs[8]]

    filtered = FtdiDeviceFilter().description_regex("^0003").filter(devs)
    assert filtered == []

    filtered = (
        FtdiDeviceFilter()
        .vendor_id("0403")
        .product_id("6020")
        .serial_number("SER06")
        .description_regex("0003")
        .filter(devs)
    )
    assert filtered == [devs[5]]
