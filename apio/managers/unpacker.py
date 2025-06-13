"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2

from pathlib import Path
from tarfile import open as tarfile_open
from rich.progress import track
from apio.common.apio_console import console, cerror
from apio.utils import util


class ArchiveBase:
    """DOC: TODO"""

    def __init__(self, arhfileobj, is_tar_file: bool):
        self._afo = arhfileobj
        self._is_tar_file = is_tar_file

    def get_items(self):  # pragma: no cover
        """DOC: TODO"""

        raise NotImplementedError()

    def extract_item(self, item, dest_dir):
        """DOC: TODO"""

        if hasattr(item, "filename") and item.filename.endswith(".gitignore"):
            return
        if self._is_tar_file and util.get_python_ver_tuple() >= (3, 12, 0):
            # -- Special case for avoiding the tar deprecation warning. Search
            # -- 'extraction_filter' in the page
            # -- https://docs.python.org/3/library/tarfile.html
            self._afo.extract(item, dest_dir, filter="fully_trusted")
        else:
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
        ArchiveBase.__init__(self, tarfile_open(archpath), is_tar_file=True)

    def get_items(self):
        return self._afo.getmembers()


# class ZIPArchive(ArchiveBase):
#     """DOC: TODO"""

#     def __init__(self, archpath):
#         # R1732: Consider using 'with' for resource-allocating operations
#         # (consider-using-with)
#         ArchiveBase.__init__(self, ZipFile(archpath), is_tar_file=False)

#     @staticmethod
#     def preserve_permissions(item, dest_dir):
#         """DOC: TODO"""

#         # -- Build the filename
#         file = str(Path(dest_dir) / item.filename)

#         attrs = item.external_attr >> 16
#         if attrs:
#             chmod(file, attrs)

#     def get_items(self):
#         """DOC: TODO"""

#         return self._afo.infolist()

#     def after_extract(self, item, dest_dir):
#         """DOC: TODO"""

#         self.preserve_permissions(item, dest_dir)


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
        if arch_ext in (".tgz"):
            self._unpacker = TARArchive(archpath)

        # -- Zip file
        # elif arch_ext == ".zip":
        #     self._unpacker = ZIPArchive(archpath)

        # -- Fatal error. Unknown extension.
        if not self._unpacker:
            cerror(f"Can not unpack file '{archpath}'")
            raise util.ApioException()

    def start(self) -> bool:
        """Start unpacking the file"""

        # -- Build an array with all the files inside the tarball
        items = self._unpacker.get_items()

        # -- Unpack while displaying a progress bar.
        for i in track(
            range(len(items)),
            description="Unpacking  ",
            console=console(),
        ):
            self._unpacker.extract_item(items[i], self._dest_dir)

        return True
