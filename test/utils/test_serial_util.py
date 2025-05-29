"""
Tests of serial_util.py
"""

from typing import List
from apio.utils.serial_util import (
    SerialDevice,
    SerialDeviceFilter,
)


def test_filter_serial_devices():
    """Test the filtering function."""
    devs: List[SerialDevice] = [
        SerialDevice(  # devs[0]
            "port0",
            "name0",
            "manuf0",
            "product0",
            "0403",
            "6020",
            "serial0",
            "type0",
            "location0",
        ),
        SerialDevice(  # devs[1]
            "port1",
            "name1",
            "manuf1",
            "product1",
            "0405",
            "6010",
            "serial1",
            "type1",
            "location1",
        ),
        SerialDevice(  # devs[2]
            "port2",
            "name2",
            "manuf2",
            "product2",
            "0403",
            "6010",
            "serial2",
            "type2",
            "location2",
        ),
        SerialDevice(  # devs[3]
            "port3",
            "name3",
            "manuf3",
            "product3",
            "0405",
            "6020",
            "serial3",
            "type3",
            "location3",
        ),
    ]

    # -- All filtering disabled.
    serial_filter = SerialDeviceFilter()
    assert serial_filter.summary() == "[all]"
    assert serial_filter.filter(devs) == devs

    # -- Filter by VID
    serial_filter = SerialDeviceFilter().vendor_id("9999")
    assert serial_filter.summary() == "[VID=9999]"
    assert serial_filter.filter(devs) == []

    serial_filter = SerialDeviceFilter().vendor_id("0405")
    assert serial_filter.summary() == "[VID=0405]"
    assert serial_filter.filter(devs) == [devs[1], devs[3]]

    # -- Filter by PID
    serial_filter = SerialDeviceFilter().product_id("9999")
    assert serial_filter.summary() == "[PID=9999]"
    assert serial_filter.filter(devs) == []

    serial_filter = SerialDeviceFilter().product_id("6020")
    assert serial_filter.summary() == "[PID=6020]"
    assert serial_filter.filter(devs) == [devs[0], devs[3]]

    # -- Filter by port and port name

    serial_filter = SerialDeviceFilter().port("no-such-port")
    assert serial_filter.summary() == "[port=no-such-port]"
    assert serial_filter.filter(devs) == []

    serial_filter = SerialDeviceFilter().port("port2")
    assert serial_filter.summary() == "[port=port2]"
    assert serial_filter.filter(devs) == [devs[2]]

    serial_filter = SerialDeviceFilter().port("name2")
    assert serial_filter.summary() == "[port=name2]"
    assert serial_filter.filter(devs) == [devs[2]]

    # -- Filter by VID, PID
    serial_filter = (
        SerialDeviceFilter().vendor_id("0405").product_id("6020").port("port3")
    )
    assert serial_filter.summary() == "[VID=0405, PID=6020, port=port3]"
    assert serial_filter.filter(devs) == [devs[3]]

    serial_filter = (
        SerialDeviceFilter().vendor_id("0405").product_id("6020").port("name3")
    )
    assert serial_filter.summary() == "[VID=0405, PID=6020, port=name3]"
    assert serial_filter.filter(devs) == [devs[3]]
