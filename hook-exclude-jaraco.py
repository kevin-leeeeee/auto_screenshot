# PyInstaller runtime hook to exclude jaraco and related packages
import sys

# Block jaraco and related imports
blocked_modules = [
    'jaraco',
    'jaraco.text',
    'jaraco.functools',
    'jaraco.context',
    'jaraco.classes',
    'importlib_resources',
    'importlib_metadata',
]

for module in blocked_modules:
    if module in sys.modules:
        del sys.modules[module]
    sys.modules[module] = None
