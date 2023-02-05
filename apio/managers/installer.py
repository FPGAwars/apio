"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2021 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import re
import shutil
from pathlib import Path
from os import makedirs, remove, rename
from os.path import isfile, isdir, basename
import click
import requests


from apio import util

# from apio.api import api_request
from apio.resources import Resources
from apio.profile import Profile

from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


# R0902: Too many instance attributes (12/7) (too-many-instance-attributes)
# pylint: disable=R0902
class Installer:
    """Installer. Class with methods for installing and managing
    packages"""

    def __init__(self, package, platform="", force=False, checkversion=True):
        """Class initialization. Parameters:
        * package:  Package name to manage/install. It can have a prefix with
                    the version. Ex. "system@1.1.2"
        """

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

        self.profile = Profile()

        # -- Folder name were the packages are stored
        dirname = "packages"

        # -- If the package is known...
        # --(It is defined in the resources/packages.json file)
        if self.package in self.resources.packages:
            # -- Store the package dir
            self.packages_dir = str(Path(util.get_home_dir()) / dirname)

            # Get the data of the given package
            data = self.resources.packages.get(self.package)

            # Get the information about the valid versions
            distribution = self.resources.distribution

            # Get the spectec package version
            self.spec_version = distribution.get("packages").get(self.package)

            # Get the package name (from resources/package.json file)
            self.package_name = data.get("release").get("package_name")

            # Get the extension given to the toolchain. Tipically tar.gz
            self.extension = data.get("release").get("extension")

            # Get the current platform
            platform = platform or self._get_platform()

            # Check if the version is ok (It is only done if the
            # checkversion flag has been activated)
            if checkversion:
                # Check version. The filename is read from the
                # repostiroy
                # -- Get the url of the version.txt file
                url_version = data.get("release").get("url_version")

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
                self.packages_dir = str(Path(util.get_home_dir()) / dirname)

                self.package_name = "toolchain-" + package

        # -- If the Installer.package_dir is empty, is because the package
        # -- was not known. Abort!
        if self.packages_dir == "":
            click.secho(f"Error: no such package '{self.package}'", fg="red")
            sys.exit(1)

    def get_download_url(self, data, platform):
        """DOC: TODO"""

        compressed_name = data.get("release").get("compressed_name")
        self.compressed_name = compressed_name.replace(
            "%V", self.version
        ).replace("%P", platform)
        uncompressed_name = data.get("release").get("uncompressed_name")
        self.uncompressed_name = uncompressed_name.replace(
            "%V", self.version
        ).replace("%P", platform)

        tarball = self._get_tarball_name(self.compressed_name, self.extension)

        download_url = self._get_download_url(
            data.get("repository").get("name"),
            data.get("repository").get("organization"),
            data.get("release").get("tag_name").replace("%V", self.version),
            tarball,
        )

        return download_url

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def install(self):
        """Install the current package in the set in the Installer Object"""

        # -- Warning if the package has been marked as obsolete
        if self.package in self.resources.obsolete_pkgs:
            # -- Get the string with the new package to use instead
            # -- of the obsolete one (if available)
            if self.resources.obsolete_pkgs[self.package] != "":
                new_package = self.resources.obsolete_pkgs[self.package]
                new_package_msg = f"Use {new_package} instead\n"
            else:
                new_package_msg = ""

            click.secho(
                f"Warning: Package {self.package} is obsolete. "
                f"Will be removed in the future. "
                f"{new_package_msg}",
                fg="yellow",
            )

        click.secho(f"Installing {self.package} package:", fg="cyan")

        # -- Create the apio package folder, if it does not exit
        if not isdir(self.packages_dir):
            makedirs(self.packages_dir)
        assert isdir(self.packages_dir)

        # -- The first step is downloading the package
        # -- This variable stores the path to the packages
        dlpath = None

        try:
            # Try full platform
            platform_download_url = self.download_urls[0].get("url")
            print(f"platform_download_url: {platform_download_url}")
            dlpath = self._download(platform_download_url)

        # -- There is no write access to the package folder
        except IOError as exc:
            click.secho(
                "Warning: permission denied in packages directory", fg="yellow"
            )
            click.secho(str(exc), fg="red")

        # --
        except Exception:
            # Try os name
            dlpath = self._install_os_package(platform_download_url)

        # -- Second step: Install downloaded package
        self._install_package(dlpath)

        # Rename unpacked dir to package dir
        self._rename_unpacked_dir()

    # W0703: Catching too general exception Exception (broad-except)
    # pylint: disable=W0703
    def _install_os_package(self, platform_download_url):
        os_download_url = self.download_urls[1].get("url")
        if platform_download_url != os_download_url:
            name = self.download_urls[0].get("platform")
            click.secho(
                f"Warning: full platform does not match: {name}",
                fg="yellow",
            )

            os_name = self.download_urls[1].get("platform")
            click.secho(
                f"         Trying OS name: {os_name}",
                fg="yellow",
            )
            try:
                return self._download(os_download_url)
            except Exception as exc:
                click.secho(f"Error: {str(exc)}", fg="red")
        else:
            click.secho(
                "Error: package not availabe for this platform", fg="red"
            )
        return None

    def _install_package(self, dlpath):
        if dlpath:
            package_dir = str(Path(self.packages_dir) / self.package_name)
            if isdir(package_dir):
                shutil.rmtree(package_dir)
            if self.uncompressed_name:
                self._unpack(dlpath, self.packages_dir)
            else:
                self._unpack(
                    dlpath,
                    package_dir,
                )

            remove(dlpath)
            self.profile.add_package(self.package, self.version)
            self.profile.save()
            click.secho(
                f"""Package \'{self.package}\' has been """
                """successfully installed!""",
                fg="green",
            )

    def _rename_unpacked_dir(self):
        if self.uncompressed_name:
            # -- Build the names
            unpack_dir = str(Path(self.packages_dir) / self.uncompressed_name)
            package_dir = str(Path(self.packages_dir) / self.package_name)

            if isdir(unpack_dir):
                rename(unpack_dir, package_dir)

    def uninstall(self):
        """DOC: TODO"""

        # -- Build the filename
        file = str(Path(self.packages_dir) / self.package_name)
        if isdir(file):
            package_color = click.style(self.package, fg="cyan")
            click.echo(f"Uninstalling {package_color} package:")
            shutil.rmtree(file)
            click.secho(
                f"""Package \'{self.package}\' has been """
                """successfully uninstalled!""",
                fg="green",
            )
        else:
            util.show_package_path_error(self.package)
        self.profile.remove_package(self.package)
        self.profile.save()

    @staticmethod
    def _get_platform():
        return util.get_systype()

    @staticmethod
    def _get_download_url(name, organization, tag, tarball):
        url = (
            f"https://github.com/{organization}/{name}/releases/"
            + f"download/{tag}/{tarball}"
        )
        return url

    @staticmethod
    def _get_tarball_name(name, extension):
        tarball = f"{name}.{extension}"
        return tarball

    def _get_valid_version(self, url_version=""):
        """Get the latest valid version from the given remote
        version.txt file. The file is downloaded and the version is
        read and returned

        - INPUTS:
          * url_version: URL of the package's version.txt file
            Ex. https://github.com/FPGAwars/apio-examples/raw/master/
                version.txt

            The url_version for every package is located in the file:
            resources/packages.json
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

    # -- This function can be removed
    @staticmethod
    def _find_required_version(releases, tag_name, req_v):
        for release in releases:
            if "tag_name" in release:
                tag = tag_name.replace("%V", req_v)
                if tag == release.get("tag_name"):
                    return req_v
        return None

    @staticmethod
    def _find_latest_version(releases, tag_name, spec_v):
        print("->Find latest version")

        for release in releases:
            if "tag_name" in release:
                pattern = tag_name.replace("%V", "(?P<v>.*?)") + "$"
                print(f"Pattern: {pattern}")
                print(f"Release tag_name: {release.get('tag_name')}")
                match = re.search(pattern, release.get("tag_name"))
                if match:
                    prerelease = release.get("prerelease", False)
                    if not prerelease:
                        version = match.group("v")
                        print(f"Match: Version: {version}")
                        if util.check_package_version(version, spec_v):
                            return version
        return None

    def _download(self, url):
        # Note: here we check only for the version of locally installed
        # packages. For this reason we don't say what's the installation
        # path.
        if (
            not self.profile.installed_version(self.package, self.version)
            or self.force_install
        ):
            filed = FileDownloader(url, self.packages_dir)
            filepath = filed.get_filepath()
            click.secho("Download " + basename(filepath))
            try:
                filed.start()
            except KeyboardInterrupt:
                if isfile(filepath):
                    remove(filepath)
                click.secho("Abort download!", fg="red")
                sys.exit(1)
            return filepath

        version = self.profile.get_package_version(self.package)
        click.secho(
            f"Already installed. Version {version}",
            fg="yellow",
        )
        return None

    @staticmethod
    def _unpack(pkgpath, pkgdir):
        fileu = FileUnpacker(pkgpath, pkgdir)
        return fileu.start()
