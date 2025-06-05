"""
Tests of serial_util.py
"""

from typing import List
from apio.utils.serial_util import (
    SerialDevice,
    SerialDeviceFilter,
)


def test_device_summaries():
    """Test serial device summary() string."""
    device = SerialDevice(
        "dev/port0", "port0", "0403", "6010", "m0", "p0", "sn0", "t0", "l0"
    )
    assert device.summary() == "[dev/port0] [0403:6010, [m0] [p0] [sn0]"


def test_filtering():
    """Test the filtering function."""
    devs: List[SerialDevice] = [
        SerialDevice(  # devs[0]
            "port0",
            "name0",
            "0403",
            "6020",
            "manuf0",
            "product0",
            "serial0",
            "type0",
            "location0",
        ),
        SerialDevice(  # devs[1]
            "port1",
            "name1",
            "0405",
            "6010",
            "manuf1",
            "product1",
            "serial1",
            "type1",
            "location1",
        ),
        SerialDevice(  # devs[2]
            "port2",
            "name2",
            "0403",
            "6010",
            "manuf2",
            "product2",
            "serial2",
            "type2",
            "location2",
        ),
        SerialDevice(  # devs[3]
            "port3",
            "name3",
            "0405",
            "6020",
            "manuf3",
            "product3",
            "serial3",
            "type3",
            "location3",
        ),
    ]

    # -- All filtering disabled.
    filt = SerialDeviceFilter()
    assert filt.summary() == "[all]"
    assert filt.filter(devs) == devs

    # -- Filter by VID
    filt = SerialDeviceFilter().set_vendor_id("9999")
    assert filt.summary() == "[VID=9999]"
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().set_vendor_id("0405")
    assert filt.summary() == "[VID=0405]"
    assert filt.filter(devs) == [devs[1], devs[3]]

    # -- Filter by PID
    filt = SerialDeviceFilter().set_product_id("9999")
    assert filt.summary() == "[PID=9999]"
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().set_product_id("6020")
    assert filt.summary() == "[PID=6020]"
    assert filt.filter(devs) == [devs[0], devs[3]]

    # -- Filter by description regex
    filt = SerialDeviceFilter().set_product_regex("no-such-device")
    assert filt.summary() == '[REGEX="no-such-device"]'
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().set_product_regex("^product2$")
    assert filt.summary() == '[REGEX="^product2$"]'
    assert filt.filter(devs) == [devs[2]]

    filt = SerialDeviceFilter().set_product_regex("product2")
    assert filt.summary() == '[REGEX="product2"]'
    assert filt.filter(devs) == [devs[2]]

    filt = SerialDeviceFilter().set_product_regex("(product3)|(product2)")
    assert filt.summary() == '[REGEX="(product3)|(product2)"]'
    assert filt.filter(devs) == [devs[2], devs[3]]

    # -- Filter by serial number
    filt = SerialDeviceFilter().set_serial_num("no-such-device")
    assert filt.summary() == '[S/N="no-such-device"]'
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().set_serial_num("serial2")
    assert filt.summary() == '[S/N="serial2"]'
    assert filt.filter(devs) == [devs[2]]

    # -- Filter by port and port name
    filt = SerialDeviceFilter().set_port("no-such-port")
    assert filt.summary() == "[PORT=no-such-port]"
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().set_port("port2")
    assert filt.summary() == "[PORT=port2]"
    assert filt.filter(devs) == [devs[2]]

    filt = SerialDeviceFilter().set_port("name2")
    assert filt.summary() == "[PORT=name2]"
    assert filt.filter(devs) == [devs[2]]

    # -- Filter by VID, PID
    filt = (
        SerialDeviceFilter()
        .set_vendor_id("0405")
        .set_product_id("6020")
        .set_port("port3")
    )
    assert filt.summary() == "[VID=0405, PID=6020, PORT=port3]"
    assert filt.filter(devs) == [devs[3]]

    filt = (
        SerialDeviceFilter()
        .set_vendor_id("0405")
        .set_product_id("6020")
        .set_port("name3")
    )
    assert filt.summary() == "[VID=0405, PID=6020, PORT=name3]"
    assert filt.filter(devs) == [devs[3]]
