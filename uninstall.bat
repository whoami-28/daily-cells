@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ======================================================
echo       DailyCells - Dead Cells Daily Run Uninstaller
echo ======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не обнаружен в системе!
    pause
    exit /b 1
)

python patcher.py --uninstall
echo.
pause
