# Database Infrastruktur (db_infrastruktur)

**Pembuat:** Bryan  
**Topik:** jalan, jembatan, perumahan, pengairan, transportasi  
**Tanggal:** 2026-10-08

---

## Schema Database

### 1. tb_jalan
- id_jalan (PK)
- nama_jalan
- lokasi (kabupaten/kota, kecamatan)
- tipe_jalan (nasional, provinsi, kabupaten, desa)
- panjang_km
- lebar_m
- jenis_permukaan (aspal, beton, tanah, kerikil)
- kondisi (baik, sedang, rusak ringan, rusak berat)
- tahun_pembangunan
- tahun_pemeliharaan_terakhir
- nama_proyek
- kontraktor_pelaksana
- anggaran_rupiah
- status_proyek (operasional, dalam perbaikan, perencanaan)

### 2. tb_jembatan
- id_jembatan (PK)
- nama_jembatan
- lokasi
- panjang_m
- lebar_m
- tipe_jembatan (beton, baja, gantung, bailey, kayu)
- kapasitas_beban_ton
- kondisi (baik, sedang, rusak ringan, rusak berat)
- tahun_pembangunan
- tahun_pemeliharaan_terakhir
- nama_proyek
- kontraktor_pelaksana
- anggaran_rupiah
- status_proyek (operasional, dalam perbaikan, perencanaan)

### 3. tb_perumahan
- id_perumahan (PK)
- nama_proyek
- lokasi
- jenis_program (rumah rakyat, subsidi, relokasi bencana, kampung layak, rusunawa)
- jumlah_unit
- luas_area_m2
- status_kepemilikan (hak milik, sewa, hibah)
- tahun_pembangunan
- tahun_selesai
- persentase_penyelesaian
- pengelola
- anggaran_rupiah
- jumlah_penghuni
- kondisi_bangunan (baik, sedang, rusak)
- status_proyek (perencanaan, konstruksi, selesai, ditangguhkan)

### 4. tb_pengairan
- id_pengairan (PK)
- nama_aset
- jenis_aset (bendungan, saluran primer, saluran sekunder, embung, sumur bor)
- lokasi
- luas_layanan_ha
- panjang_saluran_km
- kapasitas_debit_m3
- kondisi (baik, sedang, rusak ringan, rusak berat)
- tahun_pembangunan
- tahun_pemeliharaan_terakhir
- nama_proyek
- kontraktor_pelaksana
- anggaran_rupiah
- status_operasional (beroperasi, tidak beroperasi, dalam perbaikan)

### 5. tb_transportasi
- id_transportasi (PK)
- nama_aset
- jenis_aset (terminal bus, pelabuhan, bandara, halte, pool, dermaga)
- lokasi
- kapasitas_penumpang
- luas_area_m2
- fasilitas
- kondisi (baik, sedang, rusak)
- tahun_pembangunan
- tahun_renovasi_terakhir
- pengelola
- anggaran_pembangunan_rupiah
- status_operasional (beroperasi, tutup sementara, dalam renovasi)

---

## Table Relationships

**Model:** Independent Tables (OLTP)

**Structure:**
```
tb_jalan (standalone)
tb_jembatan (standalone)
tb_perumahan (standalone)
tb_pengairan (standalone)
tb_transportasi (standalone)
```

**No Foreign Keys** between tables - each infrastructure type is independent.

**Rationale:**
- Project info embedded in each table (simpler, no joins required)
- Each infrastructure type has unique attributes
- Source database for ETL - simplicity over normalization
- No cross-references needed for phase 1

**Indexes (Optimized Composite Indexes):**
- Primary Keys: Auto-indexed
- Composite indexes for query optimization:
  - `idx_jalan_status_kondisi` (status_proyek, kondisi, tahun_pembangunan)
  - `idx_jalan_tahun_tipe` (tahun_pembangunan, tipe_jalan)
  - `idx_jembatan_status_kondisi` (status_proyek, kondisi, tahun_pembangunan)
  - `idx_jembatan_tahun_tipe` (tahun_pembangunan, tipe_jembatan)
  - `idx_perumahan_status` (status_proyek, persentase_penyelesaian)
  - `idx_perumahan_tahun_program` (tahun_pembangunan, jenis_program)
  - `idx_pengairan_status` (status_operasional, kondisi)
  - `idx_pengairan_tahun_jenis` (tahun_pembangunan, jenis_aset)
  - `idx_transportasi_status` (status_operasional, kondisi)
  - `idx_transportasi_tahun_jenis` (tahun_pembangunan, jenis_aset)

---

## Data Model

### 1. tb_jalan
```sql
id_jalan                    MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
nama_jalan                  VARCHAR(80) NOT NULL
lokasi                      VARCHAR(80) NOT NULL
tipe_jalan                  ENUM('nasional','provinsi','kabupaten','desa') NOT NULL
panjang_km                  DECIMAL(6,2) NOT NULL
lebar_m                     DECIMAL(4,2) NOT NULL
jenis_permukaan             ENUM('aspal','beton','tanah','kerikil') NOT NULL
kondisi                     ENUM('baik','sedang','rusak ringan','rusak berat') NOT NULL
tahun_pembangunan           YEAR NOT NULL
tahun_pemeliharaan_terakhir YEAR NULL
nama_proyek                 VARCHAR(120) NULL
kontraktor_pelaksana        VARCHAR(80) NULL
anggaran_rupiah             BIGINT UNSIGNED NULL
status_proyek               ENUM('operasional','dalam perbaikan','perencanaan') NOT NULL DEFAULT 'operasional'
created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

INDEX idx_jalan_status_kondisi (status_proyek, kondisi, tahun_pembangunan)
INDEX idx_jalan_tahun_tipe (tahun_pembangunan, tipe_jalan)
```

### 2. tb_jembatan
```sql
id_jembatan                 MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
nama_jembatan               VARCHAR(80) NOT NULL
lokasi                      VARCHAR(80) NOT NULL
panjang_m                   DECIMAL(6,2) NOT NULL
lebar_m                     DECIMAL(4,2) NOT NULL
tipe_jembatan               ENUM('beton','baja','gantung','bailey','kayu') NOT NULL
kapasitas_beban_ton         TINYINT UNSIGNED NOT NULL
kondisi                     ENUM('baik','sedang','rusak ringan','rusak berat') NOT NULL
tahun_pembangunan           YEAR NOT NULL
tahun_pemeliharaan_terakhir YEAR NULL
nama_proyek                 VARCHAR(120) NULL
kontraktor_pelaksana        VARCHAR(80) NULL
anggaran_rupiah             BIGINT UNSIGNED NULL
status_proyek               ENUM('operasional','dalam perbaikan','perencanaan') NOT NULL DEFAULT 'operasional'
created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

INDEX idx_jembatan_status_kondisi (status_proyek, kondisi, tahun_pembangunan)
INDEX idx_jembatan_tahun_tipe (tahun_pembangunan, tipe_jembatan)
```

### 3. tb_perumahan
```sql
id_perumahan                MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
nama_proyek                 VARCHAR(120) NOT NULL
lokasi                      VARCHAR(80) NOT NULL
jenis_program               ENUM('rumah rakyat','subsidi','relokasi bencana','kampung layak','rusunawa') NOT NULL
jumlah_unit                 SMALLINT UNSIGNED NOT NULL
luas_area_m2                DECIMAL(8,2) NULL
status_kepemilikan          ENUM('hak milik','sewa','hibah') NOT NULL
tahun_pembangunan           YEAR NOT NULL
tahun_selesai               YEAR NULL
persentase_penyelesaian     TINYINT UNSIGNED NOT NULL DEFAULT 0
pengelola                   VARCHAR(80) NULL
anggaran_rupiah             BIGINT UNSIGNED NOT NULL
jumlah_penghuni             MEDIUMINT UNSIGNED NULL
kondisi_bangunan            ENUM('baik','sedang','rusak') NOT NULL
status_proyek               ENUM('perencanaan','konstruksi','selesai','ditangguhkan') NOT NULL
created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

INDEX idx_perumahan_status (status_proyek, persentase_penyelesaian)
INDEX idx_perumahan_tahun_program (tahun_pembangunan, jenis_program)
```

### 4. tb_pengairan
```sql
id_pengairan                MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
nama_aset                   VARCHAR(80) NOT NULL
jenis_aset                  ENUM('bendungan','saluran primer','saluran sekunder','embung','sumur bor') NOT NULL
lokasi                      VARCHAR(80) NOT NULL
luas_layanan_ha             DECIMAL(8,2) NULL
panjang_saluran_km          DECIMAL(6,2) NULL
kapasitas_debit_m3          DECIMAL(8,2) NULL
kondisi                     ENUM('baik','sedang','rusak ringan','rusak berat') NOT NULL
tahun_pembangunan           YEAR NOT NULL
tahun_pemeliharaan_terakhir YEAR NULL
nama_proyek                 VARCHAR(120) NULL
kontraktor_pelaksana        VARCHAR(80) NULL
anggaran_rupiah             BIGINT UNSIGNED NULL
status_operasional          ENUM('beroperasi','tidak beroperasi','dalam perbaikan') NOT NULL
created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

INDEX idx_pengairan_status (status_operasional, kondisi)
INDEX idx_pengairan_tahun_jenis (tahun_pembangunan, jenis_aset)
```

### 5. tb_transportasi
```sql
id_transportasi             MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
nama_aset                   VARCHAR(80) NOT NULL
jenis_aset                  ENUM('terminal bus','pelabuhan','bandara','halte','pool','dermaga') NOT NULL
lokasi                      VARCHAR(80) NOT NULL
kapasitas_penumpang         MEDIUMINT UNSIGNED NULL
luas_area_m2                DECIMAL(8,2) NULL
fasilitas                   VARCHAR(120) NULL
kondisi                     ENUM('baik','sedang','rusak') NOT NULL
tahun_pembangunan           YEAR NOT NULL
tahun_renovasi_terakhir     YEAR NULL
pengelola                   VARCHAR(80) NULL
anggaran_pembangunan_rupiah BIGINT UNSIGNED NULL
status_operasional          ENUM('beroperasi','tutup sementara','dalam renovasi') NOT NULL
created_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
updated_at                  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

INDEX idx_transportasi_status (status_operasional, kondisi)
INDEX idx_transportasi_tahun_jenis (tahun_pembangunan, jenis_aset)
```

**Data Type Decisions (Optimized):**
- **YEAR** untuk tahun (compact, 1-byte storage)
- **DECIMAL** dengan precision sesuai kebutuhan:
  - `DECIMAL(6,2)` untuk panjang_km (up to 9,999.99 km)
  - `DECIMAL(4,2)` untuk lebar_m (up to 99.99 m)
  - `DECIMAL(8,2)` untuk luas area/layanan (up to 999,999.99)
- **BIGINT UNSIGNED** untuk currency (rupiah, handles trillions, non-negative)
- **TINYINT UNSIGNED** untuk persentase (0-100) dan kapasitas beban ton jembatan (0-255 ton, 1 byte)
- **SMALLINT UNSIGNED** untuk kapasitas unit perumahan (up to 65,535, 2 bytes)
- **MEDIUMINT UNSIGNED** untuk primary keys (up to 16.7M records, 3 bytes) dan kapasitas penumpang/penghuni
- **ENUM** untuk status/tipe (1 byte, built-in validation)
- **VARCHAR** dengan size optimal:
  - `VARCHAR(80)` untuk nama aset/lokasi/kontraktor/pengelola
  - `VARCHAR(120)` untuk nama proyek dan fasilitas (1-byte length prefix, hemat memori buffer)
- **NULL/NOT NULL** berdasarkan business logic (data kritis vs optional)
- **DEFAULT values** untuk workflow stages dan persentase
- **Metadata columns** (created_at, updated_at) untuk audit trail

**Index Strategy (Composite Indexes):**
- Composite indexes untuk common query patterns (status + kondisi + tahun)
- Support leftmost prefix optimization
- No standalone lokasi index (too large for VARCHAR index)
- Faster filtered queries, reduced index overhead

---

## Sample Data Summary

**Target Records:**
- ~20-50 road segments (ruas jalan across Aceh)
- ~10-20 bridges (jembatan strategis)
- ~15 housing projects (perumahan rakyat, rusunawa)
- ~10-15 irrigation assets (bendungan, saluran irigasi)
- ~8-12 transportation hubs (terminal, pelabuhan)

**Lokasi Real di Aceh:**
- Banda Aceh, Aceh Besar, Aceh Utara, Aceh Timur
- Pidie, Bireuen, Lhokseumawe
- Aceh Tengah, Gayo Lues, Aceh Barat, Simeulue

**Status Distribution:**
- Mix of operational, dalam perbaikan, dan perencanaan
- Various kondisi: baik (60%), sedang (25%), rusak (15%)
- Project years: 2015-2026 range

---

## FastAPI Endpoints

**Directory:** `infrastruktur-api/` (to be created)

**Planned Endpoints:**
- `GET /` - Service information
- `GET /health` - Database connection health check
- `GET /api/tables` - List all available tables and endpoints
- `GET /api/jalan` - Roads data
- `GET /api/jembatan` - Bridges data
- `GET /api/perumahan` - Housing data
- `GET /api/pengairan` - Irrigation data
- `GET /api/transportasi` - Transportation data
- `GET /docs` - Swagger UI interactive documentation

**Features:**
- Pagination support (`?page=N&limit=M`, max 1000 records per request)
- JSON-safe conversion (datetime, decimal, bytes)
- CORS enabled for all origins
- Read-only API (GET methods only)
- Environment variable configuration via `.env`

**Configuration (Environment Variables):**
- `INFRASTRUKTUR_DB_HOST` - MySQL host (default: 127.0.0.1)
- `INFRASTRUKTUR_DB_PORT` - MySQL port (default: 3306)
- `INFRASTRUKTUR_DB_USER` - MySQL username (default: root)
- `INFRASTRUKTUR_DB_PASSWORD` - MySQL password
- `INFRASTRUKTUR_DB_NAME` - Database name (default: db_infrastruktur)

---

## Progress

- [x] Schema design
- [x] Table relationships
- [x] Data model (optimized for efficiency)
- [x] SQL schema file (create_db_infrastruktur.sql)
- [x] SQL dump file with sample data (db_infrastruktur.sql)
- [x] Review SQL schema & sample data (TODO upon return)
- [x] FastAPI endpoints (infrastruktur-api/)
- [x] Airflow DAG (infrastruktur.py)
- [x] Integration with main.py
- [x] Testing

**Last Updated:** 2026-10-13
