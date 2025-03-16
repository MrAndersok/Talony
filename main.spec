# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('times.ttf', '.'),
        ('img.png', '.'),
        ('tickets.db', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    excludes=[
        'reportlab.graphics.barcode.usps4s',
        'reportlab.graphics.barcode.code93',
        'reportlab.graphics.barcode.code39'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TalonyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # True якщо потрібно бачити консоль
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TalonyApp'
)

