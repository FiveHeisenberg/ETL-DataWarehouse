# PowerShell script untuk menjalankan Dispenda API di Windows
# 1. Asumsikan db_dispenda sudah terestore di MySQL lokal
# 2. Ubah konfigurasi .env sesuai dengan password MySQL kamu
# 3. Jalankan script ini

# Setup virtual environment
if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:DISPENDA_DB_HOST="127.0.0.1"
$env:DISPENDA_DB_PORT="3306"
$env:DISPENDA_DB_USER="root"
$env:DISPENDA_DB_PASSWORD="PASSWORD_MYSQL"  # GANTI DENGAN PASSWORD KAMU
$env:DISPENDA_DB_NAME="db_dispenda"

# Run the API server
Write-Host "Starting Dispenda API Server on http://0.0.0.0:8000"
Write-Host "Swagger Docs: http://localhost:8000/docs"
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8000
