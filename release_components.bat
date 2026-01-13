@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  AutoFlow - 分離式元件發布工具                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ========== 檢查 GitHub CLI ==========
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 錯誤: 找不到 GitHub CLI
    echo 請先安裝: winget install --id GitHub.cli
    pause
    exit /b 1
)

gh auth status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 錯誤: GitHub CLI 尚未登入
    echo 請執行: gh auth login
    pause
    exit /b 1
)

echo ✅ GitHub CLI 已就緒
echo.

REM ========== 讀取版本號 ==========
set /p VERSION=<version.txt
set TAG=v%VERSION%

echo 📦 準備發布版本: %TAG%
echo.

REM ========== 檢查建置產物 ==========
echo 檢查建置產物...
echo.

set FILES_TO_UPLOAD=
set UPLOAD_COUNT=0

REM 檢查 manifest.json
if not exist "dist\manifest.json" (
    echo ❌ 錯誤: 找不到 manifest.json
    echo 請先執行 build_components.bat
    pause
    exit /b 1
)

set FILES_TO_UPLOAD=%FILES_TO_UPLOAD% "dist\manifest.json"
set /a UPLOAD_COUNT+=1
echo ✅ manifest.json

REM 檢查核心程式
set /p CORE_VERSION=<core_version.txt
if exist "dist\AutoFlow_Core_v%CORE_VERSION%.zip" (
    set FILES_TO_UPLOAD=%FILES_TO_UPLOAD% "dist\AutoFlow_Core_v%CORE_VERSION%.zip"
    set /a UPLOAD_COUNT+=1
    
    for %%A in ("dist\AutoFlow_Core_v%CORE_VERSION%.zip") do set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo ✅ AutoFlow_Core_v%CORE_VERSION%.zip (!SIZE_MB! MB)
)

REM 檢查外部腳本
set /p SCRIPTS_VERSION=<scripts_version.txt
if exist "dist\Scripts_v%SCRIPTS_VERSION%.zip" (
    set FILES_TO_UPLOAD=%FILES_TO_UPLOAD% "dist\Scripts_v%SCRIPTS_VERSION%.zip"
    set /a UPLOAD_COUNT+=1
    
    for %%A in ("dist\Scripts_v%SCRIPTS_VERSION%.zip") do set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo ✅ Scripts_v%SCRIPTS_VERSION%.zip (!SIZE_MB! MB)
)

REM 檢查完整壓縮包 (可選)
if exist "dist\AutoFlow_Control_Center_%TAG%_Full.zip" (
    set /p INCLUDE_FULL=是否也上傳完整壓縮包? (Y/N): 
    if /i "!INCLUDE_FULL!"=="Y" (
        set FILES_TO_UPLOAD=%FILES_TO_UPLOAD% "dist\AutoFlow_Control_Center_%TAG%_Full.zip"
        set /a UPLOAD_COUNT+=1
        
        for %%A in ("dist\AutoFlow_Control_Center_%TAG%_Full.zip") do set SIZE=%%~zA
        set /a SIZE_MB=!SIZE! / 1048576
        echo ✅ AutoFlow_Control_Center_%TAG%_Full.zip (!SIZE_MB! MB)
    )
)

echo.
echo 📊 將上傳 %UPLOAD_COUNT% 個檔案
echo.

REM ========== 確認發布 ==========
set /p CONFIRM=確定要發布到 GitHub? (Y/N): 

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo ❌ 已取消發布
    pause
    exit /b 0
)

echo.

REM ========== 建立 Release ==========
echo 正在建立 GitHub Release...
echo.

REM 使用 manifest.json 中的 changelog 或 CHANGELOG.md
if exist "CHANGELOG.md" (
    gh release create %TAG% %FILES_TO_UPLOAD% --title "AutoFlow Control Center %TAG%" --notes-file CHANGELOG.md --latest
) else (
    gh release create %TAG% %FILES_TO_UPLOAD% --title "AutoFlow Control Center %TAG%" --notes "AutoFlow Control Center %TAG% 發布版本" --latest
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 發布失敗!
    echo.
    echo 如標籤已存在,請執行:
    echo   gh release delete %TAG% --yes
    echo.
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  🎉 發布成功!                                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 版本: %TAG%
echo 📊 上傳檔案: %UPLOAD_COUNT% 個
echo 🔗 Release 頁面: https://github.com/kevin-leeeeee/auto_screenshot/releases/tag/%TAG%
echo.

REM 開啟 Release 頁面
set /p OPEN=是否開啟 Release 頁面? (Y/N): 
if /i "%OPEN%"=="Y" (
    start https://github.com/kevin-leeeeee/auto_screenshot/releases/tag/%TAG%
)

echo.
pause
