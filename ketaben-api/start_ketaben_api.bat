@echo off
REM Batch file to run ketaben API on Windows
echo Starting db_ketaben REST API...
echo.

REM Check if .env exists
if exist .env (
    echo Loading environment from .env...
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "%%a=%%b"
    )
)

echo.
echo API will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
