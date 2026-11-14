# REST API db_dispenda

REST API read-only untuk Dispenda (Pajak Daerah) yang mengekspos 6 tabel utama melalui endpoint GET. Dibangun dengan FastAPI, dirancang khusus untuk ETL/Airflow lokal.

## Prasyarat

- Python 3.9+
- MySQL 8 dengan database `db_dispenda` sudah ter-restore
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
DISPENDA_DB_HOST=127.0.0.1
DISPENDA_DB_PORT=3306
DISPENDA_DB_USER=root
DISPENDA_DB_PASSWORD=PASSWORD_MYSQL
DISPENDA_DB_NAME=db_dispenda
```

Atau set environment variables langsung di terminal:

```powershell
$env:DISPENDA_DB_HOST="127.0.0.1"
$env:DISPENDA_DB_PORT="3306"
$env:DISPENDA_DB_USER="root"
$env:DISPENDA_DB_PASSWORD="password_kamu"
$env:DISPENDA_DB_NAME="db_dispenda"
```

### 4. Jalankan Server

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

Atau gunakan script helper:

```powershell
.\run_windows.ps1
```

Server akan berjalan di `http://0.0.0.0:8000`

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

### Data Endpoints

```
GET /api/kategori-pajak       → tb_kategori_pajak
GET /api/metode-bayar         → tb_metode_bayar
GET /api/wajib-pajak          → tb_wajib_pajak
GET /api/objek-pajak          → tb_objek_pajak
GET /api/tagihan              → tb_tagihan
GET /api/pembayaran           → tb_pembayaran
```

### Query Parameters

- `page` (default: 1, min: 1) — nomor halaman
- `limit` (default: 100, min: 1, max: 1000) — jumlah record per halaman

### Contoh Request

```bash
# Halaman pertama, 100 record
curl "http://localhost:8000/api/kategori-pajak?page=1&limit=100"

# Halaman kedua, 500 record
curl "http://localhost:8000/api/wajib-pajak?page=2&limit=500"
```

## Response Format

### Success (200)

```json
{
  "success": true,
  "data": [
    { "id_kategori": 1, "nama_pajak": "PBB", ... },
    { "id_kategori": 2, "nama_pajak": "BPHTB", ... }
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

### Error (404 / 500)

```json
{
  "success": false,
  "error": "Endpoint 'invalid-endpoint' tidak tersedia.",
  "available_endpoints": ["kategori-pajak", "metode-bayar", ...]
}
```

## Testing

Akses dokumentasi interaktif Swagger UI:

```
http://localhost:8000/docs
```

Atau ReDoc:

```
http://localhost:8000/redoc
```

## Integrasi dengan Airflow

Di Airflow DAG, gunakan endpoint seperti:

```python
api_url = "http://192.168.1.XX:8000/api"
response = requests.get(f"{api_url}/kategori-pajak?page=1&limit=100")
data = response.json()
```

Ganti `192.168.1.XX` dengan IP komputer yang menjalankan API server ini.

## Notes

- API berjalan di **port 8000** secara default, dapat diubah dengan flag `--port` di uvicorn
- Akses dari **semua origin** diizinkan (CORS enabled) untuk kemudahan testing lokal
- Database driver menggunakan **PyMySQL** untuk kompatibilitas Windows
- Charset database: **utf8mb4** (support emoji dan karakter spesial)

---

Dibuat untuk Tahap 1 ETL Airflow — Dispenda (Pajak Daerah) Banda Aceh
