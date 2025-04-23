@echo off
REM Navigate to the script directory
cd /d "%~dp0"

REM Run the Python script
python main.py

REM Check for errors
if %errorlevel% neq 0 (
    echo Error: Script execution failed with error code %errorlevel%.
    pause
) else (
    echo Script executed successfully.
)

REM Optional pause for debugging
pause
