# PowerShell script untuk menjalankan Perencanaan API di Windows
# 1. Asumsikan db_perencanaan sudah terestore di MySQL lokal
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
$env:PERENCANAAN_DB_HOST="127.0.0.1"
$env:PERENCANAAN_DB_PORT="3306"
$env:PERENCANAAN_DB_USER="root"
$env:PERENCANAAN_DB_PASSWORD=""  # GANTI DENGAN PASSWORD KAMU
$env:PERENCANAAN_DB_NAME="db_perencanaan"

# Run the API server
Write-Host "Starting Perencanaan API Server on http://0.0.0.0:8003"
Write-Host "Swagger Docs: http://localhost:8003/docs"
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8003