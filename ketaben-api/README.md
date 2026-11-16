# REST API - db_ketaben (Ketangguhan Bencana)

FastAPI read-only untuk expose database `db_ketaben` ke Airflow ETL pipeline.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database:
```bash
cp .env.example .env
# Edit .env dengan kredensial database Anda
```

3. Run server:

**Windows:**
```bash
run_windows.ps1
```
atau
```bash
start_ketaben_api.bat
```

**Linux/Mac:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### Health Check
- `GET /` - Service info
- `GET /health` - Database connection check

### Metadata
- `GET /api/tables` - List semua tabel dan endpoint

### Data (dengan pagination)
- `GET /api/bencana?page=1&limit=100`
- `GET /api/korban-bencana?page=1&limit=100`
- `GET /api/kerusakan-bencana?page=1&limit=100`
- `GET /api/bantuan?page=1&limit=100`
- `GET /api/rehabilitasi?page=1&limit=100`
- `GET /api/rekonstruksi?page=1&limit=100`

### Swagger Documentation
- `GET /docs` - Interactive API docs

## Response Format

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 152,
    "total_pages": 2,
    "has_next": true
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| KETABEN_DB_HOST | 127.0.0.1 | MySQL host |
| KETABEN_DB_PORT | 3306 | MySQL port |
| KETABEN_DB_USER | root | MySQL user |
| KETABEN_DB_PASSWORD | (empty) | MySQL password |
| KETABEN_DB_NAME | db_ketaben | Database name |

## Notes

- Read-only API (hanya GET)
- Pagination: max 1000 records per request
- Auto-convert datetime, decimal, bytes ke JSON-safe format
- CORS enabled untuk semua origins
