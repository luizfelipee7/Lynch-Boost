# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path.cwd()


def data_tree(source, destination):
    source_root = ROOT / source
    entries = []
    for path in source_root.rglob("*"):
        if path.is_file():
            target_dir = Path(destination) / path.relative_to(source_root).parent
            entries.append((str(path), str(target_dir)))
    return entries


datas = [
    (str(ROOT / "config.json"), "."),
    *data_tree("assets", "assets"),
    *data_tree("dados", "dados"),
    *data_tree("scripts/windows_tweaks", "scripts/windows_tweaks"),
    *data_tree("scripts/games", "scripts/games"),
    *data_tree("scripts/app.exe", "scripts/app.exe"),
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
