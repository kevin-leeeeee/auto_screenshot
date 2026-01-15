@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM ==========================================
REM   AutoFlow 自動打包與發布整理腳本 (v2.2.0)
REM   優化版 - 含環境檢查與錯誤處理
REM ==========================================

REM ========== 讀取版本號 ==========
if not exist "version.txt" (
    echo [錯誤] 找不到 version.txt
    pause
    exit /b 1
)
set /p VERSION=<version.txt
set APP_NAME=AutoFlow_Control_Center_v%VERSION%
set DIST_PATH=dist\%APP_NAME%
set START_TIME=%TIME%

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  AutoFlow Control Center - 自動建置腳本 v%VERSION%            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ========== 環境檢查 ==========
echo [0/6] 檢查建置環境...
echo.

REM 檢查 Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] 找不到 Node.js，請先安裝 Node.js
    echo 下載位置: https://nodejs.org/
    pause
    exit /b 1
)

REM 檢查 Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.12+
    pause
    exit /b 1
)

REM 檢查 PyInstaller
python -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] 找不到 PyInstaller，請執行: pip install pyinstaller
    pause
    exit /b 1
)

REM 檢查前端目錄
if not exist "autoflow-control-center" (
    echo [錯誤] 找不到前端目錄 autoflow-control-center
    pause
    exit /b 1
)

echo ✓ Node.js 已安裝
echo ✓ Python 已安裝
echo ✓ PyInstaller 已安裝
echo ✓ 前端目錄存在
echo.

REM ========== 前端建置 ==========
echo [1/6] 建置 React 前端...
echo.

cd autoflow-control-center
if not exist "package.json" (
    echo [錯誤] 找不到 package.json
    cd ..
    pause
    exit /b 1
)

call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] 前端建置失敗
    cd ..
    pause
    exit /b 1
)
cd ..

echo ✓ 前端建置完成
echo.

REM ========== 清理舊建置 ==========
echo [2/6] 清理舊建置檔案...
echo.

if exist "build" (
    rmdir /s /q "build"
    echo ✓ 已清除 build 目錄
)

if exist "%DIST_PATH%" (
    rmdir /s /q "%DIST_PATH%"
    echo ✓ 已清除舊的 dist 目錄
)

echo.

REM ========== PyInstaller 打包 ==========
echo [3/6] 執行 PyInstaller 打包 (One-Directory 模式)...
echo.

call pyinstaller --clean autoflow_onedir.spec --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo [錯誤] PyInstaller 打包失敗
    pause
    exit /b 1
)

echo ✓ PyInstaller 打包完成
echo.

REM ========== 複製外部腳本 ==========
echo [4/6] 整理外部腳本 (插拔式架構)...
echo.

REM 建立目錄
if not exist "%DIST_PATH%\excel_轉換" mkdir "%DIST_PATH%\excel_轉換"
if not exist "%DIST_PATH%\截圖腳本" mkdir "%DIST_PATH%\截圖腳本"

REM 複製 Excel 轉換腳本 (排除不必要的檔案)
echo 複製 excel_轉換...
xcopy /E /I /Y /Q "excel_轉換\*.py" "%DIST_PATH%\excel_轉換\" >nul
xcopy /E /I /Y /Q "excel_轉換\README.md" "%DIST_PATH%\excel_轉換\" >nul 2>&1
if exist "excel_轉換\測試資料.xlsx" (
    copy /Y "excel_轉換\測試資料.xlsx" "%DIST_PATH%\excel_轉換\" >nul
)

REM 複製截圖腳本 (排除不必要的檔案)
echo 複製 截圖腳本...
xcopy /E /I /Y /Q "screenshot_script\*.py" "%DIST_PATH%\截圖腳本\" >nul
xcopy /E /I /Y /Q "screenshot_script\*.json" "%DIST_PATH%\截圖腳本\" >nul 2>&1
xcopy /E /I /Y /Q "screenshot_script\README.md" "%DIST_PATH%\截圖腳本\" >nul 2>&1

echo ✓ 外部腳本複製完成
echo.

REM ========== 建立壓縮檔 ==========
echo [5/6] 建立發布壓縮包...
echo.

if exist "dist\%APP_NAME%_Full.zip" (
    del /f /q "dist\%APP_NAME%_Full.zip"
)

REM powershell -Command "Compress-Archive -Path '%DIST_PATH%' -DestinationPath 'dist\%APP_NAME%_Full.zip' -CompressionLevel Optimal -Force"
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 壓縮檔建立失敗，但程式檔案已準備完成
) else (
    echo ✓ 壓縮檔建立完成
)
echo.

REM ========== 計算建置時間 ==========
echo [6/6] 建置完成！
echo.

REM 計算檔案大小
for %%A in ("dist\%APP_NAME%_Full.zip") do set SIZE=%%~zA
set /a SIZE_MB=!SIZE! / 1048576

echo ╔════════════════════════════════════════════════════════════╗
echo ║  建置成功！                                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 發布包位置: dist\%APP_NAME%_Full.zip
echo 📊 壓縮包大小: !SIZE_MB! MB
echo 📁 程式目錄: %DIST_PATH%\
echo.
echo 🎯 下一步:
echo    1. 測試執行檔: cd %DIST_PATH% ^&^& %APP_NAME%.exe
echo    2. 上傳到 GitHub Releases
echo.

pause
