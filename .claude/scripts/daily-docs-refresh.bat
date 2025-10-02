@echo off
REM Daily documentation refresh script for MADF
REM Runs cache-docs-simple.js and updates CLAUDE.md timestamp

cd /d "D:\OneDrive\MADF"

echo Starting daily documentation refresh...
echo Date: %date% Time: %time%

node .claude\scripts\cache-docs-simple.cjs

if %errorlevel% equ 0 (
    echo Documentation refresh completed successfully.
) else (
    echo Documentation refresh failed with error code %errorlevel%
)

echo Finished at %time%