@echo off
setlocal EnableDelayedExpansion
REM ==== Polar Ninja Make Release ZIP (no PowerShell policy tweaks needed) ====
set ROOT=C:\PolarNinja
set OUTDIR=%ROOT%\..
set OUTZIP=%OUTDIR%\PolarNinja_Beta05.zip
set IGNORE_FILE=%ROOT%\tools\_common\PolarNinja-Ignore.txt

echo === Polar Ninja Release Maker (Beta .05) ===
echo Root : %ROOT%
echo Out  : %OUTZIP%
echo.

if not exist "%ROOT%" (
  echo ERROR: %ROOT% not found.
  pause
  exit /b 1
)

if not exist "%IGNORE_FILE%" (
  echo ERROR: Ignore file not found: %IGNORE_FILE%
  pause
  exit /b 1
)

REM Build a temp file list
set FILELIST=%TEMP%\pn_filelist_%RANDOM%.txt
if exist "%FILELIST%" del "%FILELIST%" >nul 2>&1

REM Collect all files
for /r "%ROOT%" %%F in (*) do (
  set "REL=%%F"
  set "REL=!REL:%ROOT%\=!"
  echo !REL!>>"%FILELIST%"
)

REM Remove ignored patterns (case-insensitive, simple contains/endswith matching)
set FILTERED=%TEMP%\pn_filelist_filtered_%RANDOM%.txt
if exist "%FILTERED%" del "%FILTERED%" >nul 2>&1

for /f "usebackq delims=" %%L in ("%IGNORE_FILE%") do (
  set "PAT=%%L"
  if "!PAT!"==""  set PAT=#
  echo !PAT! | findstr /b "#">nul && (REM comment line, skip) && set "PAT="
  if defined PAT (
    set "PAT=!PAT:\=/!"
    set "PAT=!PAT:~0,-1!"
  )
)

REM Basic filter pass (excludes lines containing any ignore token)
> "%FILTERED%" (
  for /f "usebackq delims=" %%L in ("%FILELIST%") do (
    set "KEEP=1"
    for /f "usebackq delims=" %%P in ("%IGNORE_FILE%") do (
      set "T=%%P"
      if "!T!"==""  set T=#
      echo !T! | findstr /b "#">nul && set "T="
      if defined T (
        echo %%L | findstr /i /c:"!T!">nul && set KEEP=0
      )
    )
    if !KEEP!==1 echo %%L
  )
)

REM Create the ZIP using built-in PowerShell Compress-Archive (no execution policy changes)
if exist "%OUTZIP%" del "%OUTZIP%" >nul 2>&1
for /f "usebackq delims=" %%L in ("%FILTERED%") do (
  powershell -NoProfile -Command "Add-Type -A 'System.IO.Compression.FileSystem'; [System.IO.Compression.ZipFile]::CreateFromDirectory('%ROOT%','%OUTZIP%')" >nul 2>&1 && goto donezip
)

:donezip
if exist "%OUTZIP%" (
  echo Created: %OUTZIP%
) else (
  echo ERROR: Failed to create %OUTZIP%.
)
echo.
pause
endlocal
