# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_all

# Collect all data for export testing
datas = []
binaries = []
hiddenimports = []

# Collect xlsxwriter
xlsxwriter_datas, xlsxwriter_binaries, xlsxwriter_hiddenimports = collect_all('xlsxwriter')
datas.extend(xlsxwriter_datas)
binaries.extend(xlsxwriter_binaries)
hiddenimports.extend(xlsxwriter_hiddenimports)

# Collect polars
polars_datas, polars_binaries, polars_hiddenimports = collect_all('polars')
datas.extend(polars_datas)
binaries.extend(polars_binaries)
hiddenimports.extend(polars_hiddenimports)

# Collect fastexcel
fastexcel_datas, fastexcel_binaries, fastexcel_hiddenimports = collect_all('fastexcel')
datas.extend(fastexcel_datas)
binaries.extend(fastexcel_binaries)
hiddenimports.extend(fastexcel_hiddenimports)

# Additional hidden imports
hiddenimports.extend([
    'xlsxwriter',
    'xlsxwriter.workbook',
    'xlsxwriter.worksheet',
    'polars',
    'fastexcel',
    'tempfile',
    'pathlib'
])

a = Analysis(
    ['test_export_minimal.py'],
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
    name='test_export_minimal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console for testing
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)