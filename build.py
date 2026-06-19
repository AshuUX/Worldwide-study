import PyInstaller.__main__
import os
import sys

# For onefile build where data should be EXTERNAL:
# We do NOT add data to --add-data if we want it to stay in the folder.
# But we must ensure the app knows where to look.

PyInstaller.__main__.run([
    'app.py',
    '--onefile',
    '--windowed',
    '--name=HydroInsure',
    '--icon=assets/icon.ico',
    # We add necessary code folders
    '--add-data=hydrology_engine:hydrology_engine',
    '--add-data=insurance_engine:insurance_engine',
    '--add-data=generation_translator:generation_translator',
    '--add-data=data_pipeline:data_pipeline',
    '--add-data=validation_suite:validation_suite',
    '--add-data=nepal_adapter:nepal_adapter',
    '--add-data=gui:gui',
    '--hidden-import=scipy.special._ufuncs_cxx',
    '--hidden-import=scipy.linalg.cython_blas',
    '--hidden-import=scipy.linalg.cython_lapack',
    '--hidden-import=sklearn.utils._cython_blas',
    '--hidden-import=pandas._libs.tslibs.timedeltas',
    '--collect-all=scipy',
    '--collect-all=sklearn',
])
