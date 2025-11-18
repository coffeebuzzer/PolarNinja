@echo off
setlocal
REM ==== Polar Ninja One-Click PRUNE (permanent delete) ====
set ROOT=C:\PolarNinja
set LOG=%ROOT%\logs\cleanup_reports\PRUNE_%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%-%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.txt
set LOG=%LOG: =0%

echo === Polar Ninja One-Click PRUNE ===
echo Root : %ROOT%
echo Mode : APPLY (DELETE)
echo.

if not exist "%ROOT%\assets\archive" (
  echo Nothing to delete. "%ROOT%\assets\archive" does not exist.
  pause
  exit /b 0
)

echo delete %ROOT%\assets\archive>>"%LOG%"
rmdir /s /q "%ROOT%\assets\archive"

echo Done. Detailed log:
echo   %LOG%
echo.
pause
endlocal
