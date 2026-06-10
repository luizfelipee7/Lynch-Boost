# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.building.datastruct import Tree


ROOT = Path.cwd()

datas = [
    ("config.json", "."),
    Tree("assets", prefix="assets"),
    Tree("dados", prefix="dados"),
    Tree("scripts/windows_tweaks", prefix="scripts/windows_tweaks"),
    Tree("scripts/games", prefix="scripts/games"),
    Tree("scripts/app.exe", prefix="scripts/app.exe"),
]

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name="LynchBoost",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/logo-ico.ico",
    manifest="packaging/LynchBoost.exe.manifest",
)
