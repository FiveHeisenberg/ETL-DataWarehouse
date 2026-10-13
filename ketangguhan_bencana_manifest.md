# Ketangguhan Bencana Branch Manifest

**Branch:** `etl/ketangguhan-bencana`  
**Created:** 2026-10-13  
**Domain:** Disaster Resilience (disasters, casualties, damages, aid, rehabilitation, reconstruction)

---

## Files to Include

### 1. Plan Document
- `db_ketangguhan_bencana_plan.md` - Complete schema design, data model, progress tracking

### 2. Database Files
- `db/db_ketaben.sql` - Complete schema + sample data dump for all 6 tables

### 3. FastAPI Service
- `ketaben-api/` (entire directory)
  - `main.py` - FastAPI application with 6 table endpoints
  - `requirements.txt` - Dependencies
  - `README.md` - API documentation
  - `.env.example` - Configuration template
  - `run_windows.ps1` - PowerShell runner
  - `start_ketaben_api.bat` - Batch runner (if exists)

### 4. Airflow DAG
- `dags/ketangguhanbencana.py` - ETL pipeline for all 6 disaster resilience tables

### 5. Modified Core Files
- `dags/main.py` - Updated with ketangguhan bencana pipeline registration
- `.gitignore` - Updated (if ketaben-specific entries added)

---

## Tables Covered
1. `tb_bencana` - Disaster events (parent table)
2. `tb_korban_bencana` - Casualties
3. `tb_kerusakan_bencana` - Damages
4. `tb_bantuan` - Aid distribution
5. `tb_rehabilitasi` - Rehabilitation
6. `tb_rekonstruksi` - Reconstruction

---

## API Endpoints
- `GET /api/bencana`
- `GET /api/korban-bencana`
- `GET /api/kerusakan-bencana`
- `GET /api/bantuan`
- `GET /api/rehabilitasi`
- `GET /api/rekonstruksi`

---

## Schema Architecture
- Normalized relational database (1:N relationships)
- Parent-child structure with `id_bencana` foreign keys
- `ON DELETE RESTRICT` to protect historical data

---

## Notes
- All files follow existing ETL pipeline patterns
- API uses same pagination contract as other domains
- DAG integrates with main.py PIPELINE_TASKS
- 162 total sample records across all tables
