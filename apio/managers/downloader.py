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

from math import ceil
import requests
import click
from apio import util

# -- Timeout for geting a reponse from the server when downloading
# -- a file (in seconds)
TIMEOUT = 5


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
        self._request = requests.get(url, stream=True, timeout=TIMEOUT)

        # -- Raise an exception in case of download error...
        if self._request.status_code != 200:
            click.secho(
                f"Got an unrecognized status code: {self._request.status_code}"
                f"\nWhen downloading {url}",
                fg="red",
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
            chunks = int(ceil(self.get_size() / float(self.CHUNK_SIZE)))

            # -- Download the file. Show a progress bar
            with click.progressbar(
                length=chunks,
                label=click.style("Downloading", fg="yellow"),
                fill_char=click.style("█", fg="blue"),
                empty_char=click.style("░", fg="blue"),
            ) as pbar:
                for _ in pbar:

                    # -- Receive next block of bytes
                    file.write(next(itercontent))

        # -- Download done!
        self._request.close()

    def __del__(self):
        """Close any pending request"""

        if self._request:
            self._request.close()
