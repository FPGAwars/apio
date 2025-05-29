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
            "location3",
        ),
    ]

    # -- All filtering disabled.
    filt = SerialDeviceFilter()
    assert str(filt) == "[all]"
    assert filt.filter(devs) == devs

    # -- Filter by VID
    filt = SerialDeviceFilter().vendor_id("9999")
    assert str(filt) == "[VID=9999]"
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().vendor_id("0405")
    assert str(filt) == "[VID=0405]"
    assert filt.filter(devs) == [devs[1], devs[3]]

    # -- Filter by PID
    filt = SerialDeviceFilter().product_id("9999")
    assert str(filt) == "[PID=9999]"
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().product_id("6020")
    assert str(filt) == "[PID=6020]"
    assert filt.filter(devs) == [devs[0], devs[3]]

    # -- Filter by port and port name

    filt = SerialDeviceFilter().port("no-such-port")
    assert str(filt) == "[port=no-such-port]"
    assert filt.filter(devs) == []

    filt = SerialDeviceFilter().port("port2")
    assert str(filt) == "[port=port2]"
    assert filt.filter(devs) == [devs[2]]

    filt = SerialDeviceFilter().port("name2")
    assert str(filt) == "[port=name2]"
    assert filt.filter(devs) == [devs[2]]

    # -- Filter by VID, PID
    filt = (
        SerialDeviceFilter().vendor_id("0405").product_id("6020").port("port3")
    )
    assert str(filt) == "[VID=0405, PID=6020, port=port3]"
    assert filt.filter(devs) == [devs[3]]

    filt = (
        SerialDeviceFilter().vendor_id("0405").product_id("6020").port("name3")
    )
    assert str(filt) == "[VID=0405, PID=6020, port=name3]"
    assert filt.filter(devs) == [devs[3]]
