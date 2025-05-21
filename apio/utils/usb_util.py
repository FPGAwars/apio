"""USB devices related utilities."""

import re
import sys
import subprocess
from typing import List
from dataclasses import dataclass
from apio.common.apio_console import cout, cerror, configure
from apio.common.apio_styles import INFO
from apio.utils import snap_util

# -- A regex to parse a device line of 'lsusb'.
# -- See sample lines at test_usb_util.py.
DEVICE_REGEX = re.compile(
    r"^"
    r"([a-fA-F0-9]{4}):"
    r"([a-fA-F0-9]{4})[ ]+"
    r"[(]bus ([0-9]+),"
    r"[ ]+device ([0-9]+)[)]"
    r"(?:[ ]+path: ([0-9.]+)[ ]*)?"
    r"$"
)


@dataclass()
class UsbDeviceInfo:
    """A data class to hold the information of a single USB device."""

    bus: int
    device: int
    vendor_id: str
    product_id: str
    path: str

    def dump(self):
        """Dump the device info. For debugging."""
        cout(f"    bus:   [{self.bus}]")
        cout(f"    dev:   [{self.device}]")
        cout(f"    vid:   [{self.vendor_id}]")
        cout(f"    pid:   [{self.product_id}]")
        cout(f"    path:  [{self.path}]")


def _get_devices_from_text(text: str) -> List[UsbDeviceInfo]:
    """Parse the devices information from an output text of the command
    'lsusb'."""

    # -- Split to lines.
    lines = text.splitlines()

    # -- Iterate the device lines and parse into a list of DeviceInfo.
    devices = []
    for line in lines:

        # -- Skip is not a device line.
        if "bus" not in line or "device" not in line:
            continue

        # -- Match the line.
        m = DEVICE_REGEX.search(line)

        # -- If this fails, this is a programming error. We want to know
        # -- about it.
        assert m, f"Failed to parse usb device line [{line}]"

        # -- Sanity checks of the number of expected fields.
        assert DEVICE_REGEX.groups == 5
        assert len(m.groups()) == 5

        # -- Create the device object. and append to the list.
        device = UsbDeviceInfo(
            bus=int(m.group(3)),
            device=int(m.group(4)),
            vendor_id=m.group(1).upper(),
            product_id=m.group(2).upper(),
            path=m.group(5) or "",
        )

        devices.append(device)

    # -- All done.
    return devices


def scan_usb_devices() -> List[UsbDeviceInfo]:
    """Run 'lsusb' and return its results as a list of
    device info objects. This functions requires the apio shell vars to be
    set such that lsusb is on the path."""

    # -- Run the command 'lsusb'.
    result = subprocess.run(
        ["lsusb"],
        capture_output=True,
        text=True,
        check=False,
    )

    # -- Exit if the command failed.
    if result.returncode != 0:
        cerror(
            "The command 'lsusb' failed with "
            f"error code {result.returncode}"
        )
        cout(
            "[Hint]: Some platforms require driver installation "
            "using 'apio drivers install'.",
            style=INFO,
        )
        if snap_util.is_snap():
            cout(
                "[Hint]: Snap applications may require "
                "'snap connect apio:raw-usb' to access USB devices.",
                style=INFO,
            )
        sys.exit(1)

    # -- Parse the output text into a list of devices and return.
    devices = _get_devices_from_text(result.stdout)

    # -- All done.
    return devices


@dataclass
class UsbDeviceFilter:
    """A class to filter a list of usb devices by attributes. We use the
    Fluent Interface design pattern so we can assert that the values that
    the caller passes as filters are not unintentionally None or empty
    unintentionally."""

    _vendor_id: str = None
    _product_id: str = None

    def vendor_id(self, vendor_id: str) -> "UsbDeviceFilter":
        """Pass only devices with given vendor id."""
        assert vendor_id
        self._vendor_id = vendor_id
        return self

    def product_id(self, product_id: str) -> "UsbDeviceFilter":
        """Pass only devices given product id."""
        assert product_id
        self._product_id = product_id
        return self

    def _eval(self, device: UsbDeviceInfo) -> bool:
        """Test if the devices passes this field."""
        if (self._vendor_id is not None) and (
            self._vendor_id != device.vendor_id
        ):
            return False

        if (self._product_id is not None) and (
            self._product_id != device.product_id
        ):
            return False

        return True

    def filter(self, devices: List[UsbDeviceInfo]):
        """Return a copy of the list with items that are pass this filter.
        Items order is preserved."""
        result = [d for d in devices if self._eval(d)]
        return result


# -- For testing with actual boards.
# -- Make sure 'lsusb' is on the path.
if __name__ == "__main__":
    configure()
    devices_ = scan_usb_devices()
    for device_ in devices_:
        cout()
        device_.dump()
        cout()
