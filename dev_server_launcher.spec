# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Tcl/Tk library paths from the Python installation
PYTHON_PREFIX = sys.prefix  # e.g. C:/Program Files/WindowsApps/PythonSoftwareFoundation.Python.3.13_3.13.3312.0_x64__qbz5n2kfra8p0
TCL_DIR = os.path.join(PYTHON_PREFIX, "tcl")
TCL8_DIR = os.path.join(TCL_DIR, "tcl8.6")
TK8_DIR = os.path.join(TCL_DIR, "tk8.6")

a = Analysis(
    ['dev_server_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle Tcl/Tk runtime so tkinter works in the frozen exe.
        # MUST use "_tcl_data" and "_tk_data" as destination names to match
        # PyInstaller's pyi_rth__tkinter.py runtime hook (see that hook's source:
        # tcldir = os.path.join(sys._MEIPASS, '_tcl_data')).
        (TCL8_DIR, "_tcl_data"),
        (TK8_DIR, "_tk_data"),
    ],
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.colorchooser",
        "tkinter.commondialog",
        "tkinter.filedialog",
        "tkinter.font",
        "tkinter.messagebox",
        "tkinter.simpledialog",
        "requests",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='dev_server_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
