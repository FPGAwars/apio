"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

from os import chmod
from pathlib import Path
from tarfile import open as tarfile_open
from zipfile import ZipFile
import click
from apio import util


class ArchiveBase:
    """DOC: TODO"""

    def __init__(self, arhfileobj):
        self._afo = arhfileobj

    def get_items(self):  # pragma: no cover
        """DOC: TODO"""

        raise NotImplementedError()

    def extract_item(self, item, dest_dir):
        """DOC: TODO"""

        if hasattr(item, "filename") and item.filename.endswith(".gitignore"):
            return
        self._afo.extract(item, dest_dir)
        self.after_extract(item, dest_dir)

    def after_extract(self, item, dest_dir):
        """DOC: TODO"""


class TARArchive(ArchiveBase):
    """DOC: TODO"""

    def __init__(self, archpath):
        # R1732: Consider using 'with' for resource-allocating operations
        # (consider-using-with)
        # pylint: disable=R1732
        ArchiveBase.__init__(self, tarfile_open(archpath))

    def get_items(self):
        return self._afo.getmembers()


class ZIPArchive(ArchiveBase):
    """DOC: TODO"""

    def __init__(self, archpath):
        # R1732: Consider using 'with' for resource-allocating operations
        # (consider-using-with)
        # pylint: disable=R1732
        ArchiveBase.__init__(self, ZipFile(archpath))

    @staticmethod
    def preserve_permissions(item, dest_dir):
        """DOC: TODO"""

        # -- Build the filename
        file = str(Path(dest_dir) / item.filename)

        attrs = item.external_attr >> 16
        if attrs:
            chmod(file, attrs)

    def get_items(self):
        """DOC: TODO"""

        return self._afo.infolist()

    def after_extract(self, item, dest_dir):
        """DOC: TODO"""

        self.preserve_permissions(item, dest_dir)


# R0903: Too few public methods (1/2) (too-few-public-methods)
# pylint: disable=R0903
class FileUnpacker:
    """Class for unpacking compressed files"""

    def __init__(self, archpath: Path, dest_dir=Path(".")):
        """Initialize the unpacker object
        * INPUT:
          - archpath: filename with path to uncompress
          - des_dir: Destination folder
        """

        self._archpath = archpath
        self._dest_dir = dest_dir
        self._unpacker = None

        # -- Get the file extension
        arch_ext = archpath.suffix

        # -- Select the unpacker... according to the file extension
        # -- tar zip file
        if arch_ext in (".gz", ".bz2"):
            self._unpacker = TARArchive(archpath)

        # -- Zip file
        elif arch_ext == ".zip":
            self._unpacker = ZIPArchive(archpath)

        # -- Archive type not known!! Raise an exception!
        if not self._unpacker:
            click.secho(f"Can not unpack file '{archpath}'")
            raise util.ApioException()

    def start(self) -> bool:
        """Start unpacking the file"""

        # -- Build an array with all the files inside the tarball
        items = self._unpacker.get_items()

        # -- Progress bar...
        with click.progressbar(
            items,
            length=len(items),
            label=click.style("Unpacking..", fg="yellow"),
            fill_char=click.style("█", fg="blue"),
            empty_char=click.style("░", fg="blue"),
        ) as pbar:

            # -- Go though all the files in the archive...
            for item in pbar:

                # -- Extract the file!
                self._unpacker.extract_item(item, self._dest_dir)

        return True
