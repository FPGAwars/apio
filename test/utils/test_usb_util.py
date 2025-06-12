"""Tests of usb_util.py"""

from typing import List
from apio.utils.usb_util import (
    UsbDevice,
    UsbDeviceFilter,
)


def test_device_summaries():
    """Test usb device summary() string."""
    device = UsbDevice("0403", "6010", 0, 1, "m0", "p0", "sn0", "t0")
    assert device.summary() == "[0403:6010] [0:1] [m0] [p0] [sn0]"


def test_filtering():
    """Test the filtering function."""
    devs: List[UsbDevice] = [
        UsbDevice("0403", "6010", 0, 1, "m0", "p0", "sn0", "t0"),  # devs[0]
        UsbDevice("0403", "6020", 3, 1, "m1", "p1", "sn1", "t1"),  # devs[1]
        UsbDevice("0405", "6020", 3, 1, "m2", "p2", "sn2", "t2"),  # devs[2]
        UsbDevice("0403", "6020", 2, 1, "m3", "p3", "sn3", "t3"),  # devs[3]
        UsbDevice("0403", "6010", 1, 1, "m4", "p4", "sn4", "t4"),  # devs[4]
        UsbDevice("0405", "6010", 1, 1, "m5", "p5", "sn5", "t5"),  # devs[5]
    ]

    # -- All filtering disabled.
    filt = UsbDeviceFilter()
    assert filt.summary() == "[all]"
    assert filt.filter(devs) == devs

    # -- Filter by VID
    filt = UsbDeviceFilter().set_vendor_id("9999")
    assert filt.summary() == "[VID=9999]"
    assert filt.filter(devs) == []

    filt = UsbDeviceFilter().set_vendor_id("0405")
    assert filt.summary() == "[VID=0405]"
    assert filt.filter(devs) == [devs[2], devs[5]]

    # -- Filter by PID
    filt = UsbDeviceFilter().set_product_id("9999")
    assert filt.summary() == "[PID=9999]"
    assert filt.filter(devs) == []

    filt = UsbDeviceFilter().set_product_id("6020")
    assert filt.summary() == "[PID=6020]"
    assert filt.filter(devs) == [devs[1], devs[2], devs[3]]

    # -- Filter by description regex
    filt = UsbDeviceFilter().set_product_regex("no-such-device")
    assert filt.summary() == '[REGEX="no-such-device"]'
    assert filt.filter(devs) == []

    filt = UsbDeviceFilter().set_product_regex("^p2$")
    assert filt.summary() == '[REGEX="^p2$"]'
    assert filt.filter(devs) == [devs[2]]

    filt = UsbDeviceFilter().set_product_regex("p2")
    assert filt.summary() == '[REGEX="p2"]'
    assert filt.filter(devs) == [devs[2]]

    filt = UsbDeviceFilter().set_product_regex("(p3)|(p2)")
    assert filt.summary() == '[REGEX="(p3)|(p2)"]'
    assert filt.filter(devs) == [devs[2], devs[3]]

    # -- Filter by serial number
    filt = UsbDeviceFilter().set_serial_num("no-such-device")
    assert filt.summary() == '[S/N="no-such-device"]'
    assert filt.filter(devs) == []

    filt = UsbDeviceFilter().set_serial_num("sn2")
    assert filt.summary() == '[S/N="sn2"]'
    assert filt.filter(devs) == [devs[2]]

    # -- Filter by VID, PID
    filt = UsbDeviceFilter().set_vendor_id("0403").set_product_id("6010")
    assert filt.summary() == "[VID=0403, PID=6010]"
    assert filt.filter(devs) == [devs[0], devs[4]]
