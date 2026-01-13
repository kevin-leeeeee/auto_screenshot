# -*- mode: python ; coding: utf-8 -*-
# AutoFlow Control Center - One-Directory Build Configuration
# Optimized for PyWebView compatibility and reduced package size

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # React frontend build output
        ('autoflow-control-center/dist', 'autoflow-control-center/dist'),
    ],
    hiddenimports=[
        # PyWebView critical imports (Windows backends)
        'engineio.async_drivers.threading',
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        'webview.platforms.edgehtml',
        'webview.platforms.mshtml',
        
        # pythonnet (required for PyWebView on Windows)
        'clr',
        'clr_loader',
        'pythonnet',
        'System',
        'System.Windows.Forms',
        'System.Threading',
        'System.Drawing',
        
        # Flask and web server dependencies
        'flask',
        'flask.json',
        'werkzeug',
        'werkzeug.serving',
        'jinja2',
        
        # Excel processing
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.styles',
        
        # Word document generation
        'docx',
        'docx.shared',
        'docx.enum.text',
        
        # Image processing
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageGrab',
        
        # Automation dependencies
        'pyautogui',
        'pyscreeze',
        'pytweening',
        'pymsgbox',
        'pygetwindow',
        
        # HTTP requests (for update check)
        'requests',
        'urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Data Science Libraries (not needed)
        'pandas', 'numpy', 'matplotlib', 'scipy',
        'scikit-learn', 'scikit-image', 'seaborn',
        'statsmodels', 'xarray', 'tables', 'sympy',
        'PyWavelets', 'patsy', 'numexpr', 'bottleneck',
        
        # Web Scraping (external scripts handle this)
        'scrapy', 'playwright', 'selenium', 'w3lib',
        'beautifulsoup4', 'lxml',
        
        # Development Tools
        'IPython', 'notebook', 'jupyter', 'jupyterlab',
        'spyder', 'sphinx', 'pytest', 'black', 'pylint',
        'mypy', 'flake8', 'coverage',
        
        # GUI Frameworks (only using PyWebView)
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 
        'qtconsole', 'QDarkStyle', 'QtAwesome',
        'wx', 'wxPython',
        
        # Web Frameworks (only using Flask)
        'django', 'fastapi', 'tornado', 'aiohttp',
        'streamlit', 'dash', 'panel', 'holoviews',
        'bokeh', 'altair', 'plotly',
        
        # Cloud/AWS
        'boto3', 's3fs', 'botocore', 'aiobotocore',
        
        # Large/Unnecessary Libraries
        'twisted', 'xlwings', 'numba', 'cython',
        'tensorflow', 'torch', 'keras',
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
    [],
    exclude_binaries=True,
    name='AutoFlow_Control_Center_v2.1.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression
    console=True,  # Keep console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,  # Enable UPX for binaries
    upx_exclude=[
        # Exclude critical DLLs from UPX compression to avoid corruption
        'vcruntime*.dll',
        'python*.dll',
        'pythonnet.dll',
        'clr.pyd',
        'System.*.dll',
        # PyWebView related
        'webview.*.dll',
        # Image processing
        'PIL.*.pyd',
        '_imaging.pyd',
        # Avoid antivirus false positives
        'api-ms-win-*.dll',
    ],
    name='AutoFlow_Control_Center_v2.1.0',
)
