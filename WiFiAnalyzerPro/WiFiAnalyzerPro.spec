# -*- mode: python ; coding: utf-8 -*-
"""
WiFi Analyzer Pro - PyInstaller Specification
Configured for Windows standalone windowed GUI build without any console window (console=False).
Includes embedded icons, stylesheets, and portable runtime binaries.
"""

import sys
import os
from pathlib import Path

block_cipher = None

SPEC_DIR = os.path.abspath(os.path.dirname('__file__'))

# Bundled data assets
datas = [
    ('assets', 'assets'),
]

# Binaries: check for ICU libraries to guarantee compatibility across all Windows builds
binaries = []
windir = os.environ.get('WINDIR', 'C:\\windows')
for dll in ['icuuc.dll', 'icuuc74.dll', 'icuin.dll', 'icudt.dll', 'icudt74.dll']:
    dll_path = os.path.join(windir, 'system32', dll)
    if os.path.exists(dll_path):
        binaries.append((dll_path, '.'))

# Hidden imports to ensure complete bundle integrity
hiddenimports = [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'app',
    'app.models',
    'app.scanner',
    'app.parser',
    'app.main_window',
    'app.widgets',
    'app.widgets.dashboard_cards',
    'app.widgets.networks_table',
    'app.widgets.signal_chart',
    'app.widgets.radar',
    'app.widgets.heatmap',
    'app.utils',
    'app.utils.subprocess_utils',
    'app.utils.resources',
    'app.utils.oui_lookup',
    'app.utils.exporter',
]

a = Analysis(
    ['main.py'],
    pathex=[SPEC_DIR],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'test', 'matplotlib', 'numpy', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WiFiAnalyzerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join('assets', 'icons', 'app_icon.ico'),
)
