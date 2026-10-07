# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

ROOT = Path.cwd().resolve()
hiddenimports = collect_submodules("uvicorn")

a = Analysis(
    [str(ROOT / "distribution" / "allen_launcher.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "frontend"), "frontend"),
        (str(ROOT / "data" / "library"), "data/library"),
        (str(ROOT / "config"), "config"),
        (str(ROOT / "VERSION"), "."),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "playwright"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ALLEN",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ALLEN",
)
