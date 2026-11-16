# 🏗️ Tahap Implementasi ETL Airflow Dispenda

Dokumentasi progress implementasi ETL untuk Pajak Daerah (Dispenda) dalam ETL DataWarehouse Aceh.

---

## 📍 Tahap Saat Ini

### ✅ TAHAP 1: Build Read-Only API Lokal (db_dispenda)

**Status**: **SELESAI** ✅

**Deliverables**:
- ✅ REST API FastAPI untuk db_dispenda
- ✅ 6 endpoint GET (kategori-pajak, metode-bayar, wajib-pajak, objek-pajak, tagihan, pembayaran)
- ✅ Pagination support (default 100, max 1000)
- ✅ Database connection verified
- ✅ All endpoints tested & working
- ✅ Running on port 8000

**Lokasi**: 
- API Code: `dispenda-api/`
- Documentation: `TAHAP_1_VERIFIKASI.md`, `TAHAP_1_SUMMARY.md`
- Example: `CONTOH_FETCH_API.py`

**Cara Menjalankan**:
```powershell
cd "d:\MAGANG\project\ETL airflow\dispenda-api"
.\run_windows.ps1
```

**Test**:
```
curl http://localhost:8000/health
curl "http://localhost:8000/api/kategori-pajak?page=1&limit=5"
Swagger UI: http://localhost:8000/docs
```

---

## 🔄 Tahap Selanjutnya

### ⏳ TAHAP 2: Integrasi Airflow - Extract to raw_data

**Target**: Extract data dari API → raw_data database

**Tasks**:
- [ ] Create `raw_data` database
- [ ] Create `raw_*` tables untuk 6 endpoint
- [ ] Create extract task di DAG
- [ ] Fetch data dengan pagination
- [ ] Insert ke raw_data dengan metadata (sumber_database, waktu_ekstraksi)
- [ ] Test extract task
- [ ] Verify data integrity

**Expected Output**:
```sql
raw_kategori_pajak   -- Mirror dari tb_kategori_pajak + metadata
raw_metode_bayar     -- Mirror dari tb_metode_bayar + metadata
raw_wajib_pajak      -- Mirror dari tb_wajib_pajak + metadata
raw_objek_pajak      -- Mirror dari tb_objek_pajak + metadata
raw_tagihan          -- Mirror dari tb_tagihan + metadata
raw_pembayaran       -- Mirror dari tb_pembayaran + metadata
```

---

### ⏳ TAHAP 3: Transform to staging_area

**Target**: Clean & validate data dari raw_data → staging_area

**Tasks**:
- [ ] Create `staging_area` database
- [ ] Create transformation queries:
  - TRIM whitespace
  - REGEXP_REPLACE untuk standardisasi
  - NULLIF untuk invalid values
  - Data type validation
  - Duplicate removal (DISTINCT)
  - Enum standardization
- [ ] Create transform task di DAG
- [ ] Test & verify data quality

**Expected Output**:
```sql
stg_kategori_pajak   -- Cleaned kategori_pajak
stg_metode_bayar     -- Cleaned metode_bayar
stg_wajib_pajak      -- Cleaned wajib_pajak
stg_objek_pajak      -- Cleaned objek_pajak
stg_tagihan          -- Cleaned tagihan
stg_pembayaran       -- Cleaned pembayaran
```

---

### ⏳ TAHAP 4: Load to DWH (Star Schema)

**Target**: Load dari staging_area → dwh dengan star schema

**Tasks**:
- [ ] Create `dwh` database
- [ ] Create dimension tables:
  - `dim_waktu` (date dimension)
  - `dim_wajib_pajak` (wajib pajak master)
  - `dim_kategori_pajak` (jenis pajak + tarif)
  - `dim_objek_pajak` (objek pajak master)
  - `dim_metode_bayar` (payment methods)
- [ ] Create fact tables:
  - `fact_tagihan` (billing facts)
  - `fact_pembayaran` (payment facts)
- [ ] Create load task di DAG
- [ ] Implement SCD Type 1 for dimensions
- [ ] Test & verify star schema

**Expected Output**:
```
dwh/
├── Dimensions
│   ├── dim_waktu
│   ├── dim_wajib_pajak
│   ├── dim_kategori_pajak
│   ├── dim_objek_pajak
│   └── dim_metode_bayar
└── Facts
    ├── fact_tagihan
    └── fact_pembayaran
```

---

## 📊 Overall Architecture

```
                        ┌─────────────────────┐
                        │   MySQL db_dispenda │
                        └──────────┬──────────┘
                                   │
                                   ↓
                        ┌─────────────────────┐
                        │   TAHAP 1: API      │
                        │ (FastAPI, Port 8000)│
                        └──────────┬──────────┘
                                   │
                                   ↓ (Extract)
                        ┌─────────────────────┐
                        │  TAHAP 2: raw_data  │
                        │   (Mirror Tables)   │
                        └──────────┬──────────┘
                                   │
                                   ↓ (Transform)
                        ┌─────────────────────┐
                        │ TAHAP 3: staging_   │
                        │ area (Cleaned Data) │
                        └──────────┬──────────┘
                                   │
                                   ↓ (Load)
                        ┌─────────────────────┐
                        │ TAHAP 4: dwh        │
                        │  (Star Schema)      │
                        └─────────────────────┘

All coordinated by Apache Airflow DAG (ETL-Warehouse)
```

---

## 📁 Struktur Direktori

```
ETL airflow/
├── dispenda-api/              ← TAHAP 1: API
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── run_windows.ps1
│   ├── README.md
│   └── .venv/                 ← Virtual environment
│
├── dags/                       ← Airflow DAGs
│   ├── main.py                ← Orchestrator DAG
│   ├── dukcapil.py            ← Pipeline Dukcapil
│   ├── disnaker.py            ← Pipeline Disnaker
│   ├── dispenda.py            ← Pipeline Dispenda (to be updated)
│   └── pendidikan.py          ← Pipeline Pendidikan
│
├── db/                         ← Database dumps
│   └── db_dispenda.sql        ← Schema & initial data
│
├── TAHAP_IMPLEMENTASI.md      ← This file
├── TAHAP_1_SUMMARY.md         ← Tahap 1 details
├── TAHAP_1_VERIFIKASI.md      ← Tahap 1 verification
└── CONTOH_FETCH_API.py        ← Python client example
```

---

## 🚀 Quick Start

### 1. Jalankan API Dispenda (Tahap 1)

**Terminal 1:**
```powershell
cd "d:\MAGANG\project\ETL airflow\dispenda-api"

# Setup (one-time)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run
.\run_windows.ps1
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. Test API

**Terminal 2:**
```powershell
# Health check
curl http://localhost:8000/health

# Get data
curl "http://localhost:8000/api/kategori-pajak?page=1&limit=5"

# Interactive docs
start http://localhost:8000/docs
```

### 3. Test Python Client

**Terminal 2:**
```powershell
cd "d:\MAGANG\project\ETL airflow"
python CONTOH_FETCH_API.py
```

---

## 📈 Data Summary

### Database: db_dispenda

| Table | Records | API Endpoint |
|-------|---------|--------------|
| tb_kategori_pajak | 5 | `/api/kategori-pajak` |
| tb_metode_bayar | 12 | `/api/metode-bayar` |
| tb_wajib_pajak | 1,794 | `/api/wajib-pajak` |
| tb_objek_pajak | 1,813 | `/api/objek-pajak` |
| tb_tagihan | 1,813 | `/api/tagihan` |
| tb_pembayaran | 831 | `/api/pembayaran` |
| **TOTAL** | **7,868** | - |

---

## 🔗 Documentation Links

### Tahap 1 (Completed)
- [API README](dispenda-api/README.md) - Setup & usage
- [Verification Report](TAHAP_1_VERIFIKASI.md) - Test results
- [Summary](TAHAP_1_SUMMARY.md) - Complete overview
- [Python Example](CONTOH_FETCH_API.py) - Code example

### Main Project
- [README.md](README.md) - Project overview
- [PANDUAN.md](PANDUAN.md) - User guide
- [MEMORY.md](MEMORY.md) - Context & decisions

---

## ⚙️ Configuration

### Environment Variables (Tahap 1)

File: `dispenda-api/.env` atau set di terminal

```env
DISPENDA_DB_HOST=127.0.0.1
DISPENDA_DB_PORT=3306
DISPENDA_DB_USER=root
DISPENDA_DB_PASSWORD=YOUR_PASSWORD
DISPENDA_DB_NAME=db_dispenda
```

### Airflow Configuration (Tahap 2+)

File: `dags/main.py`

```python
PIPELINE_TASKS = [
    {
        "name": "dispenda",
        "create_tasks": create_dispenda_tasks,
        "api_base_url": "http://IP_KOMPUTER_API:8000/api",
    },
]
```

---

## 🧪 Testing Checklist

### Tahap 1 (API) - ✅ ALL PASSED

- [x] Server starts on port 8000
- [x] Database connection works
- [x] Health endpoint responds
- [x] All 6 data endpoints return data
- [x] Pagination works correctly
- [x] Error handling works
- [x] CORS enabled
- [x] Metadata endpoint works
- [x] Auto-pagination tested
- [x] Large batch (limit=500) tested

### Tahap 2 (Extract) - ⏳ TODO

- [ ] Create raw_data database
- [ ] Extract tasks execute successfully
- [ ] Data inserted to raw tables
- [ ] Metadata columns added
- [ ] Pagination handled correctly
- [ ] Duplicates handled
- [ ] Error recovery works

### Tahap 3 (Transform) - ⏳ TODO

- [ ] Create staging_area database
- [ ] Transform tasks execute
- [ ] Data cleaned & validated
- [ ] Whitespace trimmed
- [ ] Invalid values nullified
- [ ] Duplicates removed
- [ ] Data quality checks passed

### Tahap 4 (Load) - ⏳ TODO

- [ ] Create dwh database
- [ ] Dimensions created
- [ ] Facts created
- [ ] Star schema loaded
- [ ] SCD Type 1 working
- [ ] Lookups successful
- [ ] Data complete & accurate

---

## 🛠️ Troubleshooting

### Issue: API tidak bisa connect ke database

**Check**:
1. MySQL service running?
2. `db_dispenda` exists?
3. Credentials correct?
4. Port 3306 open?

**Solution**:
```powershell
# Test connection
python -c "
import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='db_dispenda')
print('Connected!')
conn.close()
"
```

### Issue: Port 8000 sudah dipakai

**Solution**:
```powershell
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Issue: API returns 404

**Check**:
- Endpoint name correct? (use hyphen, not underscore)
- Server running?
- URL syntax correct?

---

## 📅 Timeline

| Tahap | Estimasi | Status | Actual |
|-------|----------|--------|--------|
| Tahap 1: API | 1 hari | ✅ Done | 14 Nov 2026 |
| Tahap 2: Extract | 2 hari | ⏳ TBD | - |
| Tahap 3: Transform | 2 hari | ⏳ TBD | - |
| Tahap 4: Load | 2 hari | ⏳ TBD | - |
| **TOTAL** | **7 hari** | **29%** | - |

---

## 👥 Team & Contacts

| Role | Person | Notes |
|------|--------|-------|
| Developer | Fachrian Albar | - |
| Developer | Livia Safirani | - |
| Developer | Ulfiatul Khaira | - |
| Developer | Muhammad Nauval Qisti | - |
| Developer | Reyza Maulana Putra | - |

**Institution**: Dinas Komunikasi, Informatika dan Persandian Banda Aceh  
**University**: Politeknik Negeri Lhokseumawe - Program Studi Teknik Informatika  
**Period**: Semester 7, Tahun 2026

---

## 📞 Support

Untuk pertanyaan atau issue, lihat dokumentasi masing-masing tahap:
- Tahap 1 Issues → `TAHAP_1_VERIFIKASI.md`
- API Issues → `dispenda-api/README.md`
- Python Client → `CONTOH_FETCH_API.py`

---

**Last Updated**: 14 November 2026  
**Progress**: 1/4 Tahap Selesai ✅

---

Siap untuk Tahap 2? 🚀
