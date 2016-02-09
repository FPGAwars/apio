# -*- coding: utf-8 -*-

import json
import urllib2
from os import makedirs, remove
from os.path import isdir, isfile, join, expanduser

from downloader import FileDownloader
from unpacker import FileUnpacker


class Installer(object):

    def __init__(self):
        self._package_dir = join(expanduser("~"), '.platformio/packages/')

    def install(self):
        try:
            if not isdir(self._package_dir):
                makedirs(self._package_dir)
            assert isdir(self._package_dir)
            url = self.get_url()
            dlpath = self.download(url, self._package_dir)
            assert isfile(dlpath)
            self.unpack(dlpath, self._package_dir)
            remove(dlpath)

        except Exception as e:
            print('Error: ' + str(e))

    def get_url(self):
        releases_url = 'https://api.github.com/repos/bqlabs/toolchain-icestorm/releases/latest'
        response = urllib2.urlopen(releases_url)
        packages = json.loads(response.read())
        return packages['assets'][0]['browser_download_url']

    def download(self, url, dest_dir, sha1=None):
        fd = FileDownloader(url, dest_dir)
        fd.start()
        fd.verify(sha1)
        return fd.get_filepath()

    def unpack(self, pkgpath, dest_dir):
        fu = FileUnpacker(pkgpath, dest_dir)
        return fu.start()
