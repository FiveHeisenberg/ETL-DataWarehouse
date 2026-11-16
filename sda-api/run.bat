@echo off
REM Batch script untuk menjalankan SDA Lingkungan API di Windows
REM 1. Asumsikan db_sda_lingkungan sudah terestore di MySQL lokal
REM 2. Ubah konfigurasi .env sesuai dengan password MySQL kamu
REM 3. Jalankan script ini

REM Setup virtual environment
if not exist ".venv" (
    python -m venv .venv
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt

REM Set environment variables
set SDA_DB_HOST=127.0.0.1
set SDA_DB_PORT=3306
set SDA_DB_USER=root
set SDA_DB_PASSWORD=
set SDA_DB_NAME=db_sda_lingkungan

REM Run the API server
echo Starting SDA Lingkungan API Server on http://0.0.0.0:8002
echo Swagger Docs: http://localhost:8002/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8002
