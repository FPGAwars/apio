"""FTDI devices related utilities."""

import re
import sys
import subprocess
from typing import List, Tuple
from dataclasses import dataclass
from apio.common.apio_console import cout, cerror, configure
from apio.common.apio_styles import INFO
from apio.utils import snap_util


# -- A regex to parse the header field titles. Each field title includes
# -- Trailing spaces so we can derive it's width.
HEADER_REGEX = re.compile(
    r"^(Bus *)(device *)(vid:pid *)(probe_type *)(manufacturer *)"
    r"(serial *)(product *)$"
)


@dataclass()
class FtdiDeviceInfo:
    """A data class to hold the information of a single FTDI device."""

    # pylint: disable=too-many-instance-attributes

    # -- The fields in the order they appear in the 'openFPGAList --scan-usb'
    # -- output which is different from the order in which we print them.
    bus: int
    device: int
    vendor_id: str
    product_id: str
    type: str
    manufacturer: str
    serial_number: str
    description: str

    def dump(self):
        """Dump the device info. For debugging."""
        cout(f"    bus:           [{self.bus}]")
        cout(f"    dev:           [{self.device}]")
        cout(f"    vid:           [{self.vendor_id}]")
        cout(f"    pid:           [{self.product_id}]")
        cout(f"    type:          [{self.type}]")
        cout(f"    manufacturer:  [{self.manufacturer}]")
        cout(f"    serial_number:   [{self.serial_number}]")
        cout(f"    descripition:  [{self.description}]")


def _locate_header_columns_starts(header_line: str) -> List[int]:
    """Given the header line of an 'openFPGALoader --scan-usb' report, returns
    a list with the indexes of the first char of each of teh columns.
    We use this information later to parse the individual device lines."""

    # -- The expected number of fields.
    num_fields = 7
    assert HEADER_REGEX.groups == num_fields

    # -- Match the header line.
    m = HEADER_REGEX.match(header_line)

    # -- Fatal error if doesn't match.
    if not m:
        cerror("Failed to parse the header line of openfpgaloader.")
        cout(f"Header line[{header_line}]", style=INFO)
        sys.exit(1)

    # -- Sanity check. If this fails, it's a programming error.
    assert len(m.groups()) == num_fields

    # -- Collect the start index of all the header fields.
    fields_starts = []
    for i in range(num_fields):
        fields_starts.append(m.start(i + 1))

    # -- All done.
    return fields_starts


def _get_report_lines(text: str) -> Tuple[str, List[str]]:
    """Given the output text of 'openFPGALoader --scan-usb', extract and return
    the header line and a list of the devices lines."""

    # -- Split to lines.
    lines = text.splitlines()

    # -- Remove blank lines.
    lines = [line for line in lines if line.strip()]

    # -- Find the index of the header line. We
    header_line_index = None
    for i, line in enumerate(lines):
        if line.startswith("Bus "):
            header_line_index = i
            break

    # -- Error if header not found.
    if header_line_index is None:
        cerror("Failed to match 'openFPGALoader --scan-usb' report header.")
        sys.exit(1)

    # -- Return the header and devices lines.
    header_line = lines[header_line_index]
    begin = header_line_index + 1
    devices_lines = lines[begin:]
    return (header_line, devices_lines)


def _extract_field(
    device_line: str, field_index: int, fields_starts: List[int]
):
    # -- Extract the value of a field from a device line and cleaned it up.

    # -- Compute the slice to use.
    start = fields_starts[field_index]
    end = (
        fields_starts[field_index + 1]
        if field_index < (len(fields_starts) - 1)
        else None
    )

    # -- Extract the value and clean up.
    value = device_line[slice(start, end)].strip()
    if value == "none":
        value = ""

    # -- All done.
    return value


def _get_devices_from_text(text: str) -> FtdiDeviceInfo:
    """Parse the devices information from an output text of the command
    'openFPGALoader --scan-usb'."""

    # pylint: disable=too-many-locals

    # -- Extract header and device lines.
    header, devices_lines = _get_report_lines(text)

    # -- Find the starts of the header fields. We expect exactly 7 fields,.
    columns_starts = _locate_header_columns_starts(header)
    assert len(columns_starts) == 7, columns_starts

    # -- Iterate the device lines and parse into a list of DeviceInfo.
    devices = []
    for line in devices_lines:

        # -- Pad the line to have at least one char in the last field.
        min_len = columns_starts[-1] + 1
        line = line.ljust(min_len)

        # -- Extract fields
        bus = _extract_field(line, 0, columns_starts)
        dev = _extract_field(line, 1, columns_starts)
        vid_pid = _extract_field(line, 2, columns_starts)
        type_str = _extract_field(line, 3, columns_starts)
        manufacturer = _extract_field(line, 4, columns_starts)
        serial_number = _extract_field(line, 5, columns_starts)
        description = _extract_field(line, 6, columns_starts)

        # -- Split pid_vid to pid and vid
        tokens = vid_pid.split(":")
        assert len(tokens) == 2, tokens
        assert tokens[0].startswith("0x")
        assert tokens[1].startswith("0x")
        vid = tokens[0][2:]
        pid = tokens[1][2:]

        # -- Construct the device info.
        device = FtdiDeviceInfo(
            bus=int(bus),
            device=int(dev),
            vendor_id=vid,
            product_id=pid,
            type=type_str,
            manufacturer=manufacturer,
            serial_number=serial_number,
            description=description,
        )
        devices.append(device)

    # -- All done.
    return devices


def scan_ftdi_devices() -> List[FtdiDeviceInfo]:
    """Run 'openFPGALoader --scan-usb' and return its results as a list of
    device info objects. This functions requires the apio shell vars to be
    set such that openFPGALoader is on the path."""

    # -- Run the command 'openFPGALoader --scan-usb'.
    result = subprocess.run(
        ["openFPGALoader", "--scan-usb"],
        capture_output=True,
        text=True,
        check=False,
    )

    # -- Exit if the command failed.
    if result.returncode != 0:
        cerror(
            "The command 'openFPGALoader --scan-usb' failed with "
            f"error code {result.returncode}"
        )
        cout(
            "[Hint]: Some platforms require ftdi driver installation "
            "using 'apio drivers install ftdi'.",
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
class FtdiDeviceFilter:
    """A class to filter a list of ftdi devices by attributes. We use the
    Fluent Interface design pattern so we can assert that the values that
    the caller passes as filters are not unintentionally None or empty
    unintentionally."""

    _vendor_id: str = None
    _product_id: str = None
    _serial_code: str = None
    _description_regex: str = None

    def vendor_id(self, vendor_id: str) -> "FtdiDeviceFilter":
        """Pass only devices with given vendor id."""
        assert vendor_id
        self._vendor_id = vendor_id
        return self

    def product_id(self, product_id: str) -> "FtdiDeviceFilter":
        """Pass only devices given product id."""
        assert product_id
        self._product_id = product_id
        return self

    def serial_number(self, serial_number: str) -> "FtdiDeviceFilter":
        """Pass only devices given serial code."""
        assert serial_number
        self._serial_code = serial_number
        return self

    def description_regex(self, description_regex: str) -> "FtdiDeviceFilter":
        """Pass only devices where this regex matches their head.e"""
        assert description_regex
        self._description_regex = description_regex
        return self

    def _eval(self, device: FtdiDeviceInfo) -> bool:
        """Test if the devices passes this field."""
        if (self._vendor_id is not None) and (
            self._vendor_id != device.vendor_id
        ):
            return False

        if (self._product_id is not None) and (
            self._product_id != device.product_id
        ):
            return False

        if (self._serial_code is not None) and (
            self._serial_code != device.serial_number
        ):
            return False

        if (self._description_regex is not None) and not (
            re.search(self._description_regex, device.description)
        ):
            return False

        return True

    def filter(self, devices: List[FtdiDeviceInfo]):
        """Return a copy of the list with items that are pass this filter.
        Items order is preserved."""
        result = [d for d in devices if self._eval(d)]
        return result


# -- For testing with actual boards.
# -- Make sure 'openFPGALoader' is on the path.
if __name__ == "__main__":
    configure()
    devices_ = scan_ftdi_devices()
    for device_ in devices_:
        cout()
        device_.dump()
        cout()
