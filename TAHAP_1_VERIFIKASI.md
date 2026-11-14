# Tahap 1: Verifikasi Read-Only API Lokal (db_dispenda)

**Status: ✅ SELESAI**

## Ringkasan

API read-only lokal untuk `db_dispenda` telah berhasil dibangun menggunakan **FastAPI** dan berjalan di **http://0.0.0.0:8000**. Semua 6 endpoint telah diverifikasi dan mengembalikan data dengan benar.

---

## 1. Struktur File yang Dibuat

```
dispenda-api/
├── main.py                 # Aplikasi FastAPI utama
├── requirements.txt        # Dependensi Python
├── .env.example            # Contoh konfigurasi environment
├── run_windows.ps1         # Script helper untuk menjalankan di Windows
├── README.md               # Dokumentasi lengkap
└── .venv/                  # Virtual environment (auto-created)
```

## 2. Fitur API

### Endpoint Health Check
- `GET /` — Root endpoint
- `GET /health` — Check koneksi database

### Endpoint Metadata
- `GET /api/tables` — List semua endpoint dan tabel terkait

### Endpoint Data (6 tabel Dispenda)
- `GET /api/kategori-pajak` → `tb_kategori_pajak` (5 record)
- `GET /api/metode-bayar` → `tb_metode_bayar` (12 record)
- `GET /api/wajib-pajak` → `tb_wajib_pajak` (1.794 record)
- `GET /api/objek-pajak` → `tb_objek_pajak` (1.813 record)
- `GET /api/tagihan` → `tb_tagihan` (1.813 record)
- `GET /api/pembayaran` → `tb_pembayaran` (831 record)

### Query Parameters
- `page` (default: 1, min: 1) — nomor halaman
- `limit` (default: 100, min: 1, max: 1000) — jumlah record per halaman

---

## 3. Verifikasi Endpoint

### Health Check
```
✅ GET /health
Response: 
{
  "success": true,
  "database": "db_dispenda",
  "status": "connected"
}
```

### Metadata
```
✅ GET /api/tables
Response menampilkan 6 endpoint:
- /api/kategori-pajak → tb_kategori_pajak
- /api/metode-bayar → tb_metode_bayar
- /api/wajib-pajak → tb_wajib_pajak
- /api/objek-pajak → tb_objek_pajak
- /api/tagihan → tb_tagihan
- /api/pembayaran → tb_pembayaran
```

### Endpoint: kategori-pajak
```
✅ GET /api/kategori-pajak?page=1&limit=5
Response:
{
  "success": true,
  "data": [
    {
      "id_kategori": 1,
      "nama_pajak": "Pajak Kendaraan Bermotor (Roda 2)",
      "tarif_persentase": 1.5
    },
    {
      "id_kategori": 2,
      "nama_pajak": "Pajak Kendaraan Bermotor (Roda 4)",
      "tarif_persentase": 2.0
    },
    ...
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 5,
    "total": 5,
    "total_pages": 1,
    "has_next": false
  }
}
```

### Semua Endpoint Data (Summary)
```
✅ GET /api/metode-bayar?page=1&limit=1     → 12 total records
✅ GET /api/wajib-pajak?page=1&limit=1      → 1,794 total records
✅ GET /api/objek-pajak?page=1&limit=1      → 1,813 total records
✅ GET /api/tagihan?page=1&limit=1          → 1,813 total records
✅ GET /api/pembayaran?page=1&limit=1       → 831 total records
```

---

## 4. Setup & Menjalankan API

### Prerequisite
- Python 3.9+
- MySQL 8 dengan `db_dispenda` sudah ter-restore (✅ sudah ada)
- pip

### Instalasi

```powershell
# 1. Masuk ke folder dispenda-api
cd "d:\MAGANG\project\ETL airflow\dispenda-api"

# 2. Buat virtual environment
python -m venv .venv

# 3. Aktifkan virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
```

### Menjalankan Server

#### Option 1: Menggunakan PowerShell Script
```powershell
.\run_windows.ps1
```

#### Option 2: Manual dengan uvicorn
```powershell
$env:DISPENDA_DB_HOST="127.0.0.1"
$env:DISPENDA_DB_PORT="3306"
$env:DISPENDA_DB_USER="root"
$env:DISPENDA_DB_PASSWORD="PASSWORD_MYSQL"
$env:DISPENDA_DB_NAME="db_dispenda"

python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Output yang diharapkan:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Testing API

#### Using curl (PowerShell)
```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Get data
Invoke-WebRequest -Uri "http://localhost:8000/api/kategori-pajak?page=1&limit=10" -UseBasicParsing
```

#### Interactive Swagger UI
```
http://localhost:8000/docs
```

Browser akan membuka dokumentasi interaktif FastAPI where you can test semua endpoint.

---

## 5. Konfigurasi Koneksi Database

**File environment variables:**
- Lokasi: `dispenda-api/.env.example`
- Rename ke `.env` atau set langsung di terminal

**Environment Variables yang diperlukan:**
```
DISPENDA_DB_HOST=127.0.0.1          # IP/hostname MySQL server
DISPENDA_DB_PORT=3306               # Port MySQL (default 3306)
DISPENDA_DB_USER=root               # Username MySQL
DISPENDA_DB_PASSWORD=PASSWORD       # Password MySQL
DISPENDA_DB_NAME=db_dispenda        # Database name
```

**Koneksi lokal saat ini:**
- Host: `127.0.0.1`
- Port: `3306`
- User: `root`
- Password: (kosong)
- Database: `db_dispenda`

---

## 6. Integrasi dengan Airflow

Ketika siap mengintegrasikan dengan Airflow DAG:

### 1. Update URL di Airflow DAG
Di `dags/main.py`, tambahkan konfigurasi Dispenda API:

```python
PIPELINE_TASKS = [
    {
        "name": "dispenda",
        "create_tasks": create_dispenda_tasks,
        "api_base_url": "http://IP_KOMPUTER_API:8000/api",
    },
    # ... pipeline lainnya
]
```

Ganti `IP_KOMPUTER_API` dengan IP komputer yang menjalankan Dispenda API server.

### 2. Contoh Fetch Data dari API di DAG
```python
import requests

api_url = "http://192.168.X.X:8000/api"  # Sesuaikan IP
response = requests.get(f"{api_url}/kategori-pajak?page=1&limit=100")
data = response.json()

if data['success']:
    records = data['data']
    pagination = data['pagination']
    print(f"Fetch halaman {pagination['current_page']} dari {pagination['total_pages']}")
else:
    print("Error:", data.get('error'))
```

---

## 7. Format Respons API

### Success Response (HTTP 200)
```json
{
  "success": true,
  "data": [
    { /* record 1 */ },
    { /* record 2 */ },
    ...
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 5000,
    "total_pages": 50,
    "has_next": true
  }
}
```

### Error Response (HTTP 404 / 500)
```json
{
  "success": false,
  "error": "Endpoint 'invalid-endpoint' tidak tersedia.",
  "available_endpoints": [
    "kategori-pajak",
    "metode-bayar",
    "wajib-pajak",
    "objek-pajak",
    "tagihan",
    "pembayaran"
  ]
}
```

---

## 8. Fitur Keamanan & CORS

- **CORS Enabled**: Akses dari semua origin diizinkan (cocok untuk dev lokal)
- **Method Allowed**: GET only (read-only)
- **Database**: PyMySQL driver (native Python, no ODBC)
- **Charset**: UTF-8MB4 (support emoji & karakter spesial)

---

## 9. Troubleshooting

### Issue: Connection Refused
**Penyebab**: Database MySQL tidak berjalan atau konfigurasi host salah
**Solusi**: 
- Pastikan MySQL service berjalan
- Check `DISPENDA_DB_HOST` dan `DISPENDA_DB_PORT` di environment

### Issue: "Endpoint XXX tidak tersedia"
**Penyebab**: URL endpoint salah atau typo
**Solusi**: 
- Check endpoint names di `/api/tables`
- Gunakan nama dengan hyphen, contoh: `kategori-pajak` bukan `kategori_pajak`

### Issue: Port 8000 sudah dipakai
**Penyebab**: Aplikasi lain sudah menggunakan port 8000
**Solusi**: 
- Ganti port: `uvicorn main:app --host 0.0.0.0 --port 8001`
- Atau stop aplikasi lain yang menggunakan port 8000

---

## 10. Next Steps untuk Tahap 2

Setelah Tahap 1 (Read-Only API) selesai, Tahap 2 akan mencakup:

1. **Integrasi Airflow**: Tambahkan Dispenda pipeline ke DAG utama
2. **Extract Task**: Create task untuk fetch data dari API dan insert ke `raw_data` database
3. **Transform Task**: Clean & validate data dari `raw_data` ke `staging_area`
4. **Load Task**: Load data ke Data Warehouse (`dwh`) dengan star schema

---

## Summary Verifikasi

| Aspek | Status | Keterangan |
|-------|--------|-----------|
| API Server | ✅ Running | Port 8000, FastAPI |
| Database Connection | ✅ Connected | db_dispenda, utf8mb4 |
| Endpoint: kategori-pajak | ✅ Working | 5 records |
| Endpoint: metode-bayar | ✅ Working | 12 records |
| Endpoint: wajib-pajak | ✅ Working | 1,794 records |
| Endpoint: objek-pajak | ✅ Working | 1,813 records |
| Endpoint: tagihan | ✅ Working | 1,813 records |
| Endpoint: pembayaran | ✅ Working | 831 records |
| Pagination | ✅ Working | Min 1, Max 1000 per page |
| CORS | ✅ Enabled | All origins allowed |
| Documentation | ✅ Available | Swagger UI at /docs |

---

**Dibuat**: 14 November 2026  
**Teknologi**: FastAPI, PyMySQL, Python 3.9+  
**Target**: Local ETL Airflow - Dispenda (Pajak Daerah)
