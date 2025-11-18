@echo off
setlocal ENABLEDELAYEDEXPANSION

title Polar Ninja - Beta .06

REM Jump to the folder this script lives in
cd /d "%~dp0"

REM Prefer the Python launcher (py -3.11), fallback to plain python
set "USE="
where py >nul 2>&1 && set "USE=py -3.11"
if not defined USE set "USE=python"

REM Quick check: does Python actually run at all?
%USE% -c "print('PYOK')" >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Python 3.11+ was not found on this system.
  echo Please install Python 3.11 or later and try again.
  echo.
  pause
  goto :eof
)

REM Check for PySide6 and pygame
set "CHK="
%USE% -c "import importlib; print('OK' if all(importlib.util.find_spec(m) for m in ['PySide6','pygame']) else 'MISS')" > "__chk.txt" 2>nul

if exist "__chk.txt" (
  set /p CHK=<"__chk.txt"
  del "__chk.txt" >nul 2>&1
)

if /I not "%CHK%"=="OK" (
  echo.
  echo PySide6 and/or pygame not found. Running first-time setup...
  echo.
  if exist "%~dp0Run-Setup.bat" (
    call "%~dp0Run-Setup.bat"
  ) else (
    echo ERROR: Run-Setup.bat is missing in:
    echo   %~dp0
    echo Cannot install dependencies automatically.
    echo.
    pause
    goto :eof
  )
)

echo.
echo Launching Polar Ninja with %USE%...
echo.
%USE% app.py
if errorlevel 1 (
  echo.
  echo Polar Ninja exited with an error.
  echo.
  pause
)

endlocal
