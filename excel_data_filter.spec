# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from PyInstaller.utils.hooks import collect_all

# Collect only essential data from packages (lazy loading for faster startup)
datas = []
binaries = []
hiddenimports = []

# Only collect binaries and essential data, skip unnecessary package data
# This significantly reduces startup time by avoiding full collection
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')
binaries.extend(pyqt6_binaries)
hiddenimports.extend(pyqt6_hiddenimports)

# Polars - only binaries needed
polars_datas, polars_binaries, polars_hiddenimports = collect_all('polars')
binaries.extend(polars_binaries)
hiddenimports.extend(polars_hiddenimports)

# Fastexcel - minimal collection
fastexcel_datas, fastexcel_binaries, fastexcel_hiddenimports = collect_all('fastexcel')
binaries.extend(fastexcel_binaries)
hiddenimports.extend(fastexcel_hiddenimports)

# Include local UI assets (icons/images) so they are available at runtime
assets_root = os.path.join('ui', 'assets')
if os.path.isdir(assets_root):
    for f in glob.glob(os.path.join(assets_root, '**', '*'), recursive=True):
        if os.path.isfile(f):
            rel_dir = os.path.dirname(os.path.relpath(f, start='.'))
            datas.append((f, rel_dir))

# Additional hidden imports for Excel processing (minimal list)
hiddenimports.extend([
    'polars',
    'fastexcel',
    'xlsxwriter',
    'loguru',
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
])

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],  # Add startup optimization hook
    excludes=[
        # Exclude unnecessary modules to reduce size and startup time
        'matplotlib', 'numpy.testing', 'scipy', 'pandas.tests',
        'pytest', 'unittest', 'doctest', 'pdb', 'tkinter',
        'IPython', 'notebook', 'jupyter', 'PIL.ImageQt',
        'polars.testing', 'polars.testing.parametric',  # Exclude testing modules
        'hypothesis',  # Testing library not needed
    ],
    noarchive=False,
    optimize=2,  # Enable Python bytecode optimization
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='XLS_Filter_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        # Exclude large DLLs from UPX compression for faster startup
        'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll',
        'python3.dll', 'python311.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/assets/vsn_logo.ico',  # Embedded taskbar/window icon
)