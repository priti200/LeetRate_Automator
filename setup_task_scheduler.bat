@echo off
REM ============================================================
REM LeetCode Rating Tracker - Windows Task Scheduler Setup
REM This script creates a scheduled task to run the tracker weekly
REM ============================================================

echo.
echo ============================================================
echo LeetCode Tracker - Automated Task Setup
echo ============================================================
echo.

REM Get the current directory (where this script is located)
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Configuration
set TASK_NAME=LeetCodeRatingTracker
set PYTHON_PATH=python
set TRACKER_SCRIPT=%SCRIPT_DIR%\scheduler.py
set SCHEDULE_DAY=MONDAY
set SCHEDULE_TIME=10:00

echo Current directory: %SCRIPT_DIR%
echo Python path: %PYTHON_PATH%
echo Tracker script: %TRACKER_SCRIPT%
echo.
echo Schedule: Every %SCHEDULE_DAY% at %SCHEDULE_TIME%
echo.

REM Check if Python is available
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not found or not in PATH
    echo Please install Python or add it to your PATH variable
    pause
    exit /b 1
)

echo Python found successfully!
echo.

REM Check if the tracker script exists
if not exist "%TRACKER_SCRIPT%" (
    echo ERROR: Tracker script not found at: %TRACKER_SCRIPT%
    pause
    exit /b 1
)

echo Tracker script found!
echo.

REM Delete existing task if it exists
echo Checking for existing task...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if not errorlevel 1 (
    echo Found existing task. Deleting...
    schtasks /delete /tn "%TASK_NAME%" /f
    echo Old task deleted.
)

echo.
echo Creating new scheduled task...
echo.

REM Create the scheduled task
REM Runs every week on the specified day at the specified time
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%PYTHON_PATH%\" \"%TRACKER_SCRIPT%\" --run-now" ^
    /sc weekly ^
    /d %SCHEDULE_DAY% ^
    /st %SCHEDULE_TIME% ^
    /ru SYSTEM ^
    /f

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create scheduled task
    echo You may need to run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! Scheduled task created successfully!
echo ============================================================
echo.
echo Task Name: %TASK_NAME%
echo Schedule: Every %SCHEDULE_DAY% at %SCHEDULE_TIME%
echo.
echo To verify: Open Task Scheduler and look for "%TASK_NAME%"
echo To run manually: schtasks /run /tn "%TASK_NAME%"
echo To delete: schtasks /delete /tn "%TASK_NAME%" /f
echo.
echo The task will automatically run the LeetCode tracker
echo and update ratings from the CSV file weekly.
echo.
echo Log files will be saved to: %SCRIPT_DIR%\scheduler.log
echo.
echo ============================================================
pause
