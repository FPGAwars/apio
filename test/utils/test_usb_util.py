"""
Tests of usb_util.py
"""

from typing import List
from apio.utils.usb_util import (
    UsbDeviceInfo,
    UsbDeviceFilter,
    _get_devices_from_text,
)


# -- Simulated 'lsusb' output text.
TEXT_WITH_DEVICES = "\n".join(
    [
        "0403:6010 (bus 1, device 1) path: 1",
        "0403:6010 (bus 0, device 1) path: 1",
        "1022:15e0 (bus 2, device 0)",
        "0b0e:0305 (bus 2, device 6) path: 4.4",
        "0403:6010 (bus 2, device 8) path: 4.3.1",
    ]
)


# -- Text when no device is connected.
TEXT_NO_DEVICES = "\n"


def test_text_with_devices():
    """Test parsing of 'lsusb' text that contains devices."""

    # -- Devices are returned sorted.
    devices = _get_devices_from_text(TEXT_WITH_DEVICES)

    expected = [
        UsbDeviceInfo(
            bus=0, device=1, vendor_id="0403", product_id="6010", path="1"
        ),
        UsbDeviceInfo(
            bus=1, device=1, vendor_id="0403", product_id="6010", path="1"
        ),
        UsbDeviceInfo(
            bus=2, device=8, vendor_id="0403", product_id="6010", path="4.3.1"
        ),
        UsbDeviceInfo(
            bus=2, device=6, vendor_id="0B0E", product_id="0305", path="4.4"
        ),
        UsbDeviceInfo(
            bus=2, device=0, vendor_id="1022", product_id="15E0", path=""
        ),
    ]

    assert devices == expected


def test_text_without_devices():
    """Test parsing of 'lsusb' text that containsno devices."""

    devices = _get_devices_from_text(TEXT_NO_DEVICES)

    assert devices == []


def test_filter_usb_devices():
    """Test the filtering function."""
    devs: List[UsbDeviceInfo] = [
        UsbDeviceInfo(0, 1, "0403", "6010", "0"),  # devs[0]
        UsbDeviceInfo(3, 1, "0403", "6020", "1"),  # devs[1]
        UsbDeviceInfo(3, 1, "0405", "6020", "2"),  # devs[2]
        UsbDeviceInfo(2, 1, "0403", "6020", "3"),  # devs[3]
        UsbDeviceInfo(1, 1, "0403", "6010", "4"),  # devs[4]
        UsbDeviceInfo(1, 1, "0405", "6010", "5"),  # devs[5]
    ]

    # -- All filtering disabled.
    filtered = UsbDeviceFilter().filter(devs)
    assert filtered == devs

    # -- Filter by VID
    filtered = UsbDeviceFilter().vendor_id("9999").filter(devs)
    assert filtered == []

    filtered = UsbDeviceFilter().vendor_id("0405").filter(devs)
    assert filtered == [devs[2], devs[5]]

    # -- Filter by PID
    filtered = UsbDeviceFilter().product_id("9999").filter(devs)
    assert filtered == []

    filtered = UsbDeviceFilter().product_id("6020").filter(devs)
    assert filtered == [devs[1], devs[2], devs[3]]

    # -- Filter by VID, PID
    filtered = (
        UsbDeviceFilter().vendor_id("0403").product_id("6010").filter(devs)
    )
    assert filtered == [devs[0], devs[4]]
