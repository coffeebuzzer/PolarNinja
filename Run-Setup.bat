@echo off
setlocal

cd /d "%~dp0"

REM Prefer python launcher
where py >nul 2>&1
if %errorlevel%==0 (
  set "USE=py -3.11"
) else (
  set "USE=python"
)

echo.
echo Installing / upgrading PySide6, pygame, and pyserial...
echo.

%USE% -m pip install --upgrade pip
%USE% -m pip install --upgrade PySide6 pygame pyserial

echo.
echo Done installing dependencies.
echo Press any key to close this window.
pause

endlocal

