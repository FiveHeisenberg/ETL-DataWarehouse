# Database Ketangguhan Bencana (db_ketaben)

**Pembuat:** Bryan  
**Topik:** bencana, dampak, bantuan, rehabilitasi, rekonstruksi  
**Tanggal:** 2026-10-06

---

## Schema Database

### 1. tb_bencana
- id_bencana (PK)
- jenis_bencana (gempa bumi, banjir, tsunami, tanah longsor, kebakaran, angin puting beliung)
- lokasi (kabupaten/kota, kecamatan)
- deskripsi_kejadian
- tanggal_kejadian
- tingkat_keparahan (ringan, sedang, berat)
- status_tanggap (tanggap darurat, pemulihan, selesai)

### 2. tb_korban_bencana
- id_korban (PK)
- id_bencana (FK)
- jenis_korban (meninggal, luka berat, luka ringan, hilang, mengungsi)
- jumlah_korban
- keterangan (optional - lokasi pengungsian, nama RS)

### 3. tb_kerusakan_bencana
- id_kerusakan (PK)
- id_bencana (FK)
- jenis_objek (rumah, sekolah, puskesmas, masjid, jalan, jembatan, irigasi)
- tingkat_kerusakan (rusak berat, rusak ringan, rusak total)
- jumlah_unit
- estimasi_kerugian_rupiah
- lokasi_kerusakan

### 4. tb_bantuan
- id_bantuan (PK)
- id_bencana (FK)
- jenis_bantuan (logistik, medis, uang tunai, tempat tinggal sementara, sembako, selimut, obat-obatan)
- sumber_bantuan (BNPB, BPBD Aceh, donor internasional, pemerintah pusat, masyarakat, NGO)
- jumlah_bantuan
- satuan (paket, unit, rupiah, kg, box)
- penerima_bantuan (nama pengungsi/kelompok/desa)
- tanggal_distribusi
- lokasi_distribusi

### 5. tb_rehabilitasi
- id_rehabilitasi (PK)
- id_bencana (FK)
- jenis_rehabilitasi (perbaikan rumah, infrastruktur publik, trauma healing, pemulihan ekonomi, pemberdayaan masyarakat)
- lokasi
- deskripsi_kegiatan
- tanggal_mulai
- tanggal_selesai
- anggaran_rupiah
- sumber_dana (APBA, APBN, donor, hibah)
- status_pelaksanaan (perencanaan, dalam proses, selesai, tertunda)
- persentase_penyelesaian

### 6. tb_rekonstruksi
- id_rekonstruksi (PK)
- id_bencana (FK)
- nama_proyek
- jenis_pembangunan (rumah permanen, sekolah, puskesmas, jalan, jembatan, tempat ibadah, pasar, kantor)
- lokasi
- anggaran_rupiah
- sumber_dana (APBA, APBN, donor, CSR)
- kontraktor_pelaksana
- tanggal_mulai
- tanggal_target_selesai
- tanggal_selesai_aktual
- persentase_penyelesaian
- status_proyek (perencanaan, tender, konstruksi, selesai, ditangguhkan)

---

## Table Relationships

**Model:** Normalized Relational Database (OLTP)

**Structure:**
```
tb_bencana (1) ──< (N) tb_korban_bencana
tb_bencana (1) ──< (N) tb_kerusakan_bencana
tb_bencana (1) ──< (N) tb_bantuan
tb_bencana (1) ──< (N) tb_rehabilitasi
tb_bencana (1) ──< (N) tb_rekonstruksi
```

**Parent Table:** `tb_bencana` (master table untuk kejadian bencana)

**Child Tables:** Semua tabel lainnya memiliki foreign key `id_bencana` yang reference ke `tb_bencana.id_bencana`

**Foreign Key Constraints:**
```sql
FOREIGN KEY (id_bencana) REFERENCES tb_bencana(id_bencana)
  ON DELETE RESTRICT
  ON UPDATE CASCADE
```

**Rationale:**
- `ON DELETE RESTRICT`: Mencegah penghapusan data bencana jika masih ada data terkait (melindungi data historis)
- `ON UPDATE CASCADE`: Auto-update FK jika PK berubah (untuk maintenance)
- No cross-references antar child tables (keep simple untuk phase 1)

**Indexes:**
- Primary Keys: Auto-indexed
- Foreign Keys: `idx_[table]_bencana` pada kolom `id_bencana`
- Performance indexes:
  - `idx_bencana_tanggal` pada `tb_bencana.tanggal_kejadian`
  - `idx_bencana_lokasi` pada `tb_bencana.lokasi`
  - `idx_bencana_jenis` pada `tb_bencana.jenis_bencana`
  - `idx_bantuan_tanggal` pada `tb_bantuan.tanggal_distribusi`
  - `idx_rehabilitasi_status` pada `tb_rehabilitasi.status_pelaksanaan`
  - `idx_rekonstruksi_status` pada `tb_rekonstruksi.status_proyek`

---

## Data Model

### 1. tb_bencana
```sql
id_bencana          INT AUTO_INCREMENT PRIMARY KEY
jenis_bencana       VARCHAR(100) NOT NULL
lokasi              VARCHAR(150) NOT NULL
deskripsi_kejadian  TEXT NULL
tanggal_kejadian    DATETIME NOT NULL
tingkat_keparahan   ENUM('ringan','sedang','berat') NOT NULL
status_tanggap      ENUM('tanggap darurat','pemulihan','selesai') NOT NULL DEFAULT 'tanggap darurat'
created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 2. tb_korban_bencana
```sql
id_korban       INT AUTO_INCREMENT PRIMARY KEY
id_bencana      INT NOT NULL
jenis_korban    ENUM('meninggal','luka berat','luka ringan','hilang','mengungsi') NOT NULL
jumlah_korban   INT UNSIGNED NOT NULL
keterangan      VARCHAR(100) NULL
created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
FOREIGN KEY (id_bencana) REFERENCES tb_bencana(id_bencana) ON DELETE RESTRICT ON UPDATE CASCADE
```

### 3. tb_kerusakan_bencana
```sql
id_kerusakan              INT AUTO_INCREMENT PRIMARY KEY
id_bencana                INT NOT NULL
jenis_objek               VARCHAR(100) NOT NULL
tingkat_kerusakan         ENUM('rusak ringan','rusak berat','rusak total') NOT NULL
jumlah_unit               INT UNSIGNED NOT NULL
estimasi_kerugian_rupiah  BIGINT NULL
lokasi_kerusakan          VARCHAR(150) NOT NULL
created_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
FOREIGN KEY (id_bencana) REFERENCES tb_bencana(id_bencana) ON DELETE RESTRICT ON UPDATE CASCADE
```

### 4. tb_bantuan
```sql
id_bantuan          INT AUTO_INCREMENT PRIMARY KEY
id_bencana          INT NOT NULL
jenis_bantuan       VARCHAR(150) NOT NULL
sumber_bantuan      VARCHAR(150) NOT NULL
jumlah_bantuan      VARCHAR(15) NOT NULL
satuan              VARCHAR(50) NOT NULL
penerima_bantuan    VARCHAR(200) NULL
tanggal_distribusi  DATETIME NOT NULL
lokasi_distribusi   VARCHAR(150) NOT NULL
created_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
FOREIGN KEY (id_bencana) REFERENCES tb_bencana(id_bencana) ON DELETE RESTRICT ON UPDATE CASCADE
```

### 5. tb_rehabilitasi
```sql
id_rehabilitasi         INT AUTO_INCREMENT PRIMARY KEY
id_bencana              INT NOT NULL
jenis_rehabilitasi      VARCHAR(150) NOT NULL
lokasi                  VARCHAR(150) NOT NULL
deskripsi_kegiatan      TEXT NULL
tanggal_mulai           DATETIME NOT NULL
tanggal_selesai         DATETIME NULL
anggaran_rupiah         BIGINT NOT NULL
sumber_dana             VARCHAR(100) NOT NULL
status_pelaksanaan      ENUM('perencanaan','dalam proses','selesai','tertunda') NOT NULL DEFAULT 'perencanaan'
persentase_penyelesaian TINYINT UNSIGNED NOT NULL DEFAULT 0
created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
FOREIGN KEY (id_bencana) REFERENCES tb_bencana(id_bencana) ON DELETE RESTRICT ON UPDATE CASCADE
```

### 6. tb_rekonstruksi
```sql
id_rekonstruksi         INT AUTO_INCREMENT PRIMARY KEY
id_bencana              INT NOT NULL
nama_proyek             VARCHAR(200) NOT NULL
jenis_pembangunan       VARCHAR(150) NOT NULL
lokasi                  VARCHAR(150) NOT NULL
anggaran_rupiah         BIGINT NOT NULL
sumber_dana             VARCHAR(100) NOT NULL
kontraktor_pelaksana    VARCHAR(200) NULL
tanggal_mulai           DATETIME NOT NULL
tanggal_target_selesai  DATETIME NOT NULL
tanggal_selesai_aktual  DATETIME NULL
persentase_penyelesaian TINYINT UNSIGNED NOT NULL DEFAULT 0
status_proyek           ENUM('perencanaan','tender','konstruksi','selesai','ditangguhkan') NOT NULL DEFAULT 'perencanaan'
created_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
FOREIGN KEY (id_bencana) REFERENCES tb_bencana(id_bencana) ON DELETE RESTRICT ON UPDATE CASCADE
```

**Data Type Decisions:**
- **DATETIME** untuk semua timestamp (bukan DATE) - lebih detail
- **BIGINT** untuk currency (rupiah, no decimals)
- **ENUM** untuk status/workflow yang fixed
- **VARCHAR** untuk jenis/tipe yang dinamis
- **INT UNSIGNED / TINYINT UNSIGNED** untuk angka yang tidak boleh negatif
- **TEXT** untuk deskripsi panjang
- **NULL/NOT NULL** berdasarkan business logic (data kritis vs optional)
- **DEFAULT values** untuk workflow stages dan persentase
- **Metadata columns** (created_at, updated_at) untuk audit trail

---

---

## Sample Data Summary

**File:** `db/db_ketaben.sql`

**Records Created:**
- 10 kejadian bencana (2024-2026)
  - 3 gempa bumi (Pidie Jaya, Aceh Barat, Simeulue)
  - 3 banjir (Aceh Utara, Aceh Besar, Aceh Timur)
  - 2 tanah longsor (Aceh Tengah, Gayo Lues)
  - 1 kebakaran (Banda Aceh - Pasar Peunayong)
  - 1 angin puting beliung (Bireuen)
- 33 records korban bencana (meninggal, luka berat/ringan, hilang, mengungsi)
- 41 records kerusakan (rumah, sekolah, masjid, jalan, jembatan, irigasi, dll)
- 35 records bantuan (sembako, tenda, obat, uang tunai, air bersih, selimut)
- 23 records rehabilitasi (perbaikan rumah, trauma healing, infrastruktur, pemulihan ekonomi)
- 20 records rekonstruksi (rumah permanen, jalan, jembatan, sekolah, pasar)

**Lokasi Real di Aceh:**
- Pidie Jaya, Aceh Utara (Lhoksukon), Aceh Tengah (Silih Nara, Takengon)
- Banda Aceh (Baiturrahman, Peunayong), Aceh Besar (Indrapuri)
- Aceh Barat (Woyla), Bireuen (Peusangan), Aceh Timur (Idi Rayeuk)
- Gayo Lues (Blangkejeren), Simeulue (Teluk Dalam)

**Status Distribution:**
- Bencana 2024-awal 2025: status "selesai" (sudah melewati siklus tanggap darurat-pemulihan)
- Bencana pertengahan 2025-2026: status "pemulihan" (masih dalam proses)
- Bencana terbaru (Gempa Simeulue 25 Agustus 2026): status "tanggap darurat"

---

## FastAPI Endpoints

**Directory:** `ketaben-api/`

**Files Created:**
- `main.py` - FastAPI application dengan 6 table endpoints
- `requirements.txt` - Dependencies (fastapi, uvicorn, pymysql, python-dotenv)
- `README.md` - Complete documentation
- `.env.example` - Database configuration template
- `run_windows.ps1` - PowerShell runner script
- `start_ketaben_api.bat` - Batch file runner

**API Endpoints:**
- `GET /` - Service information
- `GET /health` - Database connection health check
- `GET /api/tables` - List all available tables and endpoints
- `GET /api/bencana` - Kejadian bencana data
- `GET /api/korban-bencana` - Korban bencana data
- `GET /api/kerusakan-bencana` - Kerusakan bencana data
- `GET /api/bantuan` - Bantuan data
- `GET /api/rehabilitasi` - Rehabilitasi data
- `GET /api/rekonstruksi` - Rekonstruksi data
- `GET /docs` - Swagger UI interactive documentation

**Features:**
- Pagination support (`?page=N&limit=M`, max 1000 records per request)
- JSON-safe conversion (datetime, decimal, bytes)
- CORS enabled for all origins
- Read-only API (GET methods only)
- Environment variable configuration via `.env`

**Configuration (Environment Variables):**
- `KETABEN_DB_HOST` - MySQL host (default: 127.0.0.1)
- `KETABEN_DB_PORT` - MySQL port (default: 3306)
- `KETABEN_DB_USER` - MySQL username (default: root)
- `KETABEN_DB_PASSWORD` - MySQL password
- `KETABEN_DB_NAME` - Database name (default: db_ketaben)

**Running the API:**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure database
cp .env.example .env
# Edit .env with your credentials

# Run (Windows)
.\run_windows.ps1
# or
start_ketaben_api.bat

# Run (Linux/Mac)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**API Base URL:** `http://localhost:8000` (default)

---

## Progress

- [x] Schema design
- [x] Table relationships
- [x] Data model
- [x] SQL dump file with sample data
- [x] FastAPI endpoints
- [x] Airflow DAG (ketangguhanbencana.py)
- [x] Integration with main.py
- [x] Testing

**Last Updated:** 2026-10-13
