@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ======================================================
echo       DailyCells - Dead Cells Daily Run Setup
echo ======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не обнаружен в системе!
    echo Для работы локального сервера эмулятора требуется Python 3.8+
    echo Скачайте и установите Python с официального сайта:
    echo   https://www.python.org/downloads/
    echo (Обязательно отметьте галочку "Add Python to PATH" при установке!)
    echo.
    pause
    exit /b 1
)

python patcher.py --install
echo.
pause
