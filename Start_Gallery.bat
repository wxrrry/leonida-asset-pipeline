@echo off
title Leonida 3D Asset Studio
echo ========================================================
echo       Leonida 3D Asset Studio ^& Model Inspector
echo ========================================================
echo.
echo Starting local web gallery server...

REM 1. Check portable python in parent dir
if exist "%~dp0..\python312\python.exe" (
    "%~dp0..\python312\python.exe" -I "%~dp0tools\gallery.py"
    goto end
)

REM 2. Try py launcher
py -3 -I "%~dp0tools\gallery.py" 2>nul
if %errorlevel% equ 0 goto end

REM 3. Try system python
python -I "%~dp0tools\gallery.py" 2>nul
if %errorlevel% equ 0 goto end

echo [ERROR] Python not found. Please install Python 3.10+ or run with your Python interpreter.
pause

:end
