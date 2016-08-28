# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2

from os import chmod
from os.path import join, splitext
from tarfile import open as tarfile_open
from time import mktime
from zipfile import ZipFile

import click

from apio import util


class UnsupportedArchiveType(util.ApioException):

    MESSAGE = "Can not unpack file '{0}'"


class ArchiveBase(object):

    def __init__(self, arhfileobj):
        self._afo = arhfileobj

    def get_items(self):  # pragma: no cover
        raise NotImplementedError()

    def extract_item(self, item, dest_dir):
        if hasattr(item, 'filename') and \
           item.filename.endswith('.gitignore'):
            return
        self._afo.extract(item, dest_dir)
        self.after_extract(item, dest_dir)

    def after_extract(self, item, dest_dir):
        pass


class TARArchive(ArchiveBase):

    def __init__(self, archpath):
        ArchiveBase.__init__(self, tarfile_open(archpath))

    def get_items(self):
        return self._afo.getmembers()


class ZIPArchive(ArchiveBase):

    def __init__(self, archpath):
        ArchiveBase.__init__(self, ZipFile(archpath))

    @staticmethod
    def preserve_permissions(item, dest_dir):
        attrs = item.external_attr >> 16
        if attrs:
            chmod(join(dest_dir, item.filename), attrs)

    @staticmethod
    def preserve_mtime(item, dest_dir):
        util.change_filemtime(
            join(dest_dir, item.filename),
            mktime(tuple(list(item.date_time) + [0] * 3))
        )

    def get_items(self):
        return self._afo.infolist()

    def after_extract(self, item, dest_dir):
        self.preserve_permissions(item, dest_dir)
        self.preserve_mtime(item, dest_dir)


class FileUnpacker(object):

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
        with click.progressbar(self._unpacker.get_items(),
                               label="Unpacking") as pb:
            for item in pb:
                self._unpacker.extract_item(item, self._dest_dir)
        return True
