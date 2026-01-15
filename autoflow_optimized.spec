# -*- mode: python ; coding: utf-8 -*-
# Fixed spec for PyWebView compatibility

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('autoflow-control-center/dist', 'autoflow-control-center/dist'),
    ],
    hiddenimports=[
        # PyWebView critical imports
        'engineio.async_drivers.threading',
        'webview',
        'webview.platforms.winforms',  # Windows backend
        'webview.platforms.edgechromium',  # Edge Chromium backend
        'webview.platforms.edgehtml',  # Edge HTML backend (fallback)
        'webview.platforms.mshtml',  # MSHTML backend (fallback)
        
        # pythonnet (required for PyWebView on Windows)
        'clr',
        'clr_loader',
        'pythonnet',
        'System',
        'System.Windows.Forms',
        'System.Threading',
        'System.Drawing',
        
        # Flask and dependencies
        'flask',
        'flask.json',
        'werkzeug',
        'werkzeug.serving',
        'jinja2',
        
        # Other dependencies
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.styles',
        'docx',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageGrab',
        'PIL.ImageChops',
        'PIL.ImageStat',
        
        # PyAutoGUI dependencies
        'pyautogui',
        'pyscreeze',
        'pytweening',
        'pymsgbox',
        'pygetwindow',
        
        # Standard library submodules often missed
        'logging.handlers',
        'dataclasses',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'uuid',
        'ctypes',
        'ctypes.wintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Data Science Libraries
        'pandas', 'numpy', 'matplotlib', 'scipy',
        'scikit-learn', 'scikit-image', 'seaborn',
        'statsmodels', 'xarray', 'tables', 'sympy',
        'PyWavelets', 'patsy',
        
        # Web Scraping
        'scrapy', 'playwright', 'selenium', 'w3lib',
        
        # Development Tools
        'IPython', 'notebook', 'jupyter',
        'spyder', 'sphinx', 'pytest', 'black',
        
        # GUI Frameworks (keep only what we need)
        'PyQt5', 'PySide2', 'PySide6', 'qtconsole',
        'QDarkStyle', 'QtAwesome',
        
        # Web Frameworks
        'streamlit', 'dash', 'panel', 'holoviews',
        'bokeh', 'altair', 'plotly',
        
        # AWS/Cloud
        'boto3', 's3fs', 'botocore',
        
        # Large Libraries
        'twisted', 'xlwings', 'numba',
    ],
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
    name='AutoFlow_Control_Center_v2.2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)
