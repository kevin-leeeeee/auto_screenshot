@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  AutoFlow - 分離式元件建置工具                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ========== 讀取版本號 ==========
if not exist "version.txt" (
    echo ❌ 錯誤: 找不到 version.txt
    pause
    exit /b 1
)

set /p VERSION=<version.txt
set /p CORE_VERSION=<core_version.txt
set /p SCRIPTS_VERSION=<scripts_version.txt

echo 📦 版本資訊:
echo    整體版本: v%VERSION%
echo    核心版本: v%CORE_VERSION%
echo    腳本版本: v%SCRIPTS_VERSION%
echo.

REM ========== 詢問要建置哪些元件 ==========
echo 請選擇要建置的元件:
echo   [1] 核心程式 + 外部腳本 (完整建置)
echo   [2] 僅核心程式
echo   [3] 僅外部腳本
echo.

set /p CHOICE=請輸入選項 (1/2/3): 

if "%CHOICE%"=="1" (
    set BUILD_CORE=1
    set BUILD_SCRIPTS=1
    echo.
    echo ✅ 將建置: 核心程式 + 外部腳本
) else if "%CHOICE%"=="2" (
    set BUILD_CORE=1
    set BUILD_SCRIPTS=0
    echo.
    echo ✅ 將建置: 核心程式
) else if "%CHOICE%"=="3" (
    set BUILD_CORE=0
    set BUILD_SCRIPTS=1
    echo.
    echo ✅ 將建置: 外部腳本
) else (
    echo.
    echo ❌ 無效的選項
    pause
    exit /b 1
)

echo.
pause
echo.

REM ========== 建置核心程式 ==========
if "%BUILD_CORE%"=="1" (
    echo [1/4] 建置核心程式...
    echo.
    
    REM 執行完整建置
    call build_release.bat
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ❌ 核心程式建置失敗!
        pause
        exit /b 1
    )
    
    echo.
    echo [2/4] 打包核心程式...
    echo.
    
    REM 建立核心壓縮包 (排除外部腳本目錄)
    set CORE_DIR=dist\AutoFlow_Control_Center_v%VERSION%
    set CORE_ZIP=dist\AutoFlow_Core_v%CORE_VERSION%.zip
    
    REM 刪除舊的核心壓縮包
    if exist "%CORE_ZIP%" del /f /q "%CORE_ZIP%"
    
    REM 打包核心 (exe + _internal 目錄)
    powershell -Command "Compress-Archive -Path '%CORE_DIR%\*.exe', '%CORE_DIR%\_internal' -DestinationPath '%CORE_ZIP%' -CompressionLevel Optimal -Force"
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ 核心程式打包失敗!
        pause
        exit /b 1
    )
    
    REM 顯示檔案大小
    for %%A in ("%CORE_ZIP%") do set CORE_SIZE=%%~zA
    set /a CORE_SIZE_MB=!CORE_SIZE! / 1048576
    
    echo ✅ 核心程式已打包: !CORE_SIZE_MB! MB
    echo.
) else (
    echo [1/4] 跳過核心程式建置
    echo [2/4] 跳過核心程式打包
    echo.
)

REM ========== 打包外部腳本 ==========
if "%BUILD_SCRIPTS%"=="1" (
    echo [3/4] 打包外部腳本...
    echo.
    
    set SCRIPTS_ZIP=dist\Scripts_v%SCRIPTS_VERSION%.zip
    
    REM 刪除舊的腳本壓縮包
    if exist "%SCRIPTS_ZIP%" del /f /q "%SCRIPTS_ZIP%"
    
    REM 打包外部腳本
    powershell -Command "Compress-Archive -Path 'excel_轉換', '截圖腳本' -DestinationPath '%SCRIPTS_ZIP%' -CompressionLevel Optimal -Force"
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ 外部腳本打包失敗!
        pause
        exit /b 1
    )
    
    REM 顯示檔案大小
    for %%A in ("%SCRIPTS_ZIP%") do set SCRIPTS_SIZE=%%~zA
    set /a SCRIPTS_SIZE_MB=!SCRIPTS_SIZE! / 1048576
    
    echo ✅ 外部腳本已打包: !SCRIPTS_SIZE_MB! MB
    echo.
) else (
    echo [3/4] 跳過外部腳本打包
    echo.
)

REM ========== 生成 Manifest ==========
echo [4/4] 生成 manifest.json...
echo.

python generate_manifest.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Manifest 生成失敗!
    pause
    exit /b 1
)

echo.

REM ========== 完成 ==========
echo ╔════════════════════════════════════════════════════════════╗
echo ║  ✅ 元件建置完成!                                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 📦 建置產物:
if "%BUILD_CORE%"=="1" (
    echo    ✅ AutoFlow_Core_v%CORE_VERSION%.zip (!CORE_SIZE_MB! MB)
)
if "%BUILD_SCRIPTS%"=="1" (
    echo    ✅ Scripts_v%SCRIPTS_VERSION%.zip (!SCRIPTS_SIZE_MB! MB)
)
echo    ✅ manifest.json
echo.

echo 💡 下一步:
echo    執行 release_components.bat 發布元件
echo.

pause
