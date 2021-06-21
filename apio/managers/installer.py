"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import sys
import re
import shutil
from os import makedirs, remove, rename
from os.path import isfile, isdir, basename
import click


from apio import util
from apio.api import api_request
from apio.resources import Resources
from apio.profile import Profile

from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


class Installer:
    """DOC: TODO"""

    def __init__(self, package, platform="", force=False, checkversion=True):

        # Parse version
        if "@" in package:
            split = package.split("@")
            self.package = split[0]
            self.version = split[1]
        else:
            self.package = package
            self.version = None

        self.force_install = force
        self.packages_dir = ""

        self.resources = Resources(platform)

        self.profile = Profile()

        dirname = "packages"

        if self.package in self.resources.packages:

            self.packages_dir = util.safe_join(util.get_home_dir(), dirname)

            # Get data
            data = self.resources.packages.get(self.package)
            distribution = self.resources.distribution

            self.spec_version = distribution.get("packages").get(self.package)
            self.package_name = data.get("release").get("package_name")
            self.extension = data.get("release").get("extension")
            platform = platform or self._get_platform()

            if checkversion:

                # Check version
                valid_version = self._get_valid_version(
                    data.get("repository").get("name"),
                    data.get("repository").get("organization"),
                    data.get("release").get("tag_name"),
                )

                # Valid version
                if not valid_version:
                    # Error
                    click.secho("Error: no valid version found", fg="red")
                    sys.exit(1)

                self.version = valid_version

                # e.g., [linux_x86_64, linux]
                platform_os = platform.split("_")[0]
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

        else:
            if self.package in self.profile.packages and checkversion is False:
                self.packages_dir = util.safe_join(
                    util.get_home_dir(), dirname
                )
                self.package_name = "toolchain-" + package

        if self.packages_dir == "":
            click.secho(
                "Error: no such package '{}'".format(self.package), fg="red"
            )
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

    def install(self):
        """DOC: TODO"""

        click.echo(
            "Installing %s package:" % click.style(self.package, fg="cyan")
        )
        if not isdir(self.packages_dir):
            makedirs(self.packages_dir)
        assert isdir(self.packages_dir)
        dlpath = None
        try:
            # Try full platform
            platform_download_url = self.download_urls[0].get("url")
            dlpath = self._download(platform_download_url)
        except IOError as exc:
            click.secho(
                "Warning: permission denied in packages directory", fg="yellow"
            )
            click.secho(str(exc), fg="red")
        except Exception:
            # Try os name
            dlpath = self._install_os_package(platform_download_url)

        # Install downloaded package
        self._install_package(dlpath)

        # Rename unpacked dir to package dir
        self._rename_unpacked_dir()

    def _install_os_package(self, platform_download_url):
        os_download_url = self.download_urls[1].get("url")
        if platform_download_url != os_download_url:
            click.secho(
                "Warning: full platform does not match: {}\
                ".format(
                    self.download_urls[0].get("platform")
                ),
                fg="yellow",
            )
            click.secho(
                "         Trying OS name: {}\
                ".format(
                    self.download_urls[1].get("platform")
                ),
                fg="yellow",
            )
            try:
                return self._download(os_download_url)
            except Exception as exc:
                click.secho("Error: {}".format(str(exc)), fg="red")
        else:
            click.secho(
                "Error: package not availabe for this platform", fg="red"
            )
        return None

    def _install_package(self, dlpath):
        if dlpath:
            package_dir = util.safe_join(self.packages_dir, self.package_name)
            if isdir(package_dir):
                shutil.rmtree(package_dir)
            if self.uncompressed_name:
                self._unpack(dlpath, self.packages_dir)
            else:
                self._unpack(
                    dlpath,
                    util.safe_join(self.packages_dir, self.package_name),
                )

            remove(dlpath)
            self.profile.add_package(self.package, self.version)
            self.profile.save()
            click.secho(
                """Package \'{}\' has been """
                """successfully installed!""".format(self.package),
                fg="green",
            )

    def _rename_unpacked_dir(self):
        if self.uncompressed_name:
            unpack_dir = util.safe_join(
                self.packages_dir, self.uncompressed_name
            )
            package_dir = util.safe_join(self.packages_dir, self.package_name)
            if isdir(unpack_dir):
                rename(unpack_dir, package_dir)

    def uninstall(self):
        """DOC: TODO"""

        if isdir(util.safe_join(self.packages_dir, self.package_name)):
            click.echo(
                "Uninstalling %s package:"
                % click.style(self.package, fg="cyan")
            )
            shutil.rmtree(util.safe_join(self.packages_dir, self.package_name))
            click.secho(
                """Package \'{}\' has been """
                """successfully uninstalled!""".format(self.package),
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
        url = "https://github.com/{0}/{1}/releases/download/{2}/{3}".format(
            organization, name, tag, tarball
        )
        return url

    @staticmethod
    def _get_tarball_name(name, extension):
        tarball = "{0}.{1}".format(name, extension)
        return tarball

    def _get_valid_version(self, rel_name, organization, tag_name):

        # Download latest releases list
        releases = api_request("{}/releases".format(rel_name), organization)

        if self.version:

            # Find required version via @
            if not util.check_package_version(self.version, self.spec_version):

                util.show_package_version_warning(
                    self.package, self.version, self.spec_version
                )
                sys.exit(1)

            return self._find_required_version(
                releases, tag_name, self.version
            )

        # Find latest version release
        return self._find_latest_version(releases, tag_name, self.spec_version)

    def _find_required_version(self, releases, tag_name, req_v):
        for release in releases:
            if "tag_name" in release:
                tag = tag_name.replace("%V", req_v)
                if tag == release.get("tag_name"):
                    prerelease = release.get("prerelease", False)
                    if prerelease and not self.force_install:
                        click.secho(
                            "Warning: "
                            + req_v
                            + " is"
                            + " a pre-release. Use --force to install",
                            fg="yellow",
                        )
                        sys.exit(1)
                    return req_v
        return None

    @staticmethod
    def _find_latest_version(releases, tag_name, spec_v):
        for release in releases:
            if "tag_name" in release:
                pattern = tag_name.replace("%V", "(?P<v>.*?)") + "$"
                match = re.search(pattern, release.get("tag_name"))
                if match:
                    prerelease = release.get("prerelease", False)
                    if not prerelease:
                        version = match.group("v")
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

        click.secho(
            "Already installed. Version {0}".format(
                self.profile.get_package_version(self.package)
            ),
            fg="yellow",
        )
        return None

    @staticmethod
    def _unpack(pkgpath, pkgdir):
        fileu = FileUnpacker(pkgpath, pkgdir)
        return fileu.start()
