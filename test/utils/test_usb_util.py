"""
Tests of usb_util.py
"""

from typing import List
from apio.utils.usb_util import (
    UsbDevice,
    UsbDeviceFilter,
)


def test_filter_usb_devices():
    """Test the filtering function."""
    devs: List[UsbDevice] = [
        UsbDevice(0, 1, "0403", "6010", "m0", "p0", "s0", "t0"),  # devs[0]
        UsbDevice(3, 1, "0403", "6020", "m1", "p1", "s1", "t1"),  # devs[1]
        UsbDevice(3, 1, "0405", "6020", "m2", "p2", "s2", "t2"),  # devs[2]
        UsbDevice(2, 1, "0403", "6020", "m3", "p3", "s3", "t3"),  # devs[3]
        UsbDevice(1, 1, "0403", "6010", "m4", "p4", "s4", "t4"),  # devs[4]
        UsbDevice(1, 1, "0405", "6010", "m5", "p5", "s5", "t5"),  # devs[5]
    ]

    # -- All filtering disabled.
    usb_filter = UsbDeviceFilter()
    assert usb_filter.summary() == "[all]"
    assert usb_filter.filter(devs) == devs

    # -- Filter by VID
    usb_filter = UsbDeviceFilter().set_vendor_id("9999")
    assert usb_filter.summary() == "[VID=9999]"
    assert usb_filter.filter(devs) == []

    usb_filter = UsbDeviceFilter().set_vendor_id("0405")
    assert usb_filter.summary() == "[VID=0405]"
    assert usb_filter.filter(devs) == [devs[2], devs[5]]

    # -- Filter by PID
    usb_filter = UsbDeviceFilter().set_product_id("9999")
    assert usb_filter.summary() == "[PID=9999]"
    assert usb_filter.filter(devs) == []

    usb_filter = UsbDeviceFilter().set_product_id("6020")
    assert usb_filter.summary() == "[PID=6020]"
    assert usb_filter.filter(devs) == [devs[1], devs[2], devs[3]]

    # -- Filter by VID, PID
    usb_filter = UsbDeviceFilter().set_vendor_id("0403").set_product_id("6010")
    assert usb_filter.summary() == "[VID=0403, PID=6010]"
    assert usb_filter.filter(devs) == [devs[0], devs[4]]
