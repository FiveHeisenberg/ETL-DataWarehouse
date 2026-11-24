# Perencanaan API Endpoints

Base URL: `http://localhost:8003`

## Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint dengan info service |
| GET | `/health` | Health check database connection |

## Metadata

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tables` | Daftar semua endpoint yang tersedia |

## Data Endpoints

Semua endpoint data mendukung pagination:
- `page` (default: 1, min: 1)
- `limit` (default: 100, max: 1000)

Response format:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 10,
    "total_pages": 1,
    "has_next": false
  }
}
```

### Master Data

| Method | Endpoint | Table | Description |
|--------|----------|-------|-------------|
| GET | `/api/skpa` | `master_skpa` | Master SKPA (Satuan Kerja Perangkat Aceh) |

### Transaksional Data

| Method | Endpoint | Table | Description |
|--------|----------|-------|-------------|
| GET | `/api/program` | `tb_program` | Program perencanaan |
| GET | `/api/kegiatan` | `tb_kegiatan` | Kegiatan perencanaan |
| GET | `/api/target` | `tb_target` | Target kinerja |
| GET | `/api/realisasi` | `tb_realisasi` | Realisasi kinerja |
| GET | `/api/evaluasi` | `tb_evaluasi_pembangunan` | Evaluasi pembangunan |

## Example Usage

```bash
# Get first page of SKPA (100 records)
curl "http://localhost:8003/api/skpa"

# Get page 2 with 500 records per page
curl "http://localhost:8003/api/kegiatan?page=2&limit=500"

# Health check
curl "http://localhost:8003/health"

# List all tables
curl "http://localhost:8003/api/tables"
```

## Running the API

### Windows (Batch)
```cmd
run.bat
```

### Windows (PowerShell)
```powershell
.\run_windows.ps1
```

### Manual
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
set PERENCANAAN_DB_HOST=127.0.0.1
set PERENCANAAN_DB_PORT=3306
set PERENCANAAN_DB_USER=root
set PERENCANAAN_DB_PASSWORD=
set PERENCANAAN_DB_NAME=db_perencanaan
uvicorn main:app --host 0.0.0.0 --port 8003
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PERENCANAAN_DB_HOST` | `127.0.0.1` | MySQL host |
| `PERENCANAAN_DB_PORT` | `3306` | MySQL port |
| `PERENCANAAN_DB_USER` | `root` | MySQL user |
| `PERENCANAAN_DB_PASSWORD` | `` | MySQL password |
| `PERENCANAAN_DB_NAME` | `db_perencanaan` | Database name |