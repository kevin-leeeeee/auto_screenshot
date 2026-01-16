@echo off
chcp 65001
echo ===================================================
echo   AutoFlow Build Script (Minimalist)
echo ===================================================
echo.

echo [0/5] Cleaning up old builds...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist AutoFlow.spec del /q AutoFlow.spec

echo [1/5] Running PyInstaller...
pyinstaller --noconfirm --onedir --windowed --name "AutoFlow" ^
    --add-data "autoflow/dist;ui" ^
    --add-data "excel;excel" ^
    --add-data "screenshot;screenshot" ^
    --hidden-import webview --hidden-import flask --hidden-import requests ^
    --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageStat --hidden-import PIL.ImageGrab --hidden-import PIL.ImageChops ^
    --hidden-import pyautogui --hidden-import docx --hidden-import pygetwindow ^
    --hidden-import clr_loader --hidden-import clr ^
    --hidden-import tkinter --hidden-import tkinter.filedialog ^
    --exclude-module core ^
    --exclude-module pandas --exclude-module numpy --exclude-module matplotlib --exclude-module scipy ^
    --exclude-module sphinx --exclude-module docutils --exclude-module IPython ^
    --exclude-module PyQt5 --exclude-module PyQt5.QtWebEngine --exclude-module PyQt5.QtWebEngineWidgets --exclude-module PyQt5.QtWebEngineCore ^
    --exclude-module PyQt5.QtNetwork --exclude-module PyQt5.QtNetworkAuth --exclude-module PyQt5.QtQuick ^
    --exclude-module PyQt5.QtQml --exclude-module PyQt5.QtQuickWidgets --exclude-module PyQt5.QtSql ^
    --exclude-module PyQt5.QtTest --exclude-module PyQt5.QtXml --exclude-module PyQt5.QtBluetooth ^
    --exclude-module PyQt5.QtLocation --exclude-module PyQt5.QtMultimedia --exclude-module PyQt5.QtNfc ^
    --exclude-module PyQt5.QtPositioning --exclude-module PyQt5.QtSensors --exclude-module PyQt5.QtSerialPort ^
    --exclude-module PyQt5.QtSvg --exclude-module PyQt5.QtWebChannel --exclude-module PyQt5.QtWebSockets ^
    --exclude-module PySide2 --exclude-module PySide6 ^
    --icon "assets/icon.ico" run.py

if errorlevel 1 (
    echo [ERROR] PyInstaller failed! Retrying without icon...
    pyinstaller --noconfirm --onedir --windowed --name "AutoFlow" ^
        --add-data "autoflow/dist;ui" ^
        --add-data "excel;excel" ^
        --add-data "screenshot;screenshot" ^
        --hidden-import webview --hidden-import flask --hidden-import requests ^
        --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageStat --hidden-import PIL.ImageGrab --hidden-import PIL.ImageChops ^
        --hidden-import pyautogui --hidden-import docx --hidden-import pygetwindow ^
        --hidden-import clr_loader --hidden-import clr ^
        --hidden-import tkinter --hidden-import tkinter.filedialog ^
        --exclude-module core ^
        --exclude-module pandas --exclude-module numpy --exclude-module matplotlib --exclude-module scipy ^
        --exclude-module sphinx --exclude-module docutils --exclude-module IPython ^
        --exclude-module PyQt5 --exclude-module PyQt5.QtWebEngine --exclude-module PyQt5.QtWebEngineWidgets --exclude-module PyQt5.QtWebEngineCore ^
        --exclude-module PyQt5.QtNetwork --exclude-module PyQt5.QtNetworkAuth --exclude-module PyQt5.QtQuick ^
        --exclude-module PyQt5.QtQml --exclude-module PyQt5.QtQuickWidgets --exclude-module PyQt5.QtSql ^
        --exclude-module PyQt5.QtTest --exclude-module PyQt5.QtXml --exclude-module PyQt5.QtBluetooth ^
        --exclude-module PyQt5.QtLocation --exclude-module PyQt5.QtMultimedia --exclude-module PyQt5.QtNfc ^
        --exclude-module PyQt5.QtPositioning --exclude-module PyQt5.QtSensors --exclude-module PyQt5.QtSerialPort ^
        --exclude-module PyQt5.QtSvg --exclude-module PyQt5.QtWebChannel --exclude-module PyQt5.QtWebSockets ^
        --exclude-module PySide2 --exclude-module PySide6 ^
        run.py
)

if errorlevel 1 (
    echo [ERROR] PyInstaller failed again. Exiting.
    pause
    exit /b 1
)

echo [2/5] Copying Core Logic...
xcopy /E /I /Y "core" "dist\AutoFlow\core"
copy /Y "version.txt" "dist\AutoFlow\"

echo [3/5] Creating UI Zip...
powershell -Command "Compress-Archive -Path 'autoflow\dist\*' -DestinationPath 'dist\ui.zip' -Force"

echo [4/5] Creating Full Release Zip...
powershell -Command "Compress-Archive -Path 'dist\AutoFlow' -DestinationPath 'dist\AutoFlow_v3.2.0_Full.zip' -Force"

echo.
echo ===================================================
echo   Build Complete! 
echo   File: dist\AutoFlow_v3.2.0_Full.zip
echo ===================================================
echo.
pause
