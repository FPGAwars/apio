import os
import click
import shutil
import glob

from os.path import join, isdir, dirname

from .. import util


class PiofpgaInstaller(object):
    """Support for FPGA in platformio(pio) plug-in installer"""

    def install(self):
        click.secho("Installing FPGA support for platformio...")
        pio_dir = os.path.join(dirname(__file__), 'platformio')

        # -- Source dirs
        board_dir = os.path.join(pio_dir, 'boards')
        builder_dir = os.path.join(pio_dir, 'builder', 'scripts')
        platform_dir = os.path.join(pio_dir, 'platforms')

        # -- Dest dirs
        dest_dir = util.get_home_dir()
        board_dest_dir = join(dest_dir, 'boards')
        platform_dest_dir = join(dest_dir, 'platforms')

        # -- Install board files
        self._copy_files(src=board_dir, dest=board_dest_dir)

        # -- Install platform files
        self._copy_files(src=platform_dir, dest=platform_dest_dir)

        # -- Install build script
        builder_files = glob.glob(join(builder_dir, '*'))
        for f in builder_files:
            path, name = os.path.split(f)
            name, ext = os.path.splitext(name)
            if not self._is_pyc(f):
                shutil.copy(f, join(platform_dest_dir, name + '-builder.py'))

        click.secho("\nNow execute the following command:")
        click.secho("")
        click.secho("  pio platforms install lattice_ice40", fg='green')

    def _copy_files(self, src, dest):
        """Copy files from src to dest folder. Files .pyc are not copied"""

        # -- Check for the dest dir
        if isdir(dest):

            # -- It exists
            board_files = glob.glob(join(src, '*'))
            for f in board_files:
                if not self._is_pyc(f):
                    shutil.copy(f, dest)
                else:
                    click.secho("Ignorig {}".format(f), fg='yellow')
        else:
            # -- dest directory does not exist
            shutil.copytree(src, dest)

    def _is_pyc(self, filename):
        """return True if it is a .pyc file"""

        name, ext = os.path.splitext(filename)
        return ext.upper() == ".PYC"
