# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import re
import click
import shutil

from os import makedirs, remove, rename
from os.path import isdir, join, basename, expanduser

from . import util
from .api import api_request
from .resources import Resources
from .profile import Profile

from .downloader import FileDownloader
from .unpacker import FileUnpacker


class Installer(object):

    def __init__(self, package):
        self.package = package
        self.version = None

        self.resources = Resources()
        self.profile = Profile()

        if package in self.resources.packages:

            data = self.resources.packages[package]

            self.version = self._get_version(
                data['repository']['name'],
                data['repository']['organization'],
                data['release']['tag_name']
            )

            self.arch = self._get_architecture()

            release = data['release']
            self.compressed_name = release['compressed_name'].replace(
                '%V', self.version).replace('%A', self.arch)
            self.uncompressed_name = release['uncompressed_name'].replace(
                '%V', self.version).replace('%A', self.arch)
            self.package_name = data['release']['package_name']

            if isinstance(data['release']['extension'], dict):
                for os in ['linux', 'darwin', 'windows']:
                    if os in self.arch:
                        self.extension = data['release']['extension'][os]
            else:
                self.extension = data['release']['extension']

            self.tarball = self._get_tarball_name(
                self.compressed_name,
                self.extension
            )

            self.download_url = self._get_download_url(
                data['repository']['name'],
                data['repository']['organization'],
                data['release']['tag_name'].replace('%V', self.version),
                self.tarball
            )

            if 'main_dir' in data.keys():
                self.packages_dir = join(expanduser('~'), data['main_dir'])
            else:
                self.packages_dir = join(util.get_home_dir(), 'packages')

    def install(self):
        if self.version is None:
            click.secho(
                'Package \'{0}\' does not exist'.format(self.package),
                fg='red')
        else:
            click.echo("Installing %s package:" % click.style(
                self.package, fg="cyan"))
            if not isdir(self.packages_dir):
                makedirs(self.packages_dir)
            assert isdir(self.packages_dir)
            try:
                dlpath = None
                dlpath = self._download(self.download_url)
                if dlpath:
                    package_dir = join(self.packages_dir, self.package)
                    if isdir(package_dir):
                        shutil.rmtree(package_dir)
                    self._unpack(dlpath, self.packages_dir)
            except Exception:
                click.secho('Package {0} not found'.format(
                    self.tarball), fg='red')
            else:
                if dlpath:
                    remove(dlpath)
                    self.profile.add(self.package, self.version)
                    self.profile.save()
                    click.secho(
                        """Package \'{}\' has been """
                        """successfully installed!""".format(self.package),
                        fg='green')

            # Rename unpacked dir to package dir
            if self.uncompressed_name:
                unpack_dir = join(self.packages_dir, self.uncompressed_name)
                package_dir = join(self.packages_dir, self.package_name)
                if isdir(unpack_dir):
                    rename(unpack_dir, package_dir)

    def uninstall(self):
        if self.version is None:
            click.secho(
                'Package \'{0}\' does not exist'.format(self.package),
                fg='red')
        else:
            if isdir(join(self.packages_dir, self.package_name)):
                click.echo("Uninstalling %s package" % click.style(
                    self.package, fg="cyan"))
                shutil.rmtree(join(self.packages_dir, self.package_name))
                click.secho(
                    """Package \'{}\' has been """
                    """successfully uninstalled!""".format(self.package),
                    fg='green')
            else:
                click.secho('Package \'{0}\' is not installed'.format(
                    self.package), fg='red')
            self.profile.remove(self.package)
            self.profile.save()

    def _get_architecture(self):
        return util.get_systype()

    def _get_download_url(self, name, organization, tag, tarball):
        url = 'https://github.com/{0}/{1}/releases/download/{2}/{3}'.format(
            organization,
            name,
            tag,
            tarball)
        return url

    def _get_tarball_name(self, name, extension):
        tarball = '{0}.{1}'.format(
            name,
            extension)
        return tarball

    def _get_version(self, name, organization, tag_name):
        version = ''
        releases = api_request('{}/releases/latest'.format(name), organization)
        if releases is not None and 'tag_name' in releases:
            pattern = tag_name.replace('%V', '(?P<v>.*?)') + '$'
            match = re.search(pattern, releases['tag_name'])
            if match:
                version = match.group('v')
        return version

    def _download(self, url, sha1=None, forced=False):
        if self.profile.check_version(self.package, self.version) or forced:
            fd = FileDownloader(url, self.packages_dir)
            click.secho('Download ' + basename(fd.get_filepath()))
            fd.start()
            # fd.verify(sha1)
            return fd.get_filepath()
        else:
            click.secho('Already installed. Version {0}'.format(
                self.profile.get_version(self.package)), fg='yellow')
            return None

    def _unpack(self, pkgpath, pkgdir):
        fu = FileUnpacker(pkgpath, pkgdir)
        return fu.start()
