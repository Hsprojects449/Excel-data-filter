# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# Collect all data from packages that might have hidden imports
datas = []
binaries = []
hiddenimports = []

# Collect PyQt6 data
pyqt6_datas, pyqt6_binaries, pyqt6_hiddenimports = collect_all('PyQt6')
datas.extend(pyqt6_datas)
binaries.extend(pyqt6_binaries)
hiddenimports.extend(pyqt6_hiddenimports)

# Collect polars and other data analysis libraries
polars_datas, polars_binaries, polars_hiddenimports = collect_all('polars')
datas.extend(polars_datas)
binaries.extend(polars_binaries)
hiddenimports.extend(polars_hiddenimports)

# Collect fastexcel (used by polars for Excel reading)
fastexcel_datas, fastexcel_binaries, fastexcel_hiddenimports = collect_all('fastexcel')
datas.extend(fastexcel_datas)
binaries.extend(fastexcel_binaries)
hiddenimports.extend(fastexcel_hiddenimports)

# Collect xlsxwriter (for Excel export functionality)
xlsxwriter_datas, xlsxwriter_binaries, xlsxwriter_hiddenimports = collect_all('xlsxwriter')
datas.extend(xlsxwriter_datas)
binaries.extend(xlsxwriter_binaries)
hiddenimports.extend(xlsxwriter_hiddenimports)

# Collect openpyxl (for Excel metadata and compatibility)
openpyxl_datas, openpyxl_binaries, openpyxl_hiddenimports = collect_all('openpyxl')
datas.extend(openpyxl_datas)
binaries.extend(openpyxl_binaries)
hiddenimports.extend(openpyxl_hiddenimports)

# Additional hidden imports for Excel processing
hiddenimports.extend([
    'polars',
    'polars.io',
    'polars.io.csv',
    'fastexcel',
    'openpyxl',
    'openpyxl.styles',
    'openpyxl.utils',
    'xlsxwriter',
    'xlsxwriter.workbook',
    'xlsxwriter.worksheet', 
    'xlsxwriter.format',
    'loguru',
    'pathlib',
    'tempfile',
    'shutil',
    'json',
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip'
])

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Excel_Data_Filter_Pro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have an icon
)