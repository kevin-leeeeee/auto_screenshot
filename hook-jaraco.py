# PyInstaller hook to completely block jaraco imports
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Return empty lists to prevent jaraco from being included
hiddenimports = []
datas = []
binaries = []

# Explicitly exclude all jaraco submodules
excludedimports = [
    'jaraco',
    'jaraco.text',
    'jaraco.functools',
    'jaraco.context',
    'jaraco.classes',
]
