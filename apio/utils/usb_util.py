"""USB devices related utilities."""

import sys
import re
from glob import glob
from typing import List, Optional
from dataclasses import dataclass
import usb.core
import usb.backend.libusb1
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO
from apio.utils import util
from apio.apio_context import ApioContext


# -- Mapping of (VID), and (VID:PID) to device type. This is presented to the
# -- user as an information only. Add more as you like.

_USB_TYPES = {
    # -- FTDI
    (0x0403): "FTDI",
    (0x0403, 0x6001): "FT232R",
    (0x0403, 0x6010): "FT2232H",
    (0x0403, 0x6011): "FT4232H",
    (0x0403, 0x6014): "FT232H",
    (0x0403, 0x6017): "FT313H",
    (0x0403, 0x8372): "FT245R",
    (0x0403, 0x8371): "FT232BM",
    (0x0403, 0x8373): "FT2232C",
    (0x0403, 0x8374): "FT4232",
}


def get_device_type(vid: int, pid: int) -> str:
    """Determine device type string. Try to match by (vid, pid) and if
    not found, by (vid). Returns "" if not found."""
    device_type = _USB_TYPES.get((vid, pid), "")
    if not device_type:
        device_type = _USB_TYPES.get((vid), "")
    return device_type


def check_usb_id_format(usb_id: str) -> None:
    """Check that a vid or pid is in 4 char uppercase hex."""
    if not re.search(r"^[0-9A-F]{4}$", usb_id):
        raise ValueError(f"Invalid 04X hex value: [{usb_id}]")


@dataclass()
class UsbDevice:
    """A data class to hold the information of a single USB device."""

    # pylint: disable=too-many-instance-attributes

    vendor_id: str
    product_id: str
    bus: int
    device: int
    manufacturer: str
    product: str
    serial_number: str
    device_type: str

    def __post_init__(self):
        """Check that vid, pid, has the format %04X."""
        check_usb_id_format(self.vendor_id)
        check_usb_id_format(self.product_id)

    def summary(self) -> str:
        """Returns a user friendly short description of this device."""
        return (
            f"[{self.vendor_id}:{self.product_id}] "
            f"[{self.bus}:{self.device}] "
            f"[{self.manufacturer}] "
            f"[{self.product}] [{self.serial_number}]"
        )


def _get_usb_str(
    device: usb.core.Device, index: int, default: str
) -> Optional[str]:
    """Extract usb string by its index."""
    # pylint: disable=broad-exception-caught
    try:
        s = usb.util.get_string(device, index)
        # For Tang 9K which contains a null char as a string separator.
        # It's not USB standard but C tools do that implicitly.
        s = s.split("\x00", 1)[0]
        return s
    except Exception as e:
        if util.is_debug(1):
            cout(f"Error getting USB string at index {index}: {e}")
        return default


def scan_usb_devices(apio_ctx: ApioContext) -> List[UsbDevice]:
    """Query and return a list with usb device info."""

    # -- Track the names we searched for. For diagnostics.
    searched_names = []

    def find_library(name: str):
        """A callback for looking up the libusb backend file."""

        # -- Track searched names, for diagnostics
        searched_names.append(name)

        # -- Try to match to a lib in oss-cad-suite/lib.
        oss_dir = apio_ctx.get_package_dir("oss-cad-suite")
        pattern = oss_dir / "lib" / f"lib{name}*"
        files = glob(str(pattern))

        if util.is_debug(1):
            cout("Apio find_library() call:")
            cout(f"   {name=}")
            cout(f"   {pattern=}")
            cout(f"   {files=}")

        # -- We don't expect multiple matches.
        if len(files) > 1:
            cerror(f"Found multiple backends for '{name}': {files}")
            sys.exit(1)

        if files:
            return files[0]
        return None

    # -- Lookup libusb backend library file in oss-cad-suite/lib.
    backend = usb.backend.libusb1.get_backend(find_library=find_library)

    if not backend:
        cerror("Libusb backend not found")
        cout(f"Searched names: {searched_names}", style=INFO)
        sys.exit(1)

    # -- Find the usb devices.
    devices: List[usb.core.Device] = usb.core.find(
        find_all=True, backend=backend
    )

    # -- Collect the devices
    result: List[UsbDevice] = []
    for device in devices:
        # -- Print entire raw device info for debugging.
        if util.is_debug(1):
            cout()
            cout(str(device))
            cout()

        # -- Sanity check.
        assert isinstance(device, usb.core.Device), type(device)

        # -- Skip hubs, they are not interesting.
        if device.bDeviceClass == 0x09:
            continue

        # -- Lookup device type or "" if not found.
        device_type = get_device_type(device.idVendor, device.idProduct)

        # -- Create the device object.
        unavail = "--unavail--"
        item = UsbDevice(
            vendor_id=f"{device.idVendor:04X}",
            product_id=f"{device.idProduct:04X}",
            bus=device.bus,
            device=device.address,
            manufacturer=_get_usb_str(
                device,
                device.iManufacturer,
                default=unavail,
            ),
            product=_get_usb_str(device, device.iProduct, default=unavail),
            serial_number=_get_usb_str(
                device, device.iSerialNumber, default=""
            ),
            device_type=device_type,
        )
        result.append(item)

    # -- Sort by (vendor, product, bus, device).
    result = sorted(
        result,
        key=lambda d: (
            d.vendor_id.lower(),
            d.product_id.lower(),
            d.bus,
            d.device,
        ),
    )

    if util.is_debug(1):
        cout(f"Found {len(result)} USB devices:")
        for device in result:
            cout(str(device))

    # -- All done.
    return result


@dataclass
class UsbDeviceFilter:
    """A class to filter a list of usb devices by attributes. We use the
    Fluent Interface design pattern so we can assert that the values that
    the caller passes as filters are not unintentionally None or empty
    unintentionally."""

    _vendor_id: str = None
    _product_id: str = None
    product_regex: str = None
    _serial_num: str = None

    def summary(self) -> str:
        """User friendly representation of the filter"""
        terms = []

        if self._vendor_id:
            terms.append(f"VID={self._vendor_id}")
        if self._product_id:
            terms.append(f"PID={self._product_id}")
        if self.product_regex:
            terms.append(f'REGEX="{self.product_regex}"')
        if self._serial_num:
            terms.append(f'S/N="{self._serial_num}"')
        if terms:
            return "[" + ", ".join(terms) + "]"
        return "[all]"

    def set_vendor_id(self, vendor_id: str) -> "UsbDeviceFilter":
        """Pass only devices with given vendor id."""
        check_usb_id_format(vendor_id)
        self._vendor_id = vendor_id
        return self

    def set_product_id(self, product_id: str) -> "UsbDeviceFilter":
        """Pass only devices with given product id."""
        check_usb_id_format(product_id)
        self._product_id = product_id
        return self

    def set_product_regex(self, product_regex: str) -> "UsbDeviceFilter":
        """Pass only devices whose product string match given regex."""
        assert product_regex
        self.product_regex = product_regex
        return self

    def set_serial_num(self, serial_num: str) -> "UsbDeviceFilter":
        """Pass only devices given product serial number.."""
        assert serial_num
        self._serial_num = serial_num
        return self

    def _eval(self, device: UsbDevice) -> bool:
        """Test if the devices passes this field."""
        if (self._vendor_id is not None) and (
            self._vendor_id != device.vendor_id
        ):
            return False

        if (self._product_id is not None) and (
            self._product_id != device.product_id
        ):
            return False

        if (self.product_regex is not None) and not re.search(
            self.product_regex, device.product
        ):
            return False

        if (self._serial_num is not None) and (
            self._serial_num.lower() != device.serial_number.lower()
        ):
            return False

        return True

    def filter(self, devices: List[UsbDevice]):
        """Return a copy of the list with items that are pass this filter.
        Items order is preserved."""
        result = [d for d in devices if self._eval(d)]
        return result
