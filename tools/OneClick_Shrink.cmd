@echo off
setlocal EnableDelayedExpansion
REM ==== Polar Ninja One-Click SHRINK (no deletes) ====
set ROOT=C:\PolarNinja
set LOG=%ROOT%\logs\cleanup_reports\OneClick_%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%-%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%.txt
set LOG=%LOG: =0%

echo === Polar Ninja One-Click Shrink ===
echo Root : %ROOT%
echo Mode : MOVE/SAFE
echo. 

REM Ensure folders
if not exist "%ROOT%\logs\cleanup_reports" mkdir "%ROOT%\logs\cleanup_reports"
if not exist "%ROOT%\assets\archive" mkdir "%ROOT%\assets\archive"

REM Delete __pycache__ folders
for /f "delims=" %%D in ('dir /s /b "%ROOT%\*__pycache__" 2^>nul') do (
  echo remove %%D>>"%LOG%"
  rmdir /s /q "%%D" 2>nul
)

REM Move *.wav in assets to archive
for /f "delims=" %%F in ('dir /b "%ROOT%\assets\*.wav" 2^>nul') do (
  echo move (WAV): %%F>>"%LOG%"
  move /y "%ROOT%\assets\%%F" "%ROOT%\assets\archive\%%F" >nul
)

REM Move images >= 5MB (PNG/JPG) into archive
for %%E in (png jpg jpeg PNG JPG JPEG) do (
  for /f "delims=" %%F in ('dir /b "%ROOT%\assets\*.%%E" 2^>nul') do (
    for %%S in ("%ROOT%\assets\%%F") do (
      set SZ=%%~zS
      if !SZ! GEQ 5242880 (
        echo move (IMG>=5MB): %%F>>"%LOG%"
        move /y "%ROOT%\assets\%%F" "%ROOT%\assets\archive\%%F" >nul
      )
    )
  )
)

echo Done. Detailed log:
echo   %LOG%
echo.
pause
endlocal
