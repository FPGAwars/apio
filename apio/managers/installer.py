# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Implementation for the apio INSTALL command"""

import sys
import shutil

from pathlib import Path
import click
import requests

from apio import util
from apio.resources import Resources
from apio.profile import Profile
from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


# R0902: Too many instance attributes (12/7) (too-many-instance-attributes)
# pylint: disable=R0902
# R0801: Similar lines in 2 files
# pylint: disable=R0801
class Installer:
    """Installer. Class with methods for installing and managing
    apio packages"""

    def __init__(
        self, package: str, platform: str = "", force=False, checkversion=True
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
        self.resources = None
        self.profile = None
        self.spec_version = None
        self.package_name = None
        self.extension = None
        self.download_urls = None
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
        self.force_install = force

        # -- Installer.package_dir: path were the packages are stored
        # -- Ex. /home/obijuan/.apio/packages
        self.packages_dir = ""

        # -- Get all the resources for the given platform
        # -- Some resources depend on the platform (like the packages)
        # -- but some others don't (like the boards)
        self.resources = Resources(platform)

        # -- Read the profile file
        self.profile = Profile()

        # -- Folder name were the packages are stored
        dirname = "packages"

        # -- If the package is known...
        # --(It is defined in the resources/packages.json file)
        if self.package in self.resources.packages:
            # -- Store the package dir
            self.packages_dir = util.get_home_dir() / dirname

            # Get the data of the given package
            data = self.resources.packages[self.package]

            # Get the information about the valid versions
            distribution = self.resources.distribution

            # Get the spectec package version
            self.spec_version = distribution["packages"][self.package]

            # Get the package name (from resources/package.json file)
            self.package_name = data["release"]["package_name"]

            # Get the extension given to the toolchain. Tipically tar.gz
            self.extension = data["release"]["extension"]

            # Get the current platform (if not forced by the user)
            platform = platform or util.get_systype()

            # Check if the version is ok (It is only done if the
            # checkversion flag has been activated)
            if checkversion:
                # Check version. The filename is read from the
                # repostiroy
                # -- Get the url of the version.txt file
                url_version = data["release"]["url_version"]

                # -- Get the latest version
                # -- It will exit in case of error
                valid_version = self._get_valid_version(url_version)

                # -- It is only execute in case the version is valid
                # -- it will exit otherwise

                # Store the valid version
                self.version = valid_version

                # Get the plaform_os name
                # e.g., [linux_x86_64, linux]
                platform_os = platform.split("_")[0]

                # Build the URLs for downloading the package
                self.download_urls = [
                    {
                        "url": self.get_download_url(data, platform),
                        "platform": platform,
                    },
                    {
                        "url": self.get_download_url(data, platform_os),
                        "platform": platform_os,
                    },
                ]
        # -- The package is kwnown but the version is not correct
        else:
            if self.package in self.profile.packages and checkversion is False:
                self.packages_dir = util.get_home_dir() / dirname

                self.package_name = "toolchain-" + package

        # -- If the Installer.package_dir property was not assigned,
        # -- is because the package was not known. Abort!
        if not self.packages_dir:
            click.secho(f"Error: no such package '{self.package}'", fg="red")
            sys.exit(1)

    def get_download_url(self, package: dict, platform: str) -> str:
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
        compressed_name = package["release"]["compressed_name"]

        # -- Replace the '%V' parameter with the package version
        compressed_name_version = compressed_name.replace("%V", self.version)

        # -- Replace the '%P' parameter with the platform
        self.compressed_name = compressed_name_version.replace("%P", platform)

        # -- Get the uncompressed name. It is also a template with the
        # -- same parameters: %V and %P
        uncompressed_name = package["release"]["uncompressed_name"]

        # -- Replace the '%V' parameter
        uncompress_name_version = uncompressed_name.replace("%V", self.version)

        # -- Replace the '%P' parameter
        self.uncompressed_name = uncompress_name_version.replace(
            "%P", platform
        )

        # -- Build the package tarball filename
        # --- Ex. 'apio-examples-0.0.35.zip'
        tarball = f"{self.compressed_name}.{self.extension}"

        # -- Build the Download URL!
        name = package["repository"]["name"]
        organization = package["repository"]["organization"]
        tag = package["release"]["tag_name"].replace("%V", self.version)

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
            # Try full platform
            # --  Ex. 'https://github.com/FPGAwars/apio-examples/releases/
            # --       download/0.0.35/apio-examples-0.0.35.zip'
            platform_download_url = self.download_urls[0]["url"]

            # -- First step: Download the file
            dlpath = self._download(platform_download_url)

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
            click.secho("Error: Package not found\n", fg="red")

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
            package_dir = self.packages_dir / self.package_name

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
            self.profile.add_package(self.package, self.version)

            # -- Save the profile
            self.profile.save()

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
            package_dir = self.packages_dir / self.package_name

            # -- Rename it!
            if unpack_dir.is_dir():
                unpack_dir.rename(package_dir)

    def uninstall(self):
        """Uninstall the apio package"""

        # -- Build the package filename
        file = self.packages_dir / self.package_name

        # -- Check that it is a folder...
        if file.is_dir():

            # -- Inform the user
            package_color = click.style(self.package, fg="cyan")
            click.echo(f"Uninstalling {package_color} package:")

            # -- Remove the folder with all its content!!
            shutil.rmtree(file)

            # -- Inform the user
            click.secho(
                f"""Package \'{self.package}\' has been """
                """successfully uninstalled!""",
                fg="green",
            )
        else:
            # -- Package not installed!
            util.show_package_path_error(self.package)

        # -- Remove the package from the profile file
        self.profile.remove_package(self.package)
        self.profile.save()

    @staticmethod
    def _get_tarball_name(name, extension):
        tarball = f"{name}.{extension}"
        return tarball

    def _get_valid_version(self, url_version: str) -> str:
        """Get the latest valid version from the given remote
        version.txt file. The file is downloaded and the version is
        read and returned

        - INPUTS:
          * url_version: URL of the package's version.txt file
            Ex. https://github.com/FPGAwars/apio-examples/raw/master/
                version.txt

            The url_version for every package is located in the file:
            resources/packages.json

        - OUTPUT: A string with the package version (Ex. '0.0.35')
        """

        if self.version:
            # -- No checking... return the required version
            return self.version

        # -- Find latest version number released
        # -- It is found in the file version.txt located in the root folder of
        # -- all the APIO packages
        if url_version:
            # -- Get the version.txt with the latest version number
            req = requests.get(url_version, timeout=5)

            # -- Check the server response
            if (
                # pylint: disable=no-member
                req.status_code
                == requests.codes.ok
            ):
                # -- Request OK
                print("File version.txt downloaded!")

                # -- Read the version without the ending \n
                version = req.text.rstrip("\n")

                # -- Debug
                print(f"Version: {version}")

                # -- Return the version
                return version

            # -- There was a problem with the request
            click.secho("Error downloading the version.txt file", fg="red")
            click.secho(f"URL: {url_version}", fg="red")
            click.secho(f"Error code: {req.status_code}", fg="red")
            sys.exit(1)

        # -- Error: No URL defined for the version.txt file
        click.secho(
            "No URL defined for the version.txt file\n"
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
        installed = self.profile.installed_version(self.package, self.version)

        # -- Package already installed, and no force_install flag
        # -- Nothing to download
        if installed and not self.force_install:
            click.secho(
                f"Already installed. Version {self.version}",
                fg="yellow",
            )
            return None

        # ----- Download the package!
        # -- Object for downloading the file
        filed = FileDownloader(url, self.packages_dir)

        # -- Get the destination path
        filepath = filed.destination

        # -- Inform the user
        click.secho(f"Download {filed.fname}")

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


def list_packages(platform: str):
    """List all the available packages"""

    # -- Get all the resources
    resources = Resources(platform)

    # -- List the packages
    resources.list_packages()
