# -*- coding: utf-8 -*-

import json
import shutil
import urllib2
from os import makedirs, rename, remove
from os.path import isdir, isfile, join, basename, splitext

from downloader import FileDownloader
from unpacker import FileUnpacker


class Installer(object):

    def __init__(self, package_dir):
        self._get_url = {
            'toolchain-icestorm': self.get_latest_icestorm,
            'tool-scons': self.get_latest_scons
        }
        self._package_dir = package_dir

    def install(self, tool, mv=False):
        if tool in self._get_url:
            if not isdir(self._package_dir):
                makedirs(self._package_dir)
            assert isdir(self._package_dir)
            url = self._get_url[tool]()
            if isdir(join(self._package_dir, tool)):
                shutil.rmtree(join(self._package_dir, tool))
            try:
                dlpath = self.download(url, self._package_dir)
                assert isfile(dlpath)
                self.unpack(dlpath, self._package_dir)
            finally:
                if dlpath:
                    remove(dlpath)
                name = splitext(splitext(basename(dlpath))[0])[0]
                if mv:
                    rename(join(self._package_dir, name),
                           join(self._package_dir, tool))

    def get_latest_icestorm(self):
        releases_url = 'https://api.github.com/repos/bqlabs/toolchain-icestorm/releases/latest'
        response = urllib2.urlopen(releases_url)
        packages = json.loads(response.read())
        return packages['assets'][0]['browser_download_url']

    def get_latest_scons(self):
        return 'http://sourceforge.net/projects/scons/files/scons/2.4.1/scons-2.4.1.tar.gz'

    def download(self, url, dest_dir, sha1=None):
        fd = FileDownloader(url, dest_dir)
        fd.start()
        fd.verify(sha1)
        return fd.get_filepath()

    def unpack(self, pkgpath, dest_dir):
        fu = FileUnpacker(pkgpath, dest_dir)
        return fu.start()
