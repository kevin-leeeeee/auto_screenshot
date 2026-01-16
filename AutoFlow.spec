# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('autoflow/dist', 'ui'), ('excel', 'excel'), ('screenshot', 'screenshot')],
    hiddenimports=['webview', 'flask', 'requests', 'PIL', 'PIL.Image', 'PIL.ImageStat', 'PIL.ImageGrab', 'PIL.ImageChops', 'pyautogui', 'docx', 'pygetwindow', 'clr_loader', 'clr', 'tkinter', 'tkinter.filedialog'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['core', 'pandas', 'numpy', 'matplotlib', 'scipy', 'sphinx', 'docutils', 'IPython', 'PyQt5', 'PyQt5.QtWebEngine', 'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebEngineCore', 'PyQt5.QtNetwork', 'PyQt5.QtNetworkAuth', 'PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtQuickWidgets', 'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtXml', 'PyQt5.QtBluetooth', 'PyQt5.QtLocation', 'PyQt5.QtMultimedia', 'PyQt5.QtNfc', 'PyQt5.QtPositioning', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort', 'PyQt5.QtSvg', 'PyQt5.QtWebChannel', 'PyQt5.QtWebSockets', 'PySide2', 'PySide6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoFlow',
)
