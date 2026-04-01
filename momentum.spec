# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

repo_root = Path(SPECPATH)
icon_ico = repo_root / "resources" / "icons" / "momentum.ico"

a = Analysis(
    ["main.py"],
    pathex=[str(repo_root)],
    binaries=[],
    datas=[
        (str(repo_root / "resources" / "icons" / "momentum.png"), "resources/icons"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Momentum",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=str(icon_ico) if icon_ico.exists() else None,
    version=str(repo_root / "packaging" / "windows" / "version_info.txt"),
)

