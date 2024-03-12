# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""TODO"""
[]
from math import ceil

import requests
import click

from apio import util


class FDUnrecognizedStatusCode(util.ApioException):
    """TODO"""

    MESSAGE = "Got an unrecognized status code '{0}' when downloaded {1}"


class FileDownloader:
    """Class for downloading files"""

    CHUNK_SIZE = 1024

    def __init__(self, url: str, dest_dir=None):
        """Initialize a FileDownloader object
        * INPUTs:
          * url: File to download (full url)
                 (Ex. 'https://github.com/FPGAwars/apio-examples/
                       releases/download/0.0.35/apio-examples-0.0.35.zip')
          * dest_dir: Destination folder (where to download the file)
        """

        # -- Store the url
        self._url = url

        # -- Get the file from the url
        # -- Ex: 'apio-examples-0.0.35.zip'
        self.fname = url.split("/")[-1]

        # -- Build the destination path
        self.destination = self.fname
        if dest_dir:

            # -- Add the path
            self.destination = dest_dir / self.fname

        self._progressbar = None
        self._request = None

        # -- Request the file
        self._request = requests.get(url, stream=True, timeout=5)

        # -- Raise an exception in case of download error...
        if self._request.status_code != 200:
            raise FDUnrecognizedStatusCode(self._request.status_code, url)

    def set_destination(self, destination):
        """TODO"""

        self.destination = destination

    def get_filepath(self):
        """TODO"""
        return self.destination

    def get_size(self) -> int:
        """Return the size (in bytes) of the latest bytes block received"""

        return int(self._request.headers["content-length"])

    def start(self):
        """Start the downloading of the file"""

        # -- Download iterator
        itercontent = self._request.iter_content(chunk_size=self.CHUNK_SIZE)

        # -- Open destination file, for writing bytes
        with open(self.destination, "wb") as file:

            # -- Get the file length in Kbytes
            chunks = int(ceil(self.get_size() / float(self.CHUNK_SIZE)))

            # -- Download the file. Show a progress bar
            with click.progressbar(length=chunks, label="Downloading") as pbar:
                for _ in pbar:

                    # -- Receive next block of bytes
                    file.write(next(itercontent))

        # -- Download done!
        self._request.close()

    def __del__(self):
        if self._request:
            self._request.close()
