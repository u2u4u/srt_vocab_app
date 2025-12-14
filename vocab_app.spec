# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
import os

block_cipher = None

# Get the path to your project
project_path = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        ('fonts', 'fonts'),  # Include fonts folder
    ],
    hiddenimports=[
        'kivymd',
        'kivymd.uix.screen',
        'kivymd.uix.button',
        'kivymd.uix.dialog',
        'kivymd.uix.textfield',
        'kivymd.uix.boxlayout',
        'kivymd.uix.label',
        'kivymd.uix.card',
        'kivymd.uix.list',
        'kivymd.toast',
        'google.genai',
        'arabic_reshaper',
        'bidi.algorithm',
        'plyer',
    ],
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
    [],
    exclude_binaries=True,
    name='VocabApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,  # Add your icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VocabApp',
)