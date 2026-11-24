@echo off
REM ========================================
REM Perencanaan API - Start Script
REM ========================================

setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check if Python installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python dari https://www.python.org
    pause
    exit /b 1
)

REM Setup virtual environment if not exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/update requirements
echo Installing dependencies...
pip install -q -r requirements.txt

REM Set environment variables
set PERENCANAAN_DB_HOST=127.0.0.1
set PERENCANAAN_DB_PORT=3306
set PERENCANAAN_DB_USER=root
set PERENCANAAN_DB_PASSWORD=
set PERENCANAAN_DB_NAME=db_perencanaan

REM Display info
echo.
echo ================================
echo Perencanaan API Server Starting
echo ================================
echo.
echo API URL:  http://localhost:8003
echo Swagger:  http://localhost:8003/docs
echo Health:   http://localhost:8003/health
echo.
echo Press CTRL+C to stop
echo.

REM Start server
python -m uvicorn main:app --host 127.0.0.1 --port 8003

REM Keep window open if error
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start server
    pause
)

endlocal