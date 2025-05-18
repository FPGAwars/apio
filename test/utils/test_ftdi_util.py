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
# -- See issue https://github.com/trabucayre/openFPGALoader/issues/549
TEXT_WITH_DEVICES = """
empty
Bus device vid:pid       probe type      manufacturer serial               product
000 001    0x0403:0x6010 FTDI2232        AlhambraBits none                 Alhambra II v1.0A - B09-335
001 001    0x0403:0x6010 FTDI2232        tinyVision.ai FT94RQ8V             UPduino v3.1c
002 001    0x0403:0x6010 FTDI2232        tinyVision.ai.v3 FT94RQ8V             UPduino v3.1c
"""

# -- Text when no device is connected.
TEXT_NO_DEVICES = """
empty
No USB devices found
Bus device vid:pid       probe type      manufacturer serial               product
"""

# -- Per https://tinyurl.com/3wxeawkv , testing with both old and new names.
PROGRAM_TYPE_TITLES = ["probe type", "probe_type"]


def test_text_with_devices():
    """Test parsing of 'openFPGALoader --scan-usb' text that contains devices."""

    # pylint: disable=protected-access

    for title in PROGRAM_TYPE_TITLES:
        print(f"{title=}")

        text = TEXT_WITH_DEVICES.replace("probe type", title)

        devices = _get_devices_from_text(text)

        expected = [
            FtdiDeviceInfo(
                bus=0,
                device=1,
                vendor_id="0403",
                product_id="6010",
                type="FTDI2232",
                manufacturer="AlhambraBits",
                serial_code="",
                description="Alhambra II v1.0A - B09-335",
            ),
            FtdiDeviceInfo(
                bus=1,
                device=1,
                vendor_id="0403",
                product_id="6010",
                type="FTDI2232",
                manufacturer="tinyVision.ai",
                serial_code="FT94RQ8V",
                description="UPduino v3.1c",
            ),
            FtdiDeviceInfo(
                bus=2,
                device=1,
                vendor_id="0403",
                product_id="6010",
                type="FTDI2232",
                manufacturer="tinyVision.ai.v3",
                serial_code="FT94RQ8V",
                description="UPduino v3.1c",
            ),
        ]

        assert devices == expected


def test_text_without_devices():
    """Test parsing of 'openFPGALoader --scan-usb' text that contains
    no devices."""

    # pylint: disable=protected-access
    # pylint: disable=use-implicit-booleaness-not-comparison

    for title in ["probe type", "probe_type"]:
        print(f"{title=}")

        text = TEXT_NO_DEVICES.replace("probe type", title)

        devices = _get_devices_from_text(text)

        assert devices == []


def test_filter_ftdi_devices():
    last_bus = -1

    # -- A helper function to generate fake devices.
    def device(
        vendor_id: str,
        product_id: str,
        serial_code: str,
        description: str,
    ) -> FtdiDeviceInfo:
        nonlocal last_bus
        last_bus += 1
        return FtdiDeviceInfo(
            bus=last_bus,
            device=0,
            vendor_id=vendor_id,
            product_id=product_id,
            type="Fake Type",
            manufacturer="Fake Manufacturer",
            serial_code=serial_code,
            description=description,
        )

    # -- Create a list of fake devices.
    devices: List[FtdiDeviceInfo] = [
        device("0403", "6010", "SER01", "Description 0001"),
        device("0410", "6020", "SER02", "Description 0002"),
        device("0403", "6020", "SER03", "Description 0003"),
        device("0403", "6010", "SER04", "Description 0001"),
        device("0410", "6020", "SER05", "Description 0002"),
        device("0403", "6020", "SER06", "Description 0003"),
        device("0403", "6010", "SER07", "Description 0001"),
        device("0410", "6020", "SER08", "Description 0002"),
        device("0403", "6020", "SER09", "Description 0003"),
    ]

    # -- All filtering disabled.
    filtered = FtdiDeviceFilter().filter(devices)
    assert filtered == devices

    # -- Filter by VID.
    filtered = FtdiDeviceFilter().vendor_id("9999").filter(devices)
    assert filtered == []

    filtered = FtdiDeviceFilter().vendor_id("0403").filter(devices)
    serials = [f.serial_code for f in filtered]
    assert serials == ["SER01", "SER03", "SER04", "SER06", "SER07", "SER09"]

    # # -- Filter by PID
    filtered = FtdiDeviceFilter().product_id("9999").filter(devices)
    assert filtered == []

    filtered = FtdiDeviceFilter().product_id("6020").filter(devices)
    serials = [f.serial_code for f in filtered]
    assert serials == ["SER02", "SER03", "SER05", "SER06", "SER08", "SER09"]

    # -- Filter by serial code.
    filtered = FtdiDeviceFilter().serial_code("9999").filter(devices)
    assert filtered == []

    filtered = FtdiDeviceFilter().serial_code("SER05").filter(devices)
    serials = [f.serial_code for f in filtered]
    assert serials == ["SER05"]

    # -- Filter by description regex. Note that the regex need to match
    # -- from the begining of the description.
    filtered = (
        FtdiDeviceFilter().description_regex("scription").filter(devices)
    )
    assert filtered == devices

    filtered = (
        FtdiDeviceFilter()
        .description_regex("^Description 0003")
        .filter(devices)
    )
    serials = [f.serial_code for f in filtered]
    assert serials == ["SER03", "SER06", "SER09"]

    filtered = FtdiDeviceFilter().description_regex("^0003").filter(devices)
    assert filtered == []

    filtered = (
        FtdiDeviceFilter()
        .vendor_id("0403")
        .product_id("6020")
        .serial_code("SER06")
        .description_regex("0003")
        .filter(devices)
    )
    serials = [f.serial_code for f in filtered]
    assert serials == ["SER06"]
