"""Implementation of the Apio system commands"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import re
import platform
from pathlib import Path
from os.path import isfile
import click

from apio import util
from apio.profile import Profile
from apio.resources import Resources


class System:  # pragma: no cover
    """System class. Managing and execution of the system commands"""

    def __init__(self):

        # -- Read the profile from the file
        profile = Profile()

        # -- Read the resources from the corresponding files
        resources = Resources()

        # -- This command is called system
        self.name = "system"

        # -- Package name: apio package were all the system commands
        # -- are located
        # -- From apio > 0.7 the system tools are located inside the
        # -- oss-cad-suite
        self.package_name = "oss-cad-suite"

        # -- Get the installed package versions
        self.version = util.get_package_version(self.name, profile)

        # -- Get the spected versions
        self.spec_version = util.get_package_spec_version(self.name, resources)

        # -- Windows: Executables should end with .exe
        self.ext = ""
        if platform.system() == "Windows":
            self.ext = ".exe"

    def lsusb(self):
        """Run the lsusb system command"""

        returncode = 1
        result = self._run_command("lsusb")

        if result:
            returncode = result.get("returncode")

        return returncode

    def lsftdi(self):
        """DOC: TODO"""

        returncode = 1
        result = self._run_command("lsftdi")

        if result:
            returncode = result.get("returncode")

        return returncode

    @staticmethod
    def lsserial():
        """DOC: TODO"""

        returncode = 0
        serial_ports = util.get_serial_ports()
        click.secho(
            "Number of Serial devices found: {}\n".format(len(serial_ports))
        )

        for serial_port in serial_ports:
            port = serial_port.get("port")
            description = serial_port.get("description")
            hwid = serial_port.get("hwid")
            click.secho(port, fg="cyan")
            click.secho("Description: {}".format(description))
            click.secho("Hardware info: {}\n".format(hwid))

        return returncode

    def get_usb_devices(self):
        """DOC: TODO"""

        usb_devices = []
        result = self._run_command("lsusb", silent=True)

        if result and result.get("returncode") == 0:
            usb_devices = self._parse_usb_devices(result.get("out"))
        else:
            raise Exception

        return usb_devices

    def get_ftdi_devices(self):
        """DOC: TODO"""

        ftdi_devices = []
        result = self._run_command("lsftdi", silent=True)

        if result and result.get("returncode") == 0:
            ftdi_devices = self._parse_ftdi_devices(result.get("out"))
        else:
            raise Exception

        return ftdi_devices

    def _run_command(self, command, silent=False):
        result = {}

        print(f"Run Command: {command}")

        # From apio >= 0.7.0, the system tools are locate in the
        # oss-cad-suite package instead of the system package
        # So first let's try to execute them from there

        # -- Get the package base dir
        system_base_dir = util.get_package_dir("tools-oss-cad-suite")
        print(f"System_base_dir: {system_base_dir}")

        # -- Get the folder were the binary file is locateds
        system_bin_dir = Path(system_base_dir) / "bin"
        print(f"System bin dir: {system_bin_dir}")

        # -- Get the executable filename
        executable_file = system_bin_dir / (command + self.ext)
        print(f"Executable file: {executable_file}")

        # -- Set the stdout and stderr for executing the command
        on_stdout = None if silent else self._on_stdout
        on_stderr = self._on_stderr

        # -- Check if the executable exists
        if isfile(executable_file):

            # -- Execute the command!
            result = util.exec_command(
                executable_file,
                stdout=util.AsyncPipe(on_stdout),
                stderr=util.AsyncPipe(on_stderr),
            )

            # -- Return the result of the execution
            return result

        # -- The command does not exist in the tools-oss-cad-suite package
        # -- Try with the tool-system package (old-package,
        # -- (for compatibility reasons)

        # -- Get the package base dir
        system_base_dir = util.get_package_dir("tools-system")
        print(f"System_base_dir: {system_base_dir}")

        # -- Get the folder were the binary file is locateds
        system_bin_dir = Path(system_base_dir) / "bin"
        print(f"System bin dir: {system_bin_dir}")

        # -- Get the executable filename
        executable_file = system_bin_dir / (command + self.ext)
        print(f"Executable file: {executable_file}")

        # -- Check if the executable exists
        if isfile(executable_file):

            # -- Execute the command!
            result = util.exec_command(
                executable_file,
                stdout=util.AsyncPipe(on_stdout),
                stderr=util.AsyncPipe(on_stderr),
            )

            # -- Return the result of the execution
            return result

        # -- The command was not in the oss-cad-suit package
        # -- The command was not in the old system package
        # -- Show the error message and a hint on how to install the package
        print("ERROR!!!!!!")
        util.show_package_path_error(self.package_name)
        util.show_package_install_instructions(self.package_name)

        return None

    @staticmethod
    def _on_stdout(line):
        click.secho(line)

    @staticmethod
    def _on_stderr(line):
        click.secho(line, fg="red")

    @staticmethod
    def _parse_usb_devices(text):
        pattern = r"(?P<hwid>[a-f0-9]{4}:[a-f0-9]{4}?)\s"
        hwids = re.findall(pattern, text)

        usb_devices = []

        for hwid in hwids:
            usb_device = {"hwid": hwid}
            usb_devices.append(usb_device)

        return usb_devices

    @staticmethod
    def _parse_ftdi_devices(text):
        pattern = r"Number\sof\sFTDI\sdevices\sfound:\s(?P<n>\d+?)\n"
        match = re.search(pattern, text)
        num = int(match.group("n")) if match else 0

        pattern = r".*Checking\sdevice:\s(?P<index>.*?)\n.*"
        index = re.findall(pattern, text)

        pattern = r".*Manufacturer:\s(?P<n>.*?),.*"
        manufacturer = re.findall(pattern, text)

        pattern = r".*Description:\s(?P<n>.*?)\n.*"
        description = re.findall(pattern, text)

        ftdi_devices = []

        for i in range(num):
            ftdi_device = {
                "index": index[i],
                "manufacturer": manufacturer[i],
                "description": description[i],
            }
            ftdi_devices.append(ftdi_device)

        return ftdi_devices
