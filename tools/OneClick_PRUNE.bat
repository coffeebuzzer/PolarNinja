@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "& '%~dp0OneClick_PRUNE.ps1' -Root '%~dp0\..'"

echo.
echo DRY-RUN complete. Press any key to APPLY deletions...
pause >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "& '%~dp0OneClick_PRUNE.ps1' -Root '%~dp0\..' -Apply:$true"

pause
