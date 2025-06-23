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
    vendor_id: str
    product_id: str
    manufacturer: str
    product: str
    serial_number: str
    device_type: str
    location: str

    def __post_init__(self):
        """Check that vid, pid, has the format %04X."""
        usb_util.check_usb_id_format(self.vendor_id)
        usb_util.check_usb_id_format(self.product_id)

    def summary(self) -> str:
        """Returns a user friendly short description of this device."""
        return (
            f"[{self.port}] "
            f"[{self.vendor_id}:{self.product_id}] "
            f"[{self.manufacturer}] [{self.product}] "
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
    for port in list_port_info:

        # -- Dump for debugging.
        if util.is_debug(1):
            cout("Raw serial port:")
            cout(f"    Device: {port.device}")
            cout(f"    Hwid: {port.hwid}")
            cout(f"    Interface: {port.interface}")

        # # -- Skip if not a serial port.
        if not port.device:
            continue

        # -- Skip if not a USB device.
        if not port.vid or not port.pid:
            continue

        # -- Add device to list.
        devices.append(
            SerialDevice(
                port=port.device,
                port_name=port.name,
                vendor_id=f"{port.vid:04X}",
                product_id=f"{port.pid:04X}",
                manufacturer=port.manufacturer,
                product=port.product,
                serial_number=port.serial_number or "",
                device_type=usb_util.get_device_type(port.vid, port.pid),
                location=port.location,
            )
        )

    # -- Sort by port name, case insensitive.
    devices = sorted(devices, key=lambda d: d.port.lower())

    if util.is_debug(1):
        cout(f"Found {len(devices)} serial device:")
        for device in devices:
            cout(str(device))

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
    _product_regex: str = None
    _serial_port: str = None
    _serial_num: str = None

    def summary(self) -> str:
        """User friendly representation of the filter"""
        terms = []
        if self._vendor_id:
            terms.append(f"VID={self._vendor_id}")
        if self._product_id:
            terms.append(f"PID={self._product_id}")
        if self._product_regex:
            terms.append(f'REGEX="{self._product_regex}"')
        if self._serial_port:
            terms.append(f"PORT={self._serial_port}")
        if self._serial_num:
            terms.append(f'S/N="{self._serial_num}"')
        if terms:
            return "[" + ", ".join(terms) + "]"
        return "[all]"

    def set_vendor_id(self, vendor_id: str) -> "SerialDeviceFilter":
        """Pass only devices with given vendor id."""
        usb_util.check_usb_id_format(vendor_id)
        self._vendor_id = vendor_id
        return self

    def set_product_id(self, product_id: str) -> "SerialDeviceFilter":
        """Pass only devices given product id."""
        usb_util.check_usb_id_format(product_id)
        self._product_id = product_id
        return self

    def set_product_regex(self, product_regex: str) -> "SerialDeviceFilter":
        """Pass only devices whose product string match given regex."""
        assert product_regex
        self._product_regex = product_regex
        return self

    def set_port(self, serial_port: str) -> "SerialDeviceFilter":
        """Pass only devices given product serial port.."""
        assert serial_port
        self._serial_port = serial_port
        return self

    def set_serial_num(self, serial_num: str) -> "SerialDeviceFilter":
        """Pass only devices given product serial number.."""
        assert serial_num
        self._serial_num = serial_num
        return self

    def _eval(self, device: SerialDevice) -> bool:
        """Test if the devices passes this field."""
        if (self._vendor_id is not None) and (
            self._vendor_id != device.vendor_id
        ):
            return False

        if (self._product_id is not None) and (
            self._product_id != device.product_id
        ):
            return False

        if (self._product_regex is not None) and not re.search(
            self._product_regex, device.product
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

        if (self._serial_num is not None) and (
            self._serial_num.lower() != device.serial_number.lower()
        ):
            return False

        return True

    def filter(self, devices: List[SerialDevice]):
        """Return a copy of the list with items that are pass this filter.
        Items order is preserved."""
        result = [d for d in devices if self._eval(d)]
        return result
