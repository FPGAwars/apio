# Installer class

import click
import shutil

from os import makedirs, remove
from os.path import isdir, join, basename

from . import util
from .profile import Profile
from .downloader import FileDownloader
from .unpacker import FileUnpacker


class Installer(object):

    # Main packages dir
    profile = Profile()
    packages_dir = join(util.get_home_dir(), 'packages')

    def __init__(self):
        self.package = None

    def install(self):
        if self.package is not None:
            click.secho('Install ', nl=False)
            click.secho(self.package, fg='cyan')
            if not isdir(self.packages_dir):
                makedirs(self.packages_dir)
            assert isdir(self.packages_dir)
            try:
                dlpath = None
                dlpath = self._download(self._get_download_url())
                if dlpath:
                    package_dir = join(self.packages_dir, self.package)
                    if isdir(package_dir):
                        shutil.rmtree(package_dir)
                    self._unpack(dlpath, self.packages_dir)
            except Exception:
                click.secho('Package {0} is not found'.format(
                    self._get_package_name(), fg='red'))
            finally:
                if dlpath:
                    remove(dlpath)
                    self.profile.packages[self.package] = basename(dlpath)
                    self.profile.save()

    def uninstall(self):
        if self.package is not None:
            if isdir(join(self.packages_dir, self.package)):
                click.secho('Uninstall package ', nl=False)
                click.secho(self.package, fg='cyan')
                shutil.rmtree(join(self.packages_dir, self.package))
            else:
                click.secho('Package {0} is not installed'.format(
                    self.package), fg='yellow')
            self.profile.remove(self.package)
            self.profile.save()

    def _get_platform(self):
        return util.get_systype()

    def _get_download_url(self):
        raise NotImplementedError

    def _get_package_name(self):
        raise NotImplementedError

    def _download(self, url, sha1=None):
        fd = FileDownloader(url, self.packages_dir)
        if self.profile.check_version(self.package, basename(fd.get_filepath())):
            click.secho('Download ' + basename(fd.get_filepath()))
            fd.start()
            fd.verify(sha1)
            return fd.get_filepath()
        else:
            click.secho('Package {0} is already the newest version'.format(
                self.package), fg='green')
            return None

    def _unpack(self, pkgpath, pkgdir):
        fu = FileUnpacker(pkgpath, pkgdir)
        return fu.start()
