"""Serial devices related utilities."""

from typing import List
from dataclasses import dataclass
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from apio.common.apio_console import cout, configure


@dataclass()
class SerialDeviceInfo:
    """A data class to hold the information of a single Serial device."""

    # pylint: disable=too-many-instance-attributes

    port: str
    port_name: str
    manufacturer: str
    description: str
    vendor_id: str
    product_id: str
    serial_number: str
    location: str

    def dump(self):
        """Dump the device info. For debugging."""
        cout(f"    port:          [{self.port}]")
        cout(f"    port-name:     [{self.port_name}]")
        cout(f"    manufacturer:  [{self.manufacturer}]")
        cout(f"    description:   [{self.description}]")
        cout(f"    vendor_id:     [{self.vendor_id}]")
        cout(f"    product_id:    [{self.product_id}]")
        cout(f"    serial_number: [{self.serial_number}]")
        cout(f"    location:      [{self.location}]")


def scan_serial_devices() -> List[SerialDeviceInfo]:
    """Scan the connected serial devices and return their information."""

    # TODO: Figure out the data and update the comments.
    #
    # """Get a list of the serial port devices connected
    # * OUTPUT: A list with the devides
    #      Ex: [{'port': '/dev/ttyACM0',
    #            'description': 'ttyACM0',
    #            'hwid': 'USB VID:PID=1D50:6130 LOCATION=1-5:1.0'}]
    # """

    # -- Initial empty device list
    devices = []

    # -- Use the serial.tools.list_ports module for reading the
    # -- serial ports
    # -- More info:
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
            SerialDeviceInfo(
                port=item.device,
                port_name=item.name,
                manufacturer=item.manufacturer,
                description=item.description,
                vendor_id=f"{item.vid:04X}",
                product_id=f"{item.pid:04X}",
                serial_number=item.serial_number or "",
                location=item.location,
            )
        )

    # -- All done.
    return devices


# TODO: Add a filter class, similar to usb_util.py.

# -- For testing with actual boards.
if __name__ == "__main__":
    configure()
    devices_ = scan_serial_devices()
    for index, device_ in enumerate(devices_):
        cout()
        print(f"[{index}]")
        device_.dump()
        cout()
