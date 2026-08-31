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


class TarArchive(ArchiveBase):
    """DOC: TODO"""

    def __init__(self, archpath):
        # pylint: disable=consider-using-with
        self._tar_file = tarfile_open(archpath)
        ArchiveBase.__init__(self, self._tar_file, is_tar_file=True)

    def get_items(self):
        return self._afo.getmembers()

    def close(self) -> None:
        """Close the underlying tar file."""
        self._tar_file.close()
        self._tar_file = None


# class ZIPArchive(ArchiveBase):
#     """DOC: TODO"""

#     def __init__(self, archpath):
#         # R1732: Consider using 'with' for resource-allocating operations
#         # (consider-using-with)
#         ArchiveBase.__init__(self, ZipFile(archpath), is_tar_file=False)

#     @staticmethod

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

    def __init__(self, archive_file_path: Path, dest_dir=Path(".")):
        """Initialize the unpacker object
        * INPUT:
          - archpath: filename with path to uncompress
          - des_dir: Destination folder
        """

        self._archive_file_path = archive_file_path
        self._dest_dir = dest_dir
        self._unpacker = None

        # -- Get the file extension
        # archive_ext = archive_file_path.suffix

        # -- Select the unpacker... according to the file extension
        # -- tar zip file
        # if archive_ext in (".tgz"):
        #     self._unpacker = TarArchive(archive_file_path)

        # -- Zip file
        # elif arch_ext == ".zip":
        #     self._unpacker = ZIPArchive(archpath)

        # -- Fatal error. Unknown extension.
        # if not self._unpacker:
        #     cerror(f"Can not unpack file '{archive_file_path}'")
        #     raise util.ApioException()

    def unpack(self) -> bool:
        """Start unpacking the file"""

        # -- Get the file extension
        archive_ext = self._archive_file_path.suffix

        # -- Select the unpacker... according to the file extension
        # -- tar zip file
        if archive_ext in (".tgz"):
            unpacker = TarArchive(self._archive_file_path)
        else:
            cerror(f"Can not unpack file '{self._archive_file_path}'")
            raise util.ApioException()

        try:
            # -- Zip file
            # elif arch_ext == ".zip":
            #     self._unpacker = ZIPArchive(archpath)

            # -- Fatal error. Unknown extension.
            # if not self._unpacker:
            #     cerror(f"Can not unpack file '{archive_file_path}'")
            #     raise util.ApioException()

            # -- Build an array with all the files inside the tarball
            # if self._unpacker is not None:
            items = unpacker.get_items()
            # else:
            #     items = []

            # -- Unpack while displaying a progress bar.
            for i in track(
                range(len(items)),
                description="Unpacking  ",
                console=console(),
            ):
                # if self._unpacker is not None:
                unpacker.extract_item(items[i], self._dest_dir)

        finally:
            unpacker.close()
        # unpacker = None

        return True
