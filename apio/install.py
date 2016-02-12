# -*- coding: utf-8 -*-

import json
import shutil
import urllib2
from os import makedirs, rename, remove
from os.path import isdir, isfile, join, basename, splitext

from profile import Profile
from downloader import FileDownloader
from unpacker import FileUnpacker


class Installer(object):

    def __init__(self, package_dir):
        self._get_url = {
            'toolchain-icestorm': self.get_latest_icestorm,
            'tool-scons': self.get_latest_scons
        }
        self._package_dir = package_dir
        self._profile = Profile()
        self._profile.load()

    def install(self, tool, move=False):
        if tool in self._get_url:
            print('Install ' + tool)
            if not isdir(self._package_dir):
                makedirs(self._package_dir)
            assert isdir(self._package_dir)
            url = self._get_url[tool]()
            try:
                dlpath = None
                dlpath = self.download(tool, url, self._package_dir)
                if dlpath:
                    if isdir(join(self._package_dir, tool)):
                        shutil.rmtree(join(self._package_dir, tool))
                    assert isfile(dlpath)
                    self.unpack(dlpath, self._package_dir)
            finally:
                if dlpath:
                    remove(dlpath)
                    filename = splitext(splitext(basename(dlpath))[0])[0]
                    if move:
                        rename(join(self._package_dir, filename),
                               join(self._package_dir, tool))
                    self._profile.packages[tool] = basename(dlpath)
                    self._profile.save()

    def uninstall(self, tool):
        if tool in self._get_url:
            print('Uninstall package {0}'.format(tool))
            if isdir(join(self._package_dir, tool)):
                shutil.rmtree(join(self._package_dir, tool))
            self._profile.remove(tool)
            self._profile.save()

    def get_latest_icestorm(self):
        releases_url = 'https://api.github.com/repos/bqlabs/toolchain-icestorm/releases/latest'
        response = urllib2.urlopen(releases_url)
        packages = json.loads(response.read())
        return packages['assets'][0]['browser_download_url']

    def get_latest_scons(self):
        return 'http://sourceforge.net/projects/scons/files/scons/2.4.1/scons-2.4.1.tar.gz'

    def download(self, tool, url, dest_dir, sha1=None):
        fd = FileDownloader(url, dest_dir)
        if self._profile.check_version(tool, basename(fd.get_filepath())):
            print('Download ' + basename(fd.get_filepath()))
            fd.start()
            fd.verify(sha1)
            return fd.get_filepath()
        else:
            print('Package {0} is already the newest version'.format(tool))
            return None

    def unpack(self, pkgpath, dest_dir):
        fu = FileUnpacker(pkgpath, dest_dir)
        return fu.start()
