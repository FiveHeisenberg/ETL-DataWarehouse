# Infrastruktur Branch Manifest

**Branch:** `etl/infrastruktur`  
**Created:** 2026-10-13  
**Domain:** Infrastructure (roads, bridges, housing, irrigation, transportation)

---

## Files to Include

### 1. Plan Document
- `db_infrastruktur_plan.md` - Complete schema design, data model, progress tracking

### 2. Database Files
- `db/create_db_infrastruktur.sql` - CREATE TABLE statements for all 5 tables
- `db/db_infrastruktur.sql` - Sample data dump

### 3. FastAPI Service
- `infrastruktur-api/` (entire directory)
  - `main.py` - FastAPI application with 5 table endpoints
  - `requirements.txt` - Dependencies
  - `README.md` - API documentation
  - `.env.example` - Configuration template
  - `run_windows.ps1` - PowerShell runner
  - `start_infrastruktur_api.bat` - Batch runner (if exists)

### 4. Airflow DAG
- `dags/infrastruktur.py` - ETL pipeline for all 5 infrastructure tables

### 5. Modified Core Files
- `dags/main.py` - Updated with infrastruktur pipeline registration
- `.gitignore` - Updated (if infrastruktur-specific entries added)

---

## Tables Covered
1. `tb_jalan` - Roads
2. `tb_jembatan` - Bridges
3. `tb_perumahan` - Housing
4. `tb_pengairan` - Irrigation
5. `tb_transportasi` - Transportation

---

## API Endpoints
- `GET /api/jalan`
- `GET /api/jembatan`
- `GET /api/perumahan`
- `GET /api/pengairan`
- `GET /api/transportasi`

---

## Notes
- All files follow existing ETL pipeline patterns
- API uses same pagination contract as other domains
- DAG integrates with main.py PIPELINE_TASKS
