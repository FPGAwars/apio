"""Implementation of the Apio system commands"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import re
import platform
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
        click.secho(f"Number of Serial devices found: {serial_ports}\n")

        for serial_port in serial_ports:
            port = serial_port.get("port")
            description = serial_port.get("description")
            hwid = serial_port.get("hwid")
            click.secho(port, fg="cyan")
            click.secho(f"Description: {description}")
            click.secho(f"Hardware info: {hwid}\n")

        return returncode

    def get_usb_devices(self) -> list:
        """Return a list of the connected USB devices
         This list is obtained by running the "lsusb" command

         * OUTPUT:  A list of objects with the usb devices
        Ex. [{'hwid':'1d6b:0003'}, {'hwid':'8087:0aaa'}, ...]

        It raises an exception in case of not being able to
        execute the "lsusb" command
        """

        # -- Initial empty usb devices list
        usb_devices = []

        # -- Run the "lsusb" command!
        result = self._run_command("lsusb", silent=True)

        # -- Sucess in executing the command
        if result and result["returncode"] == 0:

            # -- Get the list of the usb devices. It is read
            # -- from the command stdout
            # -- Ex: [{'hwid':'1d6b:0003'}, {'hwid':'04f2:b68b'}...]
            usb_devices = self._parse_usb_devices(result["out"])

            # -- Return the devices
            return usb_devices

        # -- It was not possible to run the "lsusb" command
        # -- for reading the usb devices
        raise RuntimeError("Error executing lsusb")

    def get_ftdi_devices(self) -> list:
        """Return a list of the connected FTDI devices
         This list is obtained by running the "lsftdi" command

         * OUTPUT:  A list of objects with the FTDI devices
        Ex. [{'index': '0', 'manufacturer': 'AlhambraBits',
              'description': 'Alhambra II v1.0A - B07-095'}]

        It raises an exception in case of not being able to
        execute the "lsftdi" command
        """

        # -- Initial empty ftdi devices list
        ftdi_devices = []

        # -- Run the "lsftdi" command!
        result = self._run_command("lsftdi", silent=True)

        # -- Sucess in executing the command
        if result and result["returncode"] == 0:

            # -- Get the list of the ftdi devices. It is read
            # -- from the command stdout
            # -- Ex: [{'index': '0', 'manufacturer': 'AlhambraBits',
            # --      'description': 'Alhambra II v1.0A - B07-095'}]
            ftdi_devices = self._parse_ftdi_devices(result["out"])

            # -- Return the devices
            return ftdi_devices

        # -- It was not possible to run the "lsftdi" command
        # -- for reading the ftdi devices
        raise RuntimeError("Error executing lsftdi")

    def _run_command(self, command: str, silent=False) -> dict:
        """Execute the given system command
        * INPUT:
          * command: Command to execute  (Ex. "lsusb")
          * silent: What to do with the command output
            * False --> Do not print on the console
            * True  --> Print on the console
        * OUTPUT: A dictionary with the following properties:
          * returncode:
            * 0: OK! Success in executing the command
            * x: An error has ocurred
          * out: (string). Command output
          * err: (string). Command error output

        In case of not executing the command it returns none!
        """

        # The system tools are locate in the
        # oss-cad-suite package

        # -- Get the package base dir
        # -- Ex. "/home/obijuan/.apio/packages/tools-oss-cad-suite"
        system_base_dir = util.get_package_dir("tools-oss-cad-suite")

        # -- Package not found
        if not system_base_dir:
            # -- Show the error message and a hint
            # -- on how to install the package
            util.show_package_path_error(self.package_name)
            util.show_package_install_instructions(self.package_name)
            raise util.ApioException()

        # -- Get the folder were the binary file is located (PosixPath)
        system_bin_dir = system_base_dir / "bin"

        # -- Get the executable filename
        # -- Ex. Posix('/home/obijuan/.apio/packages/tools-oss-cad-suite/
        # --            bin/lsusb')
        executable_file = system_bin_dir / (command + self.ext)

        # -- Check if the file exist!
        if not executable_file.exists():

            # -- The command was not in the oss-cad-suit package
            # -- Print an error message
            click.secho("Error!\n", fg="red")
            click.secho(f"Command not fount: {executable_file}", fg="red")

            # -- Show the error message and a hint
            # -- on how to install the package
            util.show_package_path_error(self.package_name)
            util.show_package_install_instructions(self.package_name)

            return None

        # -- The command exist! Let's execute it!

        # -- Set the stdout and stderr callbacks, when executing the command
        # -- Silent mode (True): No callback
        on_stdout = None if silent else self._on_stdout
        on_stderr = self._on_stderr

        # -- Execute the command!
        result = util.exec_command(
            executable_file,
            stdout=util.AsyncPipe(on_stdout),
            stderr=util.AsyncPipe(on_stderr),
        )

        # -- Return the result of the execution
        return result

    @staticmethod
    def _on_stdout(line):
        """Callback function. It is executed when the command prints
        information on the standard output
        """
        click.secho(line)

    @staticmethod
    def _on_stderr(line):
        """Callback function. It is executed when the command prints
        information on the standard error
        """
        click.secho(line, fg="red")

    @staticmethod
    def _parse_usb_devices(text: str) -> list:
        """Get a list of usb devices from the input string
        * INPUT: string that contains usb devices
            (Ex. "... 1d6b:0003 ... 8087:0aaa ...")
        * OUTPUT: A list of objects with the usb devices
          Ex. [{'hwid':'1d6b:0003'}, {'hwid':'8087:0aaa'}, ...]
        """

        # -- Build the regular expression for representing
        # -- patterns like '1d6b:0003'
        pattern = r"(?P<hwid>[a-f0-9]{4}:[a-f0-9]{4}?)\s"

        # -- Get the list of strings with that patter
        # -- Ex. ['1d6b:0003','8087:0aaa'...]
        hwids = re.findall(pattern, text)

        # -- Output empty list
        usb_devices = []

        # -- Build the list
        for hwid in hwids:

            # -- Create the Object with the hardware id
            usb_device = {"hwid": hwid}

            # -- Add the object to the output list
            usb_devices.append(usb_device)

        # -- Return the final list
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
