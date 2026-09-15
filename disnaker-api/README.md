# REST API db_disnaker

Alur: db_disnaker -> REST API -> Airflow -> raw_data -> staging_area.

## Install
python -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

## Jalankan di komputer yang menyimpan db_disnaker
$env:DISNAKER_DB_HOST="127.0.0.1"
$env:DISNAKER_DB_PORT="3306"
$env:DISNAKER_DB_USER="root"
$env:DISNAKER_DB_PASSWORD="PASSWORD_MYSQL"
$env:DISNAKER_DB_NAME="db_disnaker"
uvicorn main:app --host 0.0.0.0 --port 8000

Swagger: http://IP-KOMPUTER-SUMBER:8000/docs

## Endpoint
GET /api/kasus-hi
GET /api/lowongan
GET /api/pelatihan-blk
GET /api/penduduk-pencaker
GET /api/penempatan
GET /api/perusahaan
GET /api/peserta-pelatihan

Semua mendukung ?page=1&limit=100 dan mengembalikan {success,data,pagination}, sesuai kontrak yang dibaca oleh disnaker.py.

## Tes dari laptop Airflow
curl http://IP-KOMPUTER-SUMBER:8000/health
curl "http://IP-KOMPUTER-SUMBER:8000/api/perusahaan?page=1&limit=100"
