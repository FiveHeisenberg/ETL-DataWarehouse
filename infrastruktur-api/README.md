# REST API db_infrastruktur

Alur: db_infrastruktur -> REST API -> Airflow -> raw_data -> staging_area.

## Install
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

## Jalankan di komputer yang menyimpan db_infrastruktur
$env:INFRASTRUKTUR_DB_HOST="127.0.0.1"
$env:INFRASTRUKTUR_DB_PORT="3306"
$env:INFRASTRUKTUR_DB_USER="root"
$env:INFRASTRUKTUR_DB_PASSWORD="PASSWORD_MYSQL"
$env:INFRASTRUKTUR_DB_NAME="db_infrastruktur"
uvicorn main:app --host 0.0.0.0 --port 8000

Swagger: http://IP-KOMPUTER-SUMBER:8000/docs

## Endpoint
GET /api/jalan
GET /api/jembatan
GET /api/perumahan
GET /api/pengairan
GET /api/transportasi

Semua mendukung ?page=1&limit=100 dan mengembalikan {success,data,pagination}, sesuai kontrak yang dibaca oleh infrastruktur.py.

## Tes dari laptop Airflow
curl http://IP-KOMPUTER-SUMBER:8000/health
curl "http://IP-KOMPUTER-SUMBER:8000/api/jalan?page=1&limit=100"
