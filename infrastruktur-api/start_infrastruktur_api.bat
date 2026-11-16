@echo off
cd /d "%~dp0"
set INFRASTRUKTUR_DB_HOST=127.0.0.1
set INFRASTRUKTUR_DB_PORT=3306
set INFRASTRUKTUR_DB_USER=root
set INFRASTRUKTUR_DB_PASSWORD=
set INFRASTRUKTUR_DB_NAME=db_infrastruktur
uvicorn main:app --host 0.0.0.0 --port 8000
pause
