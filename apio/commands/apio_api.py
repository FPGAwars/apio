# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio api' command"""

import sys
import os
import json
from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path

# from glob import glob
import click
from rich.table import Table
from rich import box
import usb.core

# import usb.backend.libusb1
from apio.managers import installer
from apio.commands import options
from apio.common.apio_console import cout, cerror, cprint
from apio.common.apio_styles import INFO, ERROR, BORDER, EMPH3, SUCCESS
from apio.utils import cmd_util, util
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# ------ apio api test

# TODO: Delete this command once the testing is done.


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
    ftdi_type: str


# -- Mapping of FTDI PID to IC model number. Try to keep it consistent with
# -- src/libusb_ll.cpp#L159 at https://github.com/trabucayre/openFPGALoader.
FTDI_PID_TO_MODEL = {
    0x6001: "FT232R",  # Most common UART interface
    0x6010: "FT2232H",  # Dual channel, high-speed
    0x6011: "FT4232H",  # Quad channel, high-speed
    0x6014: "FT232H",  # Single channel, high-speed, multi-protocol
    0x6015: "FTX Series",  # Includes FT231X, FT234X (basic UART)
    0x6017: "FT313H",  # USB host controller IC
    0x8372: "FT245R",  # Parallel FIFO interface
    0x8371: "FT232BM",  # Older UART chip
    0x8373: "FT2232C",  # Early dual interface device
    0x8374: "FT4232",  # Early quad interface device
}


def get_usb_str(device: usb.core.Device, index: int) -> Optional[str]:
    """Extract usb string by its index."""
    # pylint: disable=broad-exception-caught
    try:
        s = usb.util.get_string(device, index)
        # For Tang 9K which contains a null char as a string seperator.
        # It's not USB standard but C tools do that implicitly.
        s = s.split("\x00", 1)[0]
        return s
    #   print(f"{serial_number=}")
    except Exception as e:
        _ = e
        return "(exception)"


def get_usb_devices(apio_ctx: ApioContext) -> List[UsbDevice]:
    """Query and return a list with usb device info."""

    # def find_library(name: str):
    #     """A callback for looking up the libusb backend file."""
    #     oss_dir = apio_ctx.get_package_dir("oss-cad-suite")
    #     pattern = oss_dir / "lib" / f"lib{name}*"
    #     files = glob(str(pattern))
    #     assert len(files) <= 1, files
    #     if files:
    #         return files[0]
    #     return None

    # -- Lookup libusb backend library file in oss-cad-suite/lib.
    # backend = usb.backend.libusb1.get_backend(find_library=find_library)

    # old_val = os.environ["PATH"]
    # items = mutations.paths + [old_val]
    # new_val = os.pathsep.join(items)

    lib_path = str(apio_ctx.get_package_dir("oss-cad-suite") / "lib")
    print(f"{lib_path=}")
    os.environ["DYLD_LIBRARY_PATH"] = lib_path

    # -- Find the usb devices.
    devices: List[usb.core.Device] = usb.core.find(find_all=True)

    # -- Collect the devices
    result: List[UsbDevice] = []
    for device in devices:
        # -- Print entire device info for debugging.
        if util.is_debug():
            print()
            print(device)
            print()

        # -- Sanity check.
        assert isinstance(device, usb.core.Device), type(device)

        # -- Skip hubs. We don't care about them.
        if device.bDeviceClass == 0x09:
            continue

        # -- Determine ftdi type or "".
        if device.idVendor == 0x0403:
            ftdi_type = FTDI_PID_TO_MODEL.get(device.idProduct, "UNKNOWN")
        else:
            ftdi_type = ""

        # -- Create the device object.
        item = UsbDevice(
            bus=device.bus,
            device=device.address,
            vendor_id=device.idVendor,
            product_id=device.idProduct,
            manufacturer=get_usb_str(device, device.iManufacturer),
            description=get_usb_str(device, device.iProduct),
            serial_num=get_usb_str(device, device.iSerialNumber),
            ftdi_type=ftdi_type,
        )
        result.append(item)

    # -- Sort by (bus, device).
    result = sorted(result, key=lambda d: (d.bus, d.device))

    # -- All done.
    return result


# -- Text in the rich-text format of the python rich library.
APIO_API_LAB_HELP = """
The command 'apio api test' is a temporary command that is used \
for cross platform testing by the apio team.
"""


@click.command(
    name="test",
    cls=ApioCommand,
    short_help="Temporary experimental internal testing.",
    help=APIO_API_LAB_HELP,
)
def _test_cli():
    """Implements the 'apio apio test' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Prepare the packages for use.
    installer.install_missing_packages_on_the_fly(apio_ctx)

    # -- Get the list of devices
    devices = get_usb_devices(apio_ctx)

    # -- If not found, print a message and exit.
    if not devices:
        cout("No USB devices found.", style=ERROR)
        return

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="USB Devices",
        title_justify="left",
    )

    # -- Add columns
    table.add_column("BUS", no_wrap=True, justify="center")
    table.add_column("DEV", no_wrap=True, justify="center")
    table.add_column("VID", no_wrap=True)
    table.add_column("PID", no_wrap=True)
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("DESCRIPTION", no_wrap=True, style=EMPH3)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("FTDI-TYPE", no_wrap=True)

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(str(device.bus))
        values.append(str(device.device))
        values.append(f"{device.vendor_id:04X}")
        values.append(f"{device.product_id:04X}")
        values.append(device.manufacturer)
        values.append(device.description)
        values.append(device.serial_num)
        values.append(device.ftdi_type)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)
    cout(f"Found {util.plurality(devices, 'USB device')}", style=SUCCESS)


# ------ apio api info

# -- Text in the rich-text format of the python rich library.
APIO_API_INFO_HELP = """
The command 'apio api info' exports apio information as a JSON document.

The optional flag '--timestamp' allows the caller to embed in the JSON \
document a known timestamp that allows to verify that the JSON document \
was indeed was generated by the same invocation.

Examples:[code]
  apio api info                # Write to stdout
  apio api info  -o apio.json  # Write to a file[/code]

Currently, the JSON document includes a list of supported boards and various
information about them. Additional information can be added as needed.
"""


timestamp_option = click.option(
    "timestamp",  # Var name.
    "-t",
    "--timestamp",
    type=str,
    metavar="text",
    help="Set a user provided timestamp.",
    cls=cmd_util.ApioOption,
)

output_option = click.option(
    "output",  # Var name.
    "-o",
    "--output",
    type=str,
    metavar="file-name",
    help="Set output file.",
    cls=cmd_util.ApioOption,
)


@click.command(
    name="info",
    cls=ApioCommand,
    short_help="Retrieve apio information.",
    help=APIO_API_INFO_HELP,
)
@timestamp_option
@output_option
@options.force_option_gen(help="Overwrite output file.")
def _info_cli(
    # Options
    timestamp: str,
    output: str,
    force: bool,
):
    """Implements the 'apio apio info' command."""

    # pylint: disable=too-many-locals

    # -- For now, the information is not in a project context. That may
    # -- change in the future.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- The top dict that we will emit as json.
    top_dict = {}

    # -- Append user timestamp if specified.
    if timestamp:
        top_dict["timestamp"] = timestamp

    # -- Generate the 'boards' section.
    boards_section = {}
    for board_id, board_info in apio_ctx.boards.items():
        # -- The board output dict.
        new_board = {}

        # -- Add board description
        new_board["description"] = board_info.get("description", None)

        # -- Add board's fpga information.
        new_fpga = {}
        fpga_id = board_info.get("fpga", None)
        fpga_info = apio_ctx.fpgas.get(fpga_id, {})
        new_fpga["id"] = fpga_id
        new_fpga["part-num"] = fpga_info.get("part_num", None)
        new_fpga["arch"] = fpga_info.get("arch", None)
        new_board["fpga"] = new_fpga

        # -- Add board's programmer information.
        new_programmer = {}
        programmer_id = board_info.get("programmer", {}).get("type", None)
        new_programmer["id"] = programmer_id
        new_board["programmer"] = new_programmer

        # -- Add the board to the boards dict.
        boards_section[board_id] = new_board

    # -- Add the boards section to the top dict.
    top_dict["boards"] = boards_section

    # -- Format the top dict as json text.
    text = json.dumps(top_dict, indent=2)

    if output:
        # -- Output the json text to a user specified file.
        output_path = Path(output)

        if output_path.is_dir():
            cerror(f"The output path {output_path} is a directory.")
            sys.exit(1)

        if output_path.exists() and not force:
            cerror(f"The file already exists {output_path}.")
            cout("Use the --force option to allow overwriting.", style=INFO)
            sys.exit(1)

        with open(output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        # -- Output the json text to stdout.
        print(text, file=sys.stdout)


# ------ apio apio

# -- Text in the rich-text format of the python rich library.
APIO_API_HELP = """
The command group 'apio apio' contains subcommands that that are intended \
to be used by tools and programs such as icestudio, rather than being used \
directly by users.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _info_cli,
            _test_cli,
        ],
    )
]


@click.command(
    name="api",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Apio programmatic interface.",
    help=APIO_API_HELP,
)
def cli():
    """Implements the 'apio apio' command group."""

    # pass
