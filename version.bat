@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  AutoFlow - 版本號更新工具                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 讀取當前版本號
if not exist "version.txt" (
    echo 2.2.0>version.txt
)

set /p CURRENT=<version.txt
echo 📌 當前版本: v%CURRENT%
echo.

REM 提示輸入新版本號
set /p NEW_VERSION=請輸入新版本號 (例如 2.2.0): 

REM 驗證版本號格式 (簡單檢查)
echo %NEW_VERSION% | findstr /R "^[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*$" >nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 錯誤: 版本號格式不正確
    echo 正確格式: X.Y.Z (例如 2.2.0)
    echo.
    pause
    exit /b 1
)

REM 確認更新
echo.
echo 即將更新版本號:
echo   v%CURRENT% → v%NEW_VERSION%
echo.
set /p CONFIRM=確定要更新嗎? (Y/N): 

if /i not "%CONFIRM%"=="Y" (
    echo.
    echo ❌ 已取消更新
    pause
    exit /b 0
)

REM 更新 version.txt
echo %NEW_VERSION%>version.txt

REM 更新 run_app.py 中的版本號
powershell -Command "(Get-Content 'run_app.py') -replace 'CURRENT_VERSION = \"v[0-9.]+\"', 'CURRENT_VERSION = \"v%NEW_VERSION%\"' | Set-Content 'run_app.py'"

REM 更新 README.md 中的版本號
powershell -Command "(Get-Content 'README.md') -replace 'v[0-9.]+', 'v%NEW_VERSION%' | Set-Content 'README.md'"

REM 更新 package.json 中的版本號 (如果存在)
if exist "autoflow-control-center\package.json" (
    powershell -Command "$json = Get-Content 'autoflow-control-center\package.json' | ConvertFrom-Json; $json.version = '%NEW_VERSION%'; $json | ConvertTo-Json -Depth 10 | Set-Content 'autoflow-control-center\package.json'"
)

echo.
echo ✅ 版本號已更新為 v%NEW_VERSION%
echo.
echo 📝 已更新的檔案:
echo   - version.txt
echo   - run_app.py
echo   - README.md
if exist "autoflow-control-center\package.json" (
    echo   - autoflow-control-center\package.json
)
echo.
echo 💡 下一步:
echo   1. 更新 CHANGELOG.md
echo   2. 執行 git commit -am "Bump version to v%NEW_VERSION%"
echo   3. 執行 release.bat 建置並發布
echo.

pause
