# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Implement a remote file downloader. Used to fetch packages from github
packages release repositories.
"""

# TODO: capture all the exceptions and return them as method return status.
# Motivation is simplifying the usage.

from math import ceil
import requests
from rich.progress import track
from apio.utils import util
from apio.common.apio_console import cout, console
from apio.common.apio_styles import ERROR

# -- Timeout for getting a response from the server when downloading
# -- a file (in seconds). We had github tests failing with timeout=10
TIMEOUT_SECS = 30


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

        # -- Request the file
        self._request = requests.get(url, stream=True, timeout=TIMEOUT_SECS)

        # -- Raise an exception in case of download error...
        if self._request.status_code != 200:
            cout(
                "Got an unexpected HTTP status code: "
                f"{self._request.status_code}",
                f"When downloading {url}",
                style=ERROR,
            )
            raise util.ApioException()

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
            num_chunks = int(ceil(self.get_size() / float(self.CHUNK_SIZE)))

            # -- Download and write the chunks, while displaying the progress.
            for _ in track(
                range(num_chunks),
                description="Downloading",
                console=console(),
            ):

                file.write(next(itercontent))

            # -- Check that the iterator reached its end. When the end is
            # -- reached, next() returns the default value None.
            assert next(itercontent, None) is None

        # -- Download done!
        self._request.close()

    def __del__(self):
        """Close any pending request"""

        if self._request:
            self._request.close()
