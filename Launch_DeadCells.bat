@echo off
setlocal
cd /d "%~dp0"

set "EXE=deadcells.exe"
if not exist "%EXE%" (
    if exist "deadcells_gl.exe" (
        set "EXE=deadcells_gl.exe"
    )
)

echo Starting Dead Cells Daily Challenge Emulator...
start "" pythonw.exe daily_server.py
echo Launching %EXE%...
start "" "%EXE%"
