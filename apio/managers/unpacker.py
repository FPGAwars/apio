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
from os.path import splitext
from tarfile import open as tarfile_open
from time import mktime
from zipfile import ZipFile

import click

from apio import util


class UnsupportedArchiveType(util.ApioException):
    """DOC: TODO"""

    MESSAGE = "Can not unpack file '{0}'"


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
        ArchiveBase.__init__(self, tarfile_open(archpath))

    def get_items(self):
        return self._afo.getmembers()


class ZIPArchive(ArchiveBase):
    """DOC: TODO"""

    def __init__(self, archpath):
        ArchiveBase.__init__(self, ZipFile(archpath))

    @staticmethod
    def preserve_permissions(item, dest_dir):
        """DOC: TODO"""

        attrs = item.external_attr >> 16
        if attrs:
            chmod(util.safe_join(dest_dir, item.filename), attrs)

    @staticmethod
    def preserve_mtime(item, dest_dir):
        """DOC: TODO"""

        util.change_filemtime(
            util.safe_join(dest_dir, item.filename),
            mktime(tuple(list(item.date_time) + [0] * 3)),
        )

    def get_items(self):
        """DOC: TODO"""

        return self._afo.infolist()

    def after_extract(self, item, dest_dir):
        """DOC: TODO"""

        self.preserve_permissions(item, dest_dir)
        self.preserve_mtime(item, dest_dir)


class FileUnpacker:
    """DOC: TODO"""

    def __init__(self, archpath, dest_dir="."):
        self._archpath = archpath
        self._dest_dir = dest_dir
        self._unpacker = None

        _, archext = splitext(archpath.lower())
        if archext in (".gz", ".bz2"):
            self._unpacker = TARArchive(archpath)
        elif archext == ".zip":
            self._unpacker = ZIPArchive(archpath)

        if not self._unpacker:
            raise UnsupportedArchiveType(archpath)

    def start(self):
        """DOC: TODO"""

        with click.progressbar(
            self._unpacker.get_items(), label="Unpacking"
        ) as pbar:
            for item in pbar:
                self._unpacker.extract_item(item, self._dest_dir)
        return True
