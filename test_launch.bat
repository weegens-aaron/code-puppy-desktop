@echo off
echo Testing pythonw.exe launch...
echo.

REM First, let's see if python works at all
python --version
echo.

REM Check if pythonw exists
where pythonw.exe
echo.

REM Try running with regular python first to see errors
echo Running with python.exe (will show errors):
python "%~dp0launch.py"

pause
