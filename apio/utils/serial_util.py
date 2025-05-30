"""Serial devices related utilities."""

import re
from typing import List
from dataclasses import dataclass
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from apio.common.apio_console import cout
from apio.utils import util, usb_util


@dataclass()
class SerialDevice:
    """A data class to hold the information of a single Serial device."""

    # pylint: disable=too-many-instance-attributes

    port: str
    port_name: str
    manufacturer: str
    description: str
    vendor_id: str
    product_id: str
    serial_number: str
    device_type: str
    location: str

    def dump(self) -> None:
        """Dump the device info. For debugging."""
        cout(f"    port:          [{self.port}]")
        cout(f"    port-name:     [{self.port_name}]")
        cout(f"    manufacturer:  [{self.manufacturer}]")
        cout(f"    description:   [{self.description}]")
        cout(f"    vendor_id:     [{self.vendor_id}]")
        cout(f"    product_id:    [{self.product_id}]")
        cout(f"    serial_number: [{self.serial_number}]")
        cout(f"    device_type  : [{self.device_type}]")
        cout(f"    location:      [{self.location}]")

    def summary(self) -> str:
        """Returns a user friendly short description of this device."""
        return (
            f"[{self.port}] "
            f"[{self.vendor_id}:{self.product_id}, "
            f"[{self.manufacturer}] [{self.description}] "
            f"[{self.serial_number}]"
        )


def scan_serial_devices() -> List[SerialDevice]:
    """Scan the connected serial devices and return their information."""

    # -- Initial empty device list
    devices = []

    # -- Use the serial.tools.list_ports module for reading the
    # -- serial ports. More info:
    # --   https://pyserial.readthedocs.io/en/latest/tools.html
    list_port_info: List[ListPortInfo] = comports()
    assert isinstance(list_port_info, list)
    if list_port_info:
        assert isinstance(list_port_info[0], ListPortInfo)

    # -- Collect the items that are USB serial ports.
    for item in list_port_info:

        # # -- Skip if not a serial port.
        if not item.device:
            continue

        # -- Skip if not a USB device.
        if not item.vid or not item.pid:
            continue

        # -- Add device to list.
        devices.append(
            SerialDevice(
                port=item.device,
                port_name=item.name,
                manufacturer=item.manufacturer,
                description=item.description,
                vendor_id=f"{item.vid:04X}",
                product_id=f"{item.pid:04X}",
                serial_number=item.serial_number or "",
                device_type=usb_util.get_device_type(item.vid, item.pid),
                location=item.location,
            )
        )

    # -- Sort by port name, case insensitive.
    devices = sorted(devices, key=lambda d: d.port.lower())

    if util.is_debug():
        cout(f"Found {len(devices)} serial device:")
        for i, device in enumerate(devices):
            cout()
            cout(f"---- serial device {i}")
            device.dump()

    # -- All done.
    return devices


@dataclass
class SerialDeviceFilter:
    """A class to filter a list of serial devices by attributes. We use the
    Fluent Interface design pattern so we can assert that the values that
    the caller passes as filters are not unintentionally None or empty
    unintentionally."""

    _vendor_id: str = None
    _product_id: str = None
    _desc_regex: str = None
    _serial_port: str = None

    def summary(self) -> str:
        """User friendly representation of the filter"""
        terms = []
        if self._vendor_id:
            terms.append(f"VID={self._vendor_id}")
        if self._product_id:
            terms.append(f"PID={self._product_id}")
        if self._desc_regex:
            terms.append(f"regex='{self._desc_regex}'")
        if self._serial_port:
            terms.append(f"port={self._serial_port}")
        if terms:
            return "[" + ", ".join(terms) + "]"
        return "[all]"

    def set_vendor_id(self, vendor_id: str) -> "SerialDeviceFilter":
        """Pass only devices with given vendor id."""
        assert vendor_id
        self._vendor_id = vendor_id
        return self

    def set_product_id(self, product_id: str) -> "SerialDeviceFilter":
        """Pass only devices given product id."""
        assert product_id
        self._product_id = product_id
        return self

    def set_desc_regex(self, desc_regex: str) -> "SerialDeviceFilter":
        """Pass only devices whose description match given regex."""
        assert desc_regex
        self._desc_regex = desc_regex
        return self

    def set_port(self, serial_port: str) -> "SerialDeviceFilter":
        """Pass only devices given product serial port.."""
        assert serial_port
        self._serial_port = serial_port
        return self

    def _eval(self, device: SerialDevice) -> bool:
        """Test if the devices passes this field."""
        if (self._vendor_id is not None) and (
            self._vendor_id.lower() != device.vendor_id.lower()
        ):
            return False

        if (self._product_id is not None) and (
            self._product_id.lower() != device.product_id.lower()
        ):
            return False

        if (self._desc_regex is not None) and not re.search(
            self._desc_regex, device.description
        ):
            return False

        # -- We allow matching by full port string or by port name.
        if (self._serial_port is not None) and (
            (
                self._serial_port.lower()
                not in [device.port.lower(), device.port_name.lower()]
            )
        ):
            return False

        return True

    def filter(self, devices: List[SerialDevice]):
        """Return a copy of the list with items that are pass this filter.
        Items order is preserved."""
        result = [d for d in devices if self._eval(d)]
        return result
