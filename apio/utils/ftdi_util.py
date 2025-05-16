"""FTDI device related utilities."""

import re
import sys
import subprocess
from typing import List, Tuple
from dataclasses import dataclass
from apio.common.apio_console import cout, cerror
from apio.common.apio_styles import INFO
from apio.utils import snap_util


# -- A regex to parse the header field titles. Each field title includes
# -- Trailing spaces so we can derive it's width.
# -- Using 'probe[ _]type' instead of 'probe type' to handle also the
# -- recent change of openFPGALoader to probe_type.
HEADER_REGEX = re.compile(
    r"^(Bus *)(device *)(vid:pid *)(probe[ _]type *)(manufacturer *)"
    r"(serial *)(product *)$"
)


@dataclass()
class FtdiDeviceInfo:
    """A data class to hold the information of a single FTDI device."""

    # pylint: disable=too-many-instance-attributes

    # -- The fields in the order they appear in the 'openFPGAList --scan-usb'
    # -- output which is different from the order in which we print them.
    index: int
    bus: int
    device: int
    vendor_id: str
    product_id: str
    type: str
    manufacturer: str
    serial_code: str
    description: str

    def dump(self):
        """Dump the device info. For debugging."""
        print(f"Device             [{self.index}]")
        print(f"    bus:           [{self.bus}]")
        print(f"    dev:           [{self.device}]")
        print(f"    vid:           [{self.vendor_id}]")
        print(f"    pid:           [{self.product_id}]")
        print(f"    type:          [{self.type}]")
        print(f"    manufacturer:  [{self.manufacturer}]")
        print(f"    serial_code:   [{self.serial_code}]")
        print(f"    descripition:  [{self.description}]")


def _locate_header_fields_starts(header_line: str) -> List[int]:
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
    assert m.lastindex == num_fields

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


def _patch_device_field_end(
    device_line: str, field_index: int, field_starts: List[int]
) -> List[int]:
    """Given a device line from a 'openFPGALoader --scan-usb' report, a field
    index of the list of fields starts, possibly extend the given field length
    if it seems that it's longer expected.

    This is a partial workaround for the issue desctibed at
    https://github.com/trabucayre/openFPGALoader/issues/549 that doesn't
    address all the possible edge cases."""

    # -- No point for calling the last field since its has no end.
    assert field_index < (len(field_starts) - 1)

    # -- Make a copy of the starts list so we can mutate it without
    # -- affecting the caller's data.
    result = field_starts.copy()

    # -- Extend the field by one char until it ends with " " or we reached
    # -- the end of the string. When we extend the field by moving by one
    # -- the starts of all the fields that follow it.
    while True:
        # -- Field end index is the start of the next field.
        end = result[field_index + 1]
        if end >= len(device_line):
            break
        if device_line[end - 1] == " ":
            break
        # -- Increment by one the starts of all following fields.
        for i in range(field_index + 1, len(field_starts)):
            result[i] += 1

    # -- All done. Return the possibly modified starts list.
    return result


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
    header_starts = _locate_header_fields_starts(header)
    assert len(header_starts) == 7, header_starts

    # -- Iterate the device lines and parse into a list of DeviceInfo.
    devices = []
    for index, line in enumerate(devices_lines):

        # -- Adjust the starts for fields 4, 5, which may exceed the their
        # -- header widths.
        line_starts = _patch_device_field_end(line, 4, header_starts)
        line_starts = _patch_device_field_end(line, 5, line_starts)

        # -- Pad the line to have at least one char in the last field.
        min_len = line_starts[-1] + 1
        line = line.ljust(min_len)

        # -- Extract fields
        bus = _extract_field(line, 0, line_starts)
        dev = _extract_field(line, 1, line_starts)
        vid_pid = _extract_field(line, 2, line_starts)
        type_str = _extract_field(line, 3, line_starts)
        manufacturer = _extract_field(line, 4, line_starts)
        serial_code = _extract_field(line, 5, line_starts)
        description = _extract_field(line, 6, line_starts)

        # -- Split pid_vid to pid and vid
        tokens = vid_pid.split(":")
        assert len(tokens) == 2, tokens
        assert tokens[0].startswith("0x")
        assert tokens[1].startswith("0x")
        vid = tokens[0][2:]
        pid = tokens[1][2:]

        # -- Construct the device info.
        device = FtdiDeviceInfo(
            index=index,
            bus=int(bus),
            device=int(dev),
            vendor_id=vid,
            product_id=pid,
            type=type_str,
            manufacturer=manufacturer,
            serial_code=serial_code,
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


# -- For testing with actual boards.
# -- Make sure 'openFPGALoader is on the path.
if __name__ == "__main__":
    devices_ = scan_ftdi_devices()
    for device_ in devices_:
        print()
        device_.dump()
        print()
