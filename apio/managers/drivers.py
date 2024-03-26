# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Manage board drivers"""


import sys
import shutil
import subprocess
from pathlib import Path
import click
from apio import util
from apio.profile import Profile
from apio.resources import Resources

FTDI_INSTALL_DRIVER_INSTRUCTIONS = """
   FTDI driver installation:
   Usage instructions

      1. Connect the FTDI FPGA board
      2. Select (Interface 0)
      3. Replace driver by "libusbK"
      4. Reconnect the board
      5. Check `apio system --lsftdi`
"""

FTDI_UNINSTALL_DRIVER_INSTRUCTIONS = """
   FTDI driver uninstallation:
   Usage instructions

      1. Find the FPGA USB Device
      2. Right click
      3. Select "Uninstall"
      4. Accept the dialog
"""

SERIAL_INSTALL_DRIVER_INSTRUCTIONS = """
   Serial driver installation:
   Usage instructions

      1. Connect the Serial FPGA board
      2. Install the driver
      3. Reconnect the board
      4. Check `apio system --lsserial`
"""

SERIAL_UNINSTALL_DRIVER_INSTRUCTIONS = """
   Serial driver uninstallation:
   Usage instructions

      1. Find the FPGA USB Device
      2. Right click
      3. Select "Uninstall"
      4. Accept the dialog
"""


class Drivers:
    """Class for managing the board drivers"""

    # -- The driver installation on linux consist of copying the rule files
    # -- to the /etc/udev/rules.d folder

    # -- FTDI source rules file paths
    resources = util.get_full_path("resources")
    ftdi_rules_local_path = resources / "80-fpga-ftdi.rules"

    # -- Target rule file
    ftdi_rules_system_path = Path("/etc/udev/rules.d/80-fpga-ftdi.rules")

    # Serial rules files paths
    serial_rules_local_path = resources / "80-fpga-serial.rules"
    serial_rules_system_path = Path("/etc/udev/rules.d/80-fpga-serial.rules")

    # Driver to restore: mac os
    driver_c = ""

    def __init__(self) -> None:
        self.profile = None
        self.name = None
        self.version = None
        self.spec_version = None

        # -- Get the platform (a string)
        self.platform = util.get_systype()

    def ftdi_enable(self):
        """Enable the FTDI driver. It depends on the platform"""

        # -- Driver enabling on Linux
        if "linux" in self.platform:
            return self._ftdi_enable_linux()

        # -- Driver enabling on MAC
        if "darwin" in self.platform:
            self._setup_darwin()
            return self._ftdi_enable_darwin()

        # -- Driver enabling on Windows
        if "windows" in self.platform:
            self._setup_windows()
            return self._ftdi_enable_windows()
        return None

    def ftdi_disable(self):
        """Disable the FTDI driver. It depends on the platform"""

        # -- Linux platforms
        if "linux" in self.platform:
            return self._ftdi_disable_linux()

        # -- MAC
        if "darwin" in self.platform:
            self._setup_darwin()
            return self._ftdi_disable_darwin()

        # -- Windows
        if "windows" in self.platform:
            self._setup_windows()
            return self._ftdi_disable_windows()

        return None

    def serial_enable(self):
        """Enable the Serial driver. It depends on the platform"""

        if "linux" in self.platform:
            return self._serial_enable_linux()

        if "darwin" in self.platform:
            self._setup_darwin()
            return self._serial_enable_darwin()

        if "windows" in self.platform:
            self._setup_windows()
            return self._serial_enable_windows()
        return None

    def serial_disable(self):
        """Disable the Serial driver. It depends on the platform"""

        if "linux" in self.platform:
            return self._serial_disable_linux()

        if "darwin" in self.platform:
            self._setup_darwin()
            return self._serial_disable_darwin()

        if "windows" in self.platform:
            self._setup_windows()
            return self._serial_disable_windows()
        return None

    def pre_upload(self):
        """Operations to do before uploading a design
        Only for mac platforms"""

        if "darwin" in self.platform:
            self._setup_darwin()
            self._pre_upload_darwin()

    def post_upload(self):
        """Operations to do after uploading a design
        Only for mac platforms"""

        if "darwin" in self.platform:
            self._setup_darwin()
            self._post_upload_darwin()

    def _setup_darwin(self):
        """Setup operation on Mac"""

        # -- Just read the profile file
        self.profile = Profile()

    def _setup_windows(self):
        """Setup operations on Windows"""

        # -- Read the Profile and Resources files
        profile = Profile()
        resources = Resources()

        # -- On windows the zadig driver installer should be
        # -- execute. Get the package version
        self.name = "drivers"
        self.version = util.get_package_version(self.name, profile)
        self.spec_version = util.get_package_spec_version(self.name, resources)

    def _ftdi_enable_linux(self):
        """Drivers enable on Linux. It copies the .rules file into
        the corresponding folder"""

        click.secho("Configure FTDI drivers for FPGA")

        # -- Check if the target rules file already exists
        if not self.ftdi_rules_system_path.exists():

            # -- The file does not exist. Copy!
            # -- Execute the cmd: sudo cp src_file target_file
            subprocess.call(
                [
                    "sudo",
                    "cp",
                    str(self.ftdi_rules_local_path),
                    str(self.ftdi_rules_system_path),
                ]
            )

            # -- Execute the commands for reloading the udev system
            self._reload_rules()

            click.secho("FTDI drivers enabled", fg="green")
            click.secho("Unplug and reconnect your board", fg="yellow")
        else:
            click.secho("Already enabled", fg="yellow")

    def _ftdi_disable_linux(self):
        """Disable the FTDI drivers on linux"""

        # -- For disabling the FTDI driver the .rules files should be
        # -- removed from the /etc/udev/rules.d/ folder

        # -- Remove the .rules file, if it exists
        if self.ftdi_rules_system_path.exists():
            click.secho("Revert FTDI drivers configuration")

            # -- Execute the sudo rm rules_file command
            subprocess.call(["sudo", "rm", str(self.ftdi_rules_system_path)])

            # -- # -- Execute the commands for reloading the udev system
            self._reload_rules()

            click.secho("FTDI drivers disabled", fg="green")
            click.secho("Unplug and reconnect your board", fg="yellow")
        else:
            click.secho("Already disabled", fg="yellow")

    def _serial_enable_linux(self):
        """Serial drivers enable on Linux"""

        click.secho("Configure Serial drivers for FPGA")

        # -- Check if the target rules file already exists
        if not self.serial_rules_system_path.exists():
            # -- Add the user to the dialout group for
            # -- having access to the serial port
            group_added = self._add_dialout_group()

            # -- The file does not exist. Copy!
            # -- Execute the cmd: sudo cp src_file target_file
            subprocess.call(
                [
                    "sudo",
                    "cp",
                    str(self.serial_rules_local_path),
                    str(self.serial_rules_system_path),
                ]
            )

            # -- Execute the commands for reloading the udev system
            self._reload_rules()

            click.secho("Serial drivers enabled", fg="green")
            click.secho("Unplug and reconnect your board", fg="yellow")
            if group_added:
                click.secho(
                    "Restart your machine to enable the dialout group",
                    fg="yellow",
                )
        else:
            click.secho("Already enabled", fg="yellow")

    def _serial_disable_linux(self):
        """Disable the serial driver on Linux"""

        # -- For disabling the serial driver the corresponding .rules file
        # -- should be removed, it it exists
        if self.serial_rules_system_path.exists():
            click.secho("Revert Serial drivers configuration")

            # -- Execute the sudo rm rule_file cmd
            subprocess.call(["sudo", "rm", str(self.serial_rules_system_path)])

            # -- Execute the commands for reloading the udev system
            self._reload_rules()
            click.secho("Serial drivers disabled", fg="green")
            click.secho("Unplug and reconnect your board", fg="yellow")
        else:
            click.secho("Already disabled", fg="yellow")

    @staticmethod
    def _reload_rules():
        """Execute the commands for reloading the udev system"""

        # -- These are Linux commands that should be executed on
        # -- the shell
        subprocess.call(["sudo", "udevadm", "control", "--reload-rules"])
        subprocess.call(["sudo", "udevadm", "trigger"])
        subprocess.call(["sudo", "service", "udev", "restart"])

    @staticmethod
    def _add_dialout_group():
        """Add the current user to the dialout group on Linux systems"""

        # -- This operation is needed for granting access to the serial port

        # -- Get the current groups of the user
        groups = subprocess.check_output("groups")

        # -- If it does not belong to the dialout group, add it!!
        if "dialout" not in groups.decode():
            # -- Command for adding the user to the dialout group
            subprocess.call("sudo usermod -a -G dialout $USER", shell=True)
            return True
        return None

    def _ftdi_enable_darwin(self):
        # Check homebrew
        brew = subprocess.call("which brew > /dev/null", shell=True)
        if brew != 0:
            click.secho("Error: homebrew is required", fg="red")
        else:
            click.secho("Enable FTDI drivers for FPGA")
            subprocess.call(["brew", "update"])
            self._brew_install("libffi")
            self._brew_install("libftdi")
            self.profile.add_setting("macos_ftdi_drivers", True)
            self.profile.save()
            click.secho("FTDI drivers enabled", fg="green")

    def _ftdi_disable_darwin(self):
        click.secho("Disable FTDI drivers configuration")
        self.profile.add_setting("macos_ftdi_drivers", False)
        self.profile.save()
        click.secho("FTDI drivers disabled", fg="green")

    def _serial_enable_darwin(self):
        # Check homebrew
        brew = subprocess.call("which brew > /dev/null", shell=True)
        if brew != 0:
            click.secho("Error: homebrew is required", fg="red")
        else:
            click.secho("Enable Serial drivers for FPGA")
            subprocess.call(["brew", "update"])
            self._brew_install("libffi")
            self._brew_install("libusb")
            # self._brew_install_serial_drivers()
            click.secho("Serial drivers enabled", fg="green")

    @staticmethod
    def _serial_disable_darwin():
        click.secho("Disable Serial drivers configuration")
        click.secho("Serial drivers disabled", fg="green")

    @staticmethod
    def _brew_install(package):
        subprocess.call(["brew", "install", "--force", package])
        subprocess.call(["brew", "unlink", package])
        subprocess.call(["brew", "link", "--force", package])

    @staticmethod
    def _brew_install_serial_drivers():
        subprocess.call(
            [
                "brew",
                "tap",
                "mengbo/ch340g-ch34g-ch34x-mac-os-x-driver",
                "https://github.com/mengbo/ch340g-ch34g-ch34x-mac-os-x-driver",
            ]
        )
        subprocess.call(
            ["brew", "cask", "install", "wch-ch34x-usb-serial-driver"]
        )

    def _pre_upload_darwin(self):
        if self.profile.settings.get("macos_ftdi_drivers", False):
            # Check and unload the drivers
            driver_a = "com.FTDI.driver.FTDIUSBSerialDriver"
            driver_b = "com.apple.driver.AppleUSBFTDI"
            if self._check_ftdi_driver_darwin(driver_a):
                subprocess.call(["sudo", "kextunload", "-b", driver_a])
                self.driver_c = driver_a
            elif self._check_ftdi_driver_darwin(driver_b):
                subprocess.call(["sudo", "kextunload", "-b", driver_b])
                self.driver_c = driver_b

    def _post_upload_darwin(self):
        if self.profile.settings.get("macos_ftdi_drivers", False):
            # Restore previous driver configuration
            if self.driver_c:
                subprocess.call(["sudo", "kextload", "-b", self.driver_c])

    @staticmethod
    def _check_ftdi_driver_darwin(driver):
        return driver in str(subprocess.check_output(["kextstat"]))

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def _ftdi_enable_windows(self):

        # -- Get the drivers apio package base folder
        drivers_base_dir = util.get_package_dir("tools-drivers")

        # -- No folder --> package not installer (or not correctly installed)
        if not drivers_base_dir:
            util.show_package_path_error(self.name)
            util.show_package_install_instructions(self.name)
            sys.exit(1)

        # -- Build the drivers base bin dir
        drivers_bin_dir = drivers_base_dir / "bin"

        # -- Check if the driver packages is installed
        package_ok = util.check_package(
            self.name, self.version, self.spec_version, drivers_bin_dir
        )

        # -- Not installed. Exit
        if not package_ok:
            sys.exit(1)

        # -- Path to the zadig.ini file
        # -- It is the zadig config file
        zadig_ini_src = drivers_base_dir / "share" / "zadig.ini"
        zadig_ini_dst = Path("zadig.ini")

        # -- copy the zadig.ini file to the current working folder
        # -- so that zadig open it when executed
        shutil.copyfile(zadig_ini_src, zadig_ini_dst)

        # -- Show messages for the user
        click.secho("Launch drivers configuration tool")
        click.secho(FTDI_INSTALL_DRIVER_INSTRUCTIONS, fg="yellow")

        # -- Zadig exe file with full path:
        zadig_exe = drivers_base_dir / "bin" / "zadig.exe"

        try:
            # -- Execute zadig!
            result = util.exec_command(str(zadig_exe))
            click.secho("FTDI drivers configuration finished", fg="green")

        # -- It was not possible to execute Zadig...
        except OSError as exc:
            click.secho("Error: " + str(exc), fg="red")
            click.secho(
                "Trying to execute zadig.exe in command line, "
                "but an error ocurred",
                fg="red",
            )
            click.secho(
                "Please, execute the command again in the command line with"
                " administrator privilegdes",
                fg="red",
            )
            sys.exit(1)

        # -- Remove zadig.ini from the current folder. It is no longer needed
        if zadig_ini_dst.exists():
            zadig_ini_dst.unlink()

        return result.get("returncode")

    @staticmethod
    def _ftdi_disable_windows():
        click.secho("Launch device manager")
        click.secho(FTDI_UNINSTALL_DRIVER_INSTRUCTIONS, fg="yellow")

        result = util.exec_command("mmc devmgmt.msc")
        return result.get("returncode")

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def _serial_enable_windows(self):
        drivers_base_dir = util.get_package_dir("tools-drivers")
        drivers_bin_dir = drivers_base_dir / "bin"

        try:
            if util.check_package(
                self.name, self.version, self.spec_version, drivers_bin_dir
            ):
                click.secho("Launch drivers configuration tool")
                click.secho(SERIAL_INSTALL_DRIVER_INSTRUCTIONS, fg="yellow")
                result = util.exec_command(
                    str(Path(drivers_bin_dir) / "serial_install.exe")
                )
                click.secho(
                    "Serial drivers configuration finished", fg="green"
                )
            else:
                result = 1
        except Exception as exc:
            click.secho("Error: " + str(exc), fg="red")
            result = 1

        if not isinstance(result, int):
            result = result.get("returncode")
        return result

    @staticmethod
    def _serial_disable_windows():
        click.secho("Launch device manager")
        click.secho(SERIAL_UNINSTALL_DRIVER_INSTRUCTIONS, fg="yellow")

        result = util.exec_command("mmc devmgmt.msc")
        return result.get("returncode")
