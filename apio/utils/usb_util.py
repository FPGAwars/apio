"""USB devices related utilities."""

import sys
from glob import glob
from typing import List, Optional
from dataclasses import dataclass
import usb.core
import usb.backend.libusb1
from apio.common.apio_console import cout, cerror, configure
from apio.common.apio_styles import INFO
from apio.utils import util
from apio.apio_context import ApioContext, ApioContextScope


# Mapping of (VID), and (VID:PID) to device type.
USB_TYPES = {
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


@dataclass()
class UsbDevice:
    """A data class to hold the information of a single USB device."""

    # pylint: disable=too-many-instance-attributes

    bus: int
    device: int
    vendor_id: str
    product_id: str
    manufacturer: str
    description: str
    serial_num: str
    device_type: str


def get_usb_str(
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
        if util.is_debug():
            print(f"Error getting USB string at index {index}: {e}")
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

        if util.is_debug():
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
        # -- Print entire device info for debugging.
        if util.is_debug():
            cout()
            cout(str(device))
            cout()

        # -- Sanity check.
        assert isinstance(device, usb.core.Device), type(device)

        # -- Skip hubs, they are not interesting.
        if device.bDeviceClass == 0x09:
            continue

        # -- Determine device type string. Try to match by (vid, pid) and if
        # -- not found, by (vid)
        device_type = USB_TYPES.get((device.idVendor, device.idProduct), "")
        if not device_type:
            device_type = USB_TYPES.get((device.idVendor), "")

        # -- Create the device object.
        unavail = "--unavail--"
        item = UsbDevice(
            bus=device.bus,
            device=device.address,
            vendor_id=device.idVendor,
            product_id=device.idProduct,
            manufacturer=get_usb_str(
                device,
                device.iManufacturer,
                default=unavail,
            ),
            description=get_usb_str(device, device.iProduct, default=unavail),
            serial_num=get_usb_str(device, device.iSerialNumber, default=""),
            device_type=device_type,
        )
        result.append(item)

    # -- Sort by (vendor, product, bus, device).
    result = sorted(
        result, key=lambda d: (d.vendor_id, d.device_type, d.bus, d.device)
    )

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

        return True

    def filter(self, devices: List[UsbDevice]):
        """Return a copy of the list with items that are pass this filter.
        Items order is preserved."""
        result = [d for d in devices if self._eval(d)]
        return result


# -- For testing with actual boards.
if __name__ == "__main__":
    configure()
    apio_ctx_ = ApioContext(scope=ApioContextScope.NO_PROJECT)
    devices_ = scan_usb_devices(apio_ctx=apio_ctx_)
    for device_ in devices_:
        cout()
        cout(str(device_))
