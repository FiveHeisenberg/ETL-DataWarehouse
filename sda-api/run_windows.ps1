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
Write-Host "Installing dependencies..."
pip install -q -r requirements.txt

# Set environment variables
$env:SDA_DB_HOST="127.0.0.1"
$env:SDA_DB_PORT="3306"
$env:SDA_DB_USER="root"
$env:SDA_DB_PASSWORD=""  # GANTI DENGAN PASSWORD KAMU (jika ada)
$env:SDA_DB_NAME="db_sda_lingkungan"

# Display info
Write-Host ""
Write-Host "================================"
Write-Host "SDA Lingkungan API Server Starting"
Write-Host "================================"
Write-Host ""
Write-Host "API URL:  http://localhost:8002"
Write-Host "Swagger:  http://localhost:8002/docs"
Write-Host "Health:   http://localhost:8002/health"
Write-Host ""
Write-Host "Press CTRL+C to stop"
Write-Host ""

# Run the API server (use 127.0.0.1 so logs show localhost)
python -m uvicorn main:app --host 127.0.0.1 --port 8002