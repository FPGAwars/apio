# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import re
import click
import shutil
import semantic_version

from os import makedirs, remove, rename
from os.path import isfile, isdir, basename

from apio import util
from apio.api import api_request
from apio.resources import Resources
from apio.profile import Profile

from apio.managers.downloader import FileDownloader
from apio.managers.unpacker import FileUnpacker


class Installer(object):

    def __init__(self, package, platform='', force=False, checkversion=True):

        # Parse version
        if '@' in package:
            split = package.split('@')
            self.package = split[0]
            self.version = split[1]
        else:
            self.package = package
            self.version = None

        self.force_install = force
        self.packages_dir = ''

        self.resources = Resources(platform)

        if self.package in self.resources.packages:

            self.profile = Profile()

            dirname = 'packages'
            self.packages_dir = util.safe_join(util.get_home_dir(), dirname)

            # Get data
            data = self.resources.packages.get(self.package)
            distribution = self.resources.distribution

            self.specversion = distribution.get('packages').get(self.package)
            self.package_name = data.get('release').get('package_name')
            self.extension = data.get('release').get('extension')
            platform = platform or self._get_platform()

            if checkversion:
                # Check version
                valid_version = self._get_valid_version(
                    data.get('repository').get('name'),
                    data.get('repository').get('organization'),
                    data.get('release').get('tag_name'),
                    self.version,
                    self.specversion,
                    force
                )
                # Valid version
                if not valid_version:
                    # Error
                    click.secho(
                        'Error: No version {} found'.format(self.version),
                        fg='red')
                    exit(1)

                self.version = valid_version

                # e.g., [linux_x86_64, linux]
                platform_os = platform.split('_')[0]
                self.download_urls = [
                    {
                        'url': self.get_download_url(data, platform),
                        'platform': platform
                    },
                    {
                        'url': self.get_download_url(data, platform_os),
                        'platform': platform_os
                    }
                ]

        if self.packages_dir == '':
            click.secho(
                'Error: No such package \'{0}\''.format(self.package),
                fg='red')
            exit(1)

    def get_download_url(self, data, platform):
        compressed_name = data.get('release').get('compressed_name')
        self.compressed_name = compressed_name.replace(
            '%V', self.version).replace('%P', platform)
        uncompressed_name = data.get('release').get('uncompressed_name')
        self.uncompressed_name = uncompressed_name.replace(
            '%V', self.version).replace('%P', platform)

        tarball = self._get_tarball_name(
            self.compressed_name,
            self.extension
        )

        download_url = self._get_download_url(
            data.get('repository').get('name'),
            data.get('repository').get('organization'),
            data.get('release').get('tag_name').replace(
                '%V', self.version),
            tarball
        )

        return download_url

    def install(self):
        click.echo('Installing %s package:' % click.style(
            self.package, fg='cyan'))
        if not isdir(self.packages_dir):
            makedirs(self.packages_dir)
        assert isdir(self.packages_dir)
        dlpath = None
        try:
            # Try full platform
            platform_download_url = self.download_urls[0].get('url')
            dlpath = self._download(platform_download_url)
        except IOError as e:
            click.secho('Warning: permission denied in packages directory',
                        fg='yellow')
            click.secho(str(e), fg='red')
        except Exception as e:
            # Try os name
            dlpath = self._install_os_package(platform_download_url)

        # Install downloaded package
        self._install_package(dlpath)

        # Rename unpacked dir to package dir
        self._rename_unpacked_dir()

    def _install_os_package(self, platform_download_url):
        os_download_url = self.download_urls[1].get('url')
        if platform_download_url != os_download_url:
            click.secho(
                'Warning: full platform does not match: {}\
                '.format(self.download_urls[0].get('platform')),
                fg='yellow')
            click.secho(
                '         Trying OS name: {}\
                '.format(self.download_urls[1].get('platform')),
                fg='yellow')
            try:
                return self._download(os_download_url)
            except Exception as e:
                click.secho(
                    'Error: {}'.format(str(e)),
                    fg='red')
        else:
            click.secho(
                'Error: package not availabe for this platform',
                fg='red')

    def _install_package(self, dlpath):
        if dlpath:
            package_dir = util.safe_join(
                self.packages_dir, self.package_name)
            if isdir(package_dir):
                shutil.rmtree(package_dir)
            if self.uncompressed_name:
                self._unpack(dlpath, self.packages_dir)
            else:
                self._unpack(dlpath, util.safe_join(
                    self.packages_dir, self.package_name))

            remove(dlpath)
            self.profile.add_package(self.package, self.version)
            self.profile.save()
            click.secho(
                """Package \'{}\' has been """
                """successfully installed!""".format(self.package),
                fg='green')

    def _rename_unpacked_dir(self):
        if self.uncompressed_name:
            unpack_dir = util.safe_join(
                self.packages_dir, self.uncompressed_name)
            package_dir = util.safe_join(
                self.packages_dir, self.package_name)
            if isdir(unpack_dir):
                rename(unpack_dir, package_dir)

    def uninstall(self):
        if isdir(util.safe_join(self.packages_dir, self.package_name)):
            click.echo('Uninstalling %s package' % click.style(
                self.package, fg='cyan'))
            shutil.rmtree(
                util.safe_join(self.packages_dir, self.package_name))
            click.secho(
                """Package \'{}\' has been """
                """successfully uninstalled!""".format(self.package),
                fg='green')
        else:
            click.secho('Package \'{0}\' is not installed'.format(
                self.package), fg='red')
        self.profile.remove_package(self.package)
        self.profile.save()

    def _get_platform(self):
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

    def _get_valid_version(self, name, organization, tag_name,
                           req_version='', specversion='', force=False):
        # Check spec version
        try:
            spec = semantic_version.Spec(specversion)
        except ValueError:
            click.secho('Invalid distribution version {0}: {1}'.format(
                        name, specversion), fg='red')
            exit(1)

        # Download latest releases list
        releases = api_request('{}/releases'.format(name), organization)

        if req_version:
            # Find required version via @
            return self._find_required_version(
                releases, tag_name, req_version, spec, force)
        else:
            # Find latest version release
            return self._find_latest_version(
                releases, tag_name, req_version, spec)

    def _find_required_version(self, releases, tag_name, req_version, spec,
                               force):
        version = self._check_sem_version(req_version, spec)
        for release in releases:
            prerelease = 'prerelease' in release and release.get('prerelease')
            if 'tag_name' in release:
                tag = tag_name.replace('%V', req_version)
                if tag == release.get('tag_name'):
                    if prerelease and not force:
                        click.secho(
                            'Warning: ' + req_version + ' is' +
                            ' a pre-release.\n' +
                            '         Use --force to install',
                            fg='yellow')
                        exit(2)
                    return version

    def _find_latest_version(self, releases, tag_name, req_version, spec):
        for release in releases:
            prerelease = 'prerelease' in release and release.get('prerelease')
            if 'tag_name' in release:
                pattern = tag_name.replace('%V', '(?P<v>.*?)') + '$'
                match = re.search(pattern, release.get('tag_name'))
                if match:
                    if not prerelease:
                        version = match.group('v')
                        return self._check_sem_version(version, spec)

    def _check_sem_version(self, version, spec):
        try:
            if semantic_version.Version(version) in spec:
                return version
            else:
                click.secho(
                    'Error: Invalid semantic version ({0})'.format(
                        self.specversion),
                    fg='red')
                exit(1)
        except ValueError:
            click.secho(
                'Error: Invalid semantic version ({0})'.format(
                    self.specversion),
                fg='red')
            exit(1)

    def _download(self, url):
        # Note: here we check only for the version of locally installed
        # packages. For this reason we don't say what's the installation
        # path.
        if self.profile.check_package_version(self.package, self.version) \
           or self.force_install:
            fd = FileDownloader(url, self.packages_dir)
            filepath = fd.get_filepath()
            click.secho('Download ' + basename(filepath))
            try:
                fd.start()
            except KeyboardInterrupt:
                if isfile(filepath):
                    remove(filepath)
                click.secho('Abort download!', fg='red')
                exit(1)
            return filepath
        else:
            click.secho('Already installed. Version {0}'.format(
                self.profile.get_package_version(self.package)), fg='yellow')
            return None

    def _unpack(self, pkgpath, pkgdir):
        fu = FileUnpacker(pkgpath, pkgdir)
        return fu.start()
