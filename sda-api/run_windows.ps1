# PowerShell script untuk menjalankan SDA Lingkungan API di Windows
# 1. Asumsikan db_sda_lingkungan sudah terestore di MySQL lokal
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
$env:SDA_DB_HOST="127.0.0.1"
$env:SDA_DB_PORT="3306"
$env:SDA_DB_USER="root"
$env:SDA_DB_PASSWORD=""
$env:SDA_DB_NAME="db_sda_lingkungan"

# Run the API server
Write-Host "Starting SDA Lingkungan API Server on http://0.0.0.0:8002"
Write-Host "Swagger Docs: http://localhost:8002/docs"
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8002
