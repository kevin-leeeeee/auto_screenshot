@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  AutoFlow - 自動建置與發布工具                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ========== 檢查 GitHub CLI ==========
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 錯誤: 找不到 GitHub CLI
    echo.
    echo 請先安裝 GitHub CLI:
    echo   方法 1: winget install --id GitHub.cli
    echo   方法 2: 下載安裝程式 https://cli.github.com/
    echo.
    echo 安裝後請執行: gh auth login
    echo.
    pause
    exit /b 1
)

REM 檢查是否已登入
gh auth status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 錯誤: GitHub CLI 尚未登入
    echo.
    echo 請執行: gh auth login
    echo.
    pause
    exit /b 1
)

echo ✅ GitHub CLI 已就緒
echo.

REM ========== 讀取版本號 ==========
if not exist "version.txt" (
    echo ❌ 錯誤: 找不到 version.txt
    echo 請先執行 bump_version.bat 設定版本號
    pause
    exit /b 1
)

set /p VERSION=<version.txt
set TAG=v%VERSION%
set ZIP_NAME=AutoFlow_Control_Center_%TAG%_Full.zip

echo 📦 準備發布版本: %TAG%
echo.

REM ========== 檢查 CHANGELOG ==========
if not exist "CHANGELOG.md" (
    echo ⚠️  警告: 找不到 CHANGELOG.md
    echo 建議建立更新日誌以提供更好的發布說明
    echo.
    set /p CONTINUE=是否繼續? (Y/N): 
    if /i not "!CONTINUE!"=="Y" (
        echo 已取消發布
        pause
        exit /b 0
    )
)

REM ========== 建置 ==========
echo [1/4] 開始建置...
echo.

call build_release.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 建置失敗!
    echo 請檢查錯誤訊息並修正後重試
    pause
    exit /b 1
)

echo.
echo ✅ 建置完成
echo.

REM ========== 檢查建置產物 ==========
if not exist "dist\%ZIP_NAME%" (
    echo ❌ 錯誤: 找不到建置產物 dist\%ZIP_NAME%
    echo.
    echo 請確認 build_release.bat 是否正確執行
    pause
    exit /b 1
)

REM 顯示檔案大小
for %%A in ("dist\%ZIP_NAME%") do set SIZE=%%~zA
set /a SIZE_MB=!SIZE! / 1048576

echo 📊 建置產物資訊:
echo   檔案: %ZIP_NAME%
echo   大小: !SIZE_MB! MB
echo.

REM ========== 確認發布 ==========
echo [2/4] 準備發布到 GitHub...
echo.
echo 即將建立 GitHub Release:
echo   標籤: %TAG%
echo   標題: AutoFlow Control Center %TAG%
echo   檔案: %ZIP_NAME% (!SIZE_MB! MB)
echo.

set /p CONFIRM=確定要發布嗎? (Y/N): 

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo ❌ 已取消發布
    pause
    exit /b 0
)

echo.

REM ========== 建立 Release ==========
echo [3/4] 正在建立 GitHub Release...
echo.

if exist "CHANGELOG.md" (
    gh release create %TAG% "dist\%ZIP_NAME%" --title "AutoFlow Control Center %TAG%" --notes-file CHANGELOG.md --latest
) else (
    gh release create %TAG% "dist\%ZIP_NAME%" --title "AutoFlow Control Center %TAG%" --notes "AutoFlow Control Center %TAG% 發布版本" --latest
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 發布失敗!
    echo.
    echo 可能的原因:
    echo   1. 標籤 %TAG% 已存在 (請先刪除或更新版本號)
    echo   2. 網路連線問題
    echo   3. GitHub 權限不足
    echo.
    echo 如需刪除已存在的標籤,請執行:
    echo   gh release delete %TAG% --yes
    echo   git tag -d %TAG%
    echo   git push origin :refs/tags/%TAG%
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ GitHub Release 建立成功!
echo.

REM ========== 完成 ==========
echo [4/4] 發布完成!
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  🎉 發布成功!                                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 版本: %TAG%
echo 📊 大小: !SIZE_MB! MB
echo 🔗 下載連結: https://github.com/kevin-leeeeee/auto_screenshot/releases/tag/%TAG%
echo.
echo 💡 下一步建議:
echo   1. 在 GitHub 上檢查 Release 頁面
echo   2. 測試下載連結是否正常
echo   3. 通知使用者更新
echo.

REM 自動開啟 Release 頁面
set /p OPEN=是否開啟 Release 頁面? (Y/N): 
if /i "%OPEN%"=="Y" (
    start https://github.com/kevin-leeeeee/auto_screenshot/releases/tag/%TAG%
)

echo.
pause
