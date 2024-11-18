# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Implementation for the apio PACKAGES command"""

import sys
import shutil

from pathlib import Path
from dataclasses import dataclass
import click
import requests

from apio import util
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


# R0902: Too many instance attributes (12/7) (too-many-instance-attributes)
# pylint: disable=R0902
# R0801: Similar lines in 2 files
# pylint: disable=R0801
class Installer:
    """Installer. Class with methods for installing and managing
    apio packages"""

    @dataclass(frozen=True)
    class Modifiers:
        """A workaround for the linter limitation of 4 arguments per method."""

        force: bool
        checkversion: bool
        verbose: bool

    def __init__(
        self,
        package: str,
        resources=None,
        modifiers=Modifiers(force=False, checkversion=True, verbose=False),
    ):
        """Class initialization. Parameters:
        * package:  Package name to manage/install. It can have a sufix with
                    the version. Ex. "system@1.1.2"
        """

        # -- Refactoring: Join together all the attributes
        # -- This class has too many attributes (it is too complex)
        # -- It should be refactor
        # -- Al the attributes are shown together so that it is
        # -- easier to refactor them in the future
        self.package = None
        self.version = None
        self.force_install = None
        self.packages_dir = None
        self.resources = resources
        self.spec_version = None
        self.package_folder_name = None
        self.extension = None
        self.download_url = None
        self.compressed_name = None

        # Parse version. The following attributes are used:
        #  * Installer.package: Package name (without version)
        #  * Installer.version: Package version (or None)
        if "@" in package:
            split = package.split("@")
            self.package = split[0]
            self.version = split[1]
        else:
            self.package = package
            self.version = None

        # -- Attribute Installer.force_install
        # -- Force installation or not
        self.force_install = modifiers.force

        # -- Show detailed output.
        self.verbose = modifiers.verbose

        # -- Installer.package_dir: path were the packages are stored
        # -- Ex. /home/obijuan/.apio/packages
        self.packages_dir = ""

        # -- Folder name were the packages are stored
        # --
        # -- NOTE: we shouldn't assume the directory name since it can be
        # -- overriden with APIO_PKG_DIR but since this old installer is
        # -- going away, we leave this as is.  (Nov 2024)
        dirname = "packages"

        # -- If the package is known...
        # --(It is defined in the resources/packages.json file)
        if self.package in self.resources.platform_packages:
            # -- Store the package dir
            self.packages_dir = util.get_home_dir() / dirname

            # Get the metadata of the given package
            package_info = self.resources.platform_packages[self.package]

            # Get the information about the valid versions
            distribution = self.resources.distribution

            # Get the spectec package version
            self.spec_version = distribution["packages"][self.package]

            # Get the package folder name under the packages root dir.
            self.package_folder_name = package_info["release"]["folder_name"]

            # Get the extension given to the toolchain. Tipically tar.gz
            self.extension = package_info["release"]["extension"]

            # Check if the version is ok (It is only done if the
            # checkversion flag has been activated)
            if modifiers.checkversion:
                # Check version. The filename is read from the repostiroy.
                # -- Get the url of the version file
                url_version = package_info["release"]["url_version"]

                # -- Get the latest version
                # -- It will exit in case of error
                remote_version = self._get_latest_version(url_version)

                # -- It is only execute in case the version is valid
                # -- it will exit otherwise

                # Store the valid version
                self.version = remote_version

                # Get the plaform_os name
                # e.g., [linux_x86_64, linux]
                # platform_os = platform.split("_")[0]

                # Build the URLs for downloading the package
                self.download_url = self._get_download_url(package_info)

        # -- The package is kwnown but the version is not correct
        else:
            if (
                self.package in self.resources.profile.packages
                and modifiers.checkversion is False
            ):
                self.packages_dir = util.get_home_dir() / dirname

                self.package_folder_name = "toolchain-" + package

        # -- If the Installer.package_dir property was not assigned,
        # -- is because the package was not known. Abort!
        if not self.packages_dir:
            click.secho(f"Error: no such package '{self.package}'", fg="red")
            sys.exit(1)

    def _get_download_url(self, package_info: dict) -> str:
        """Get the download URL for the given package
        * INPUTS:
          - package: Object with the package information:
            * Respository
              - name
              - organization
            * Release
              - tag_name
              - compressed_name
              - uncompressed_name
              - package_name
              - extension
              - url_version
            * Description
          - plaform: Destination platform (Ex. linux_x86_64)
        * OUTPUT: The download URL
          (Ex: 'https://github.com/FPGAwars/apio-examples/releases/
                download/0.0.35/apio-examples-0.0.35.zip')
        """

        # -- Get the compressed name
        # -- It is in fact a template, with paramters:
        # --  %V : Version
        # --  %P : Platfom
        # -- Ex: 'apio-examples-%V'
        compressed_name = package_info["release"]["compressed_name"]

        # -- Replace the '%V' parameter with the package version
        compressed_name_version = compressed_name.replace("%V", self.version)

        # -- Map Replace the '%P' parameter with the package selector of this
        # -- platform (the package selectors are specified in platforms.json).
        package_selector = self.resources.platforms[
            self.resources.platform_id
        ]["package_selector"]
        self.compressed_name = compressed_name_version.replace(
            "%P", package_selector
        )

        # -- Get the uncompressed name. It is also a template with the
        # -- same parameters: %V and %P
        uncompressed_name = package_info["release"]["uncompressed_name"]

        # -- Replace the '%V' parameter
        uncompress_name_version = uncompressed_name.replace("%V", self.version)

        # -- Replace the '%P' parameter
        self.uncompressed_name = uncompress_name_version.replace(
            "%P", self.resources.platform_id
        )

        # -- Build the package tarball filename
        # --- Ex. 'apio-examples-0.0.35.zip'
        tarball = f"{self.compressed_name}.{self.extension}"

        # -- Build the Download URL!
        name = package_info["repository"]["name"]
        organization = package_info["repository"]["organization"]
        tag = package_info["release"]["tag_name"].replace("%V", self.version)

        download_url = (
            f"https://github.com/{organization}/{name}/releases/"
            f"download/{tag}/{tarball}"
        )

        return download_url

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def install(self):
        """Install the current package set in the Installer Object"""

        click.secho(f"Installing {self.package} package:", fg="cyan")

        # -- Create the apio package folder, if it does not exit
        self.packages_dir.mkdir(exist_ok=True)

        # -- The first step is downloading the package
        # -- This variable stores the path to the packages
        dlpath = None

        try:
            # -- Try downloading the file
            dlpath = self._download(self.download_url)

        # -- There is no write access to the package folder
        except IOError as exc:
            click.secho(
                "Warning: permission denied in packages directory", fg="yellow"
            )
            click.secho(str(exc), fg="red")

        # -- In case of any other error, try to install with the other
        # -- url...
        # --- ummm very likely this second installation can be removed...
        # except Exception:
        # Try os name
        # dlpath = self._install_os_package(platform_download_url)
        except util.ApioException:
            click.secho("Error: package not found\n", fg="red")

        # -- Second step: Install downloaded package
        self._install_package(dlpath)

        # -- Rename unpacked dir to package dir
        self._rename_unpacked_dir()

    def _install_package(self, dlpath: Path):
        """Install the given tarball"""

        # -- Make sure there is a non-null filepath
        if dlpath:

            # -- Build the destination path
            # -- Ex. '/home/obijuan/.apio/packages/examples'
            package_dir = self.packages_dir / self.package_folder_name

            if self.verbose:
                click.secho(f"Package dir: {package_dir.absolute()}")

            # -- Destination path is a folder (Already exist!)
            if package_dir.is_dir():

                # -- Remove it!
                shutil.rmtree(package_dir)

            # -- The packages that have the property uncompressed_name
            # -- have a folder (with that name) inside the compresssed file
            # -- Ex. The package examples has the folder apio-examples-0.0.35
            # -- Because of this, it should be unpacked directly in the
            # -- packages folder (Ex. /home/obijuan/.paio/packages) and then
            # -- rename the folder to the package name
            # -- (Ex. apio-examples-0.0.35 -> examples)
            if self.uncompressed_name:

                # -- Uncompress it!!
                # -- Ex. folder: /home/obijuan/.apio/packages
                self._unpack(dlpath, self.packages_dir)

            # -- In this other case the package is directly
            # -- unpack in the package_dir folder
            # -- Ex. packages/tools-oss-cad-suite
            else:
                self._unpack(dlpath, package_dir)

            # -- Remove the downloaded compress file
            # -- Ex. remove '/home/obijuan/.apio/packages/
            #                apio-examples-0.0.35.zip'
            dlpath.unlink()

            # -- Add package to profile
            self.resources.profile.add_package(self.package, self.version)

            # -- Save the profile
            self.resources.profile.save()

            # -- Inform the user!
            click.secho(
                f"""Package \'{self.package}\' has been """
                """successfully installed!""",
                fg="green",
            )

    def _rename_unpacked_dir(self):
        """Change the name of the downloaded file to the final one
        Ex. '/home/obijuan/.apio/packages/apio-examples-0.0.35'
        ---> '/home/obijuan/.apio/packages/examples'
        Only for packages that has the property uncompressed_name
        """

        if self.uncompressed_name:

            # -- Build the names
            # -- src folder (the one downloaded and installed)
            # -- Ex. '/home/obijuan/.apio/packages/apio-examples-0.0.35'
            unpack_dir = self.packages_dir / self.uncompressed_name

            # -- New folder
            # -. Ex, '/home/obijuan/.apio/packages/examples'
            package_dir = self.packages_dir / self.package_folder_name

            # -- Rename it!
            if unpack_dir.is_dir():
                unpack_dir.rename(package_dir)

    def uninstall(self):
        """Uninstall the apio package"""

        # -- Build the package filename
        file = self.packages_dir / self.package_folder_name

        if self.verbose:
            click.secho(f"Package dir: {file.absolute()}")

        # -- Check that it is a folder...
        if file.is_dir():

            # -- Inform the user
            package_color = click.style(self.package, fg="cyan")
            click.secho(f"Uninstalling {package_color} package:")

            # -- Remove the folder with all its content!!
            shutil.rmtree(file)

            # -- Inform the user
            click.secho(
                f"Package '{self.package}' has been "
                "successfully uninstalled.",
                fg="green",
            )
        else:
            # -- Package not installed. We treat it as a success.
            click.secho(
                f"Package '{self.package}' was not installed.", fg="green"
            )

        # -- Remove the package from the profile file
        self.resources.profile.remove_package(self.package)
        self.resources.profile.save()

    @staticmethod
    def _get_tarball_name(name, extension):
        tarball = f"{name}.{extension}"
        return tarball

    def _get_latest_version(self, url_version: str) -> str:
        """Get the latest recommanded version from the given remote
        version file. The file is downloaded and the version is
        read and returned

        - INPUTS:
          * url_version: URL of the package's version file
            Ex. https://github.com/FPGAwars/apio-examples/raw/master/
                VERSION

            The url_version for every package is located in the file:
            resources/packages.json

        - OUTPUT: A string with the package version (Ex. '0.0.35')
        """

        if self.version:
            # -- No checking... return the required version
            return self.version

        # -- Find latest version number released. It is found using the
        # -- version url package configuration.
        if url_version:
            if self.verbose:
                click.secho(f"Version url: {url_version}")

            # -- Get the version file with the latest version number
            req = requests.get(url_version, timeout=5)

            # -- Check the server response
            if (
                # pylint: disable=no-member
                req.status_code
                == requests.codes.ok
            ):
                # -- Request OK
                print("Remote version file downloaded.")

                # -- Read the version without the ending \n
                version = req.text.rstrip("\n")

                # -- Debug
                print(f"Remote version: {version}")

                # -- Return the version
                return version

            # -- There was a problem with the request
            click.secho("Error downloading the version file", fg="red")
            click.secho(f"URL: {url_version}", fg="red")
            click.secho(f"Error code: {req.status_code}", fg="red")
            sys.exit(1)

        # -- Error: No URL defined for the version file
        click.secho(
            "No URL defined for the version file\n"
            + "It is not possible to get the latest version number",
            fg="red",
        )
        click.secho("Check the resources/packages.json file", fg="red")
        sys.exit(1)

    def _download(self, url: str) -> str:
        """Download the given file (url). Return the path of
        the destination file
        * INPUTS:
          * url: File to download
        * OUTPUTS:
          * The path of the destination file
        """

        # -- Check the installed version of the package
        installed_ok = self.resources.profile.is_installed_version_ok(
            self.package, self.version, self.verbose
        )

        # -- Package already installed, and no force_install flag
        # -- Nothing to download
        if installed_ok and not self.force_install:
            click.secho(
                f"Already installed. Version {self.version}",
                fg="yellow",
            )
            return None

        # ----- Download the package!
        if self.verbose:
            click.secho(f"Src url: {url}")

        # -- Object for downloading the file
        filed = FileDownloader(url, self.packages_dir)

        # -- Get the destination path
        filepath = filed.destination

        # -- Inform the user
        if self.verbose:
            click.secho(f"Local file: {filepath}")

        # -- Download start!
        try:
            filed.start()

        # -- If the user press Ctrl-C (Abort)
        except KeyboardInterrupt:

            # -- Remove the file
            if filepath.is_file():
                filepath.unlink()

            # -- Inform the user
            click.secho("Abort download!", fg="red")
            sys.exit(1)

        # -- Return the destination path
        return filepath

    @staticmethod
    def _unpack(pkgpath: Path, pkgdir: Path):
        """Unpack the given file, in the pkgdir
        * INPUTS:
          - pkgpath: File to unpack
          - pkgdir: Destination path
        """

        # -- Build the unpacker object
        fileu = FileUnpacker(pkgpath, pkgdir)

        # -- Unpack it!
        success = fileu.start()

        return success
