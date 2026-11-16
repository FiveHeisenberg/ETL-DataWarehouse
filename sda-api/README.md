# REST API db_sda_lingkungan

REST API read-only untuk SDA Lingkungan yang mengekspos 9 tabel utama melalui endpoint GET. Dibangun dengan FastAPI, dirancang khusus untuk ETL/Airflow lokal.

## Prasyarat

- Python 3.9+
- MySQL 8 dengan database `db_sda_lingkungan` sudah ter-restore
- Konektivitas jaringan antara API server dan Airflow

## Setup & Jalankan

### 1. Buat Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Konfigurasi Database

Copy `.env.example` ke `.env` dan sesuaikan:

```env
SDA_DB_HOST=127.0.0.1
SDA_DB_PORT=3306
SDA_DB_USER=root
SDA_DB_PASSWORD=PASSWORD_MYSQL
SDA_DB_NAME=db_sda_lingkungan
```

Atau set environment variables langsung di terminal:

```powershell
$env:SDA_DB_HOST="127.0.0.1"
$env:SDA_DB_PORT="3306"
$env:SDA_DB_USER="root"
$env:SDA_DB_PASSWORD="password_kamu"
$env:SDA_DB_NAME="db_sda_lingkungan"
```

### 4. Jalankan Server

```powershell
uvicorn main:app --host 0.0.0.0 --port 8002
```

Atau gunakan script helper:

```powershell
.\run_windows.ps1
```

Server akan berjalan di `http://0.0.0.0:8002`

## Endpoint API

Semua endpoint bersifat **read-only** (GET only) dan mendukung paginasi.

### Health Check

```
GET /
GET /health
```

### Metadata

```
GET /api/tables
```

Mengembalikan daftar endpoint dan tabel terkait.

### Data Endpoints - Master Tables

```
GET /api/wilayah              → master_wilayah
GET /api/fasilitas-sampah     → master_fasilitas_sampah
GET /api/perusahaan           → master_perusahaan
GET /api/stasiun-pantau       → master_stasiun_pantau
```

### Data Endpoints - Transactional Tables

```
GET /api/izin-lingkungan      → izin_lingkungan
GET /api/kualitas-air-sungai  → kualitas_air_sungai
GET /api/kualitas-udara       → kualitas_udara
GET /api/timbulan-sampah      → timbulan_sampah
GET /api/tutupan-lahan-rth    → tutupan_lahan_rth
```

### Query Parameters

- `page` (default: 1, min: 1) — nomor halaman
- `limit` (default: 100, min: 1, max: 1000) — jumlah record per halaman

### Contoh Request

```bash
# Halaman pertama, 100 record
curl "http://localhost:8002/api/wilayah?page=1&limit=100"

# Halaman kedua, 500 record
curl "http://localhost:8002/api/kualitas-udara?page=2&limit=500"
```

## Response Format

### Success (200)

```json
{
  "success": true,
  "data": [
    { "id_desa": "01011", "nama_desa": "Desa Peuniti", ... },
    { "id_desa": "01012", "nama_desa": "Desa Punge Blang Cut", ... }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 133,
    "total_pages": 2,
    "has_next": true
  }
}
```

### Error (404 / 500)

```json
{
  "success": false,
  "error": "Endpoint 'invalid-endpoint' tidak tersedia.",
  "available_endpoints": ["wilayah", "fasilitas-sampah", ...]
}
```

## Testing

Akses dokumentasi interaktif Swagger UI:

```
http://localhost:8002/docs
```

Atau ReDoc:

```
http://localhost:8002/redoc
```

## Integrasi dengan Airflow

Di Airflow DAG, gunakan endpoint seperti:

```python
api_url = "http://192.168.1.XX:8002/api"
response = requests.get(f"{api_url}/wilayah?page=1&limit=100")
data = response.json()
```

Ganti `192.168.1.XX` dengan IP komputer yang menjalankan API server ini.

## Notes

- API berjalan di **port 8002** secara default, dapat diubah dengan flag `--port` di uvicorn atau environment variable
- Akses dari **semua origin** diizinkan (CORS enabled) untuk kemudahan testing lokal
- Database driver menggunakan **PyMySQL** untuk kompatibilitas Windows
- Charset database: **utf8mb4** (support emoji dan karakter spesial)

---

Dibuat untuk ETL Airflow — SDA Lingkungan Banda Aceh
