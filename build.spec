# -*- mode: python ; coding: utf-8 -*-
# AutoFlow Control Center - One-Directory Build Configuration
# Optimized for PyWebView compatibility and reduced package size

block_cipher = None

# ========== 讀取版本號 ==========
import os
import site
version = "unknown"
if os.path.exists("version.txt"):
    with open("version.txt", "r") as f:
        version = f.read().strip()
app_name = f'AutoFlow_Control_Center_v{version}'

# ========== 找到 pythonnet 路徑 ==========
pythonnet_path = None
for sp in site.getsitepackages():
    potential_path = os.path.join(sp, 'pythonnet')
    if os.path.exists(potential_path):
        pythonnet_path = potential_path
        break

# ========== 準備 binaries 和 datas ==========
binaries_list = []
datas_list = [('autoflow-control-center/dist', 'autoflow-control-center/dist')]

if pythonnet_path:
    runtime_path = os.path.join(pythonnet_path, 'runtime')
    if os.path.exists(runtime_path):
        # 添加所有 runtime DLL
        binaries_list.append((os.path.join(runtime_path, '*.dll'), 'pythonnet/runtime'))
        # 添加整個 runtime 目錄
        datas_list.append((runtime_path, 'pythonnet/runtime'))

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=binaries_list,
    datas=datas_list,
    hiddenimports=[
        # ... (keep all existing imports) ...
        'engineio.async_drivers.threading',
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.edgechromium',
        'webview.platforms.edgehtml',
        'webview.platforms.mshtml',
        'clr',
        'clr_loader',
        'pythonnet',
        'System',
        'System.Windows.Forms',
        'System.Threading',
        'System.Drawing',
        'flask',
        'flask.json',
        'werkzeug',
        'werkzeug.serving',
        'jinja2',
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.styles',
        'docx',
        'docx.shared',
        'docx.enum.text',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageGrab',
        'PIL.ImageChops',
        'PIL.ImageStat',
        'pyautogui',
        'pyscreeze',
        'pytweening',
        'pymsgbox',
        'pygetwindow',
        'requests',
        'urllib3',
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
        'pandas', 'numpy', 'matplotlib', 'scipy',
        'scikit-learn', 'scikit-image', 'seaborn',
        'statsmodels', 'xarray', 'tables', 'sympy',
        'PyWavelets', 'patsy', 'numexpr', 'bottleneck',
        'scrapy', 'playwright', 'selenium', 'w3lib',
        'beautifulsoup4', 'lxml',
        'IPython', 'notebook', 'jupyter', 'jupyterlab',
        'spyder', 'sphinx', 'pytest', 'black', 'pylint',
        'mypy', 'flake8', 'coverage',
        'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 
        'qtconsole', 'QDarkStyle', 'QtAwesome',
        'wx', 'wxPython',
        'django', 'fastapi', 'tornado', 'aiohttp',
        'streamlit', 'dash', 'panel', 'holoviews',
        'bokeh', 'altair', 'plotly',
        'boto3', 's3fs', 'botocore', 'aiobotocore',
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
    name=app_name,
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
        'vcruntime*.dll',
        'python*.dll',
        'pythonnet.dll',
        'clr.pyd',
        'System.*.dll',
        'webview.*.dll',
        'PIL.*.pyd',
        '_imaging.pyd',
        'api-ms-win-*.dll',
    ],
    name=app_name,
)
