# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('hydrology_engine', 'hydrology_engine'),
        ('insurance_engine', 'insurance_engine'),
        ('generation_translator', 'generation_translator'),
        ('data_pipeline', 'data_pipeline'),
        ('validation_suite', 'validation_suite'),
        ('nepal_adapter', 'nepal_adapter'),
        ('gui', 'gui'),
    ],
    hiddenimports=[
        'scipy.special._ufuncs_cxx',
        'scipy.linalg.cython_blas',
        'scipy.linalg.cython_lapack',
        'sklearn.utils._cython_blas',
        'pandas._libs.tslibs.timedeltas',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HydroInsure',
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
    icon=['assets/icon.ico'],
)
