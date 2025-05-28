# -*- mode: python ; coding: utf-8 -*-

# Pyinstaller spec file for apio package generation.

from PyInstaller.utils.hooks import collect_submodules
import apio
import sys
from pathlib import Path

# -- Get the path to the 'apio' dir of the apio package.
apio_dir = Path(sys.modules["apio"].__file__).parent
print(f"{apio_dir=}")

added_files = [
    ( apio_dir / 'resources/*', 'apio/resources' ),
    ( apio_dir / 'scons/SConstruct', 'apio/scons' ),
]

hiddenimports = (
    collect_submodules('SCons') +
    collect_submodules('apio') +
    collect_submodules('usb')
)

# Per https://github.com/orgs/pyinstaller/discussions/9148
excludes = [ 'pkg_resources' ]

a = Analysis(
    [apio_dir / '__main__.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='apio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='apio',
)
