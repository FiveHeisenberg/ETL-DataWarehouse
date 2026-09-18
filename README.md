<<<<<<< HEAD
# ETL Aceh DataWarehouse

> Proyek magang untuk mengintegrasikan data antar dinas ke dalam satu Data Warehouse terpusat, dibangun dengan Apache Airflow (Astro Runtime) dan MySQL.

## Daftar Isi

- [Deskripsi Proyek](#deskripsi-proyek)
- [Tim & Identitas Magang](#tim--identitas-magang)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Alur ETL](#alur-etl)
- [Sumber Data](#sumber-data)
- [Model Data Target](#model-data-target)
- [Struktur Direktori](#struktur-direktori)
- [Teknologi yang Digunakan](#teknologi-yang-digunakan)
- [Cara Menjalankan](#cara-menjalankan)
- [Menambah Sumber Data Baru](#menambah-sumber-data-baru)

---

## Deskripsi Proyek

**ETL Aceh DataWarehouse** adalah proyek magang yang bertujuan untuk **mengintegrasikan data antar dinas** di lingkungan Pemerintah Kota (Pemko) Banda Aceh ke dalam satu Data Warehouse terpusat.

Setiap dinas menyimpan datanya pada basis data MySQL masing-masing, yaitu:

- **Dukcapil** — data kependudukan
- **Disnaker** — data ketenagakerjaan
- **Dispenda** — data pajak daerah
- **Dinas Pendidikan** — data pendidikan

Data dari setiap basis data diekspos melalui **REST API** (FastAPI), kemudian diambil oleh **Apache Airflow** melalui proses ETL dengan urutan:

```
REST API  ->  raw_data  ->  staging_area  ->  dwh (star schema)
```

Pada tahap **ekstraksi**, data API disalin apa adanya (mirror) ke database `raw_data` lengkap dengan metadata sumber (`sumber_database` dan `waktu_ekstraksi`). Pada tahap **transformasi**, data dibersihkan, distandarisasi, dan divalidasi ke database `staging_area` (misalnya validasi NIK 16 digit, normalisasi format tanggal, standarisasi nilai enum, penghilangan duplikat). Terakhir, data **dimuat** ke dalam Data Warehouse `dwh` dengan model **star schema** (tabel `dim_*` dan `fact_*`) yang siap digunakan untuk pelaporan dan analisis.

## Tim & Identitas Magang

| Anggota | NIM |
| --- | --- |
| Fachrian Albar | — |
| Livia Safirani | — |
| Ulfiatul Khaira | — |
| Muhammad Nauval Qisti | — |
| Reyza Maulana Putra | — |

- **Institusi**: Dinas Komunikasi, Informatika dan Persandian Banda Aceh
- **Perguruan Tinggi**: Politeknik Negeri Lhokseumawe — Program Studi Teknik Informatika
- **Periode**: Semester 7, Tahun 2026

## Arsitektur Sistem

```text
                         +-------------------------+
                         |  Pemerintah Kota        |
                         |  Banda Aceh             |
                         +------------+------------+
                                      |
        +-----------------------------+-----------------------------+
        |                             |                             |
   +----v----+                  +-----v-----+                 +----v----+
   | Dukcapil|                  |  Disnaker |                 | Dispenda|
   |  MySQL  |                  |   MySQL   |                 |  MySQL  |
   +----+----+                  +-----+-----+                 +----+----+
        |                             |                             |
        |   +----------------------+  |         +----------------+  |
        +-->|  REST API (FastAPI)  |--+-------->| REST API Fast  |--+
            | 192.168.222.152:8000 |    ...     | 192.168.222.71 |  ...
            +----------+-----------+            +----------------+
                       |
                       v        D E   x            E  t  r  a  c  t
             +---------------------------+
             |     Airflow (Astro)       |
             |  DAG: ETL-Warehouse       |
             +-------------+-------------+
                           |
                  +--------v--------+
                  |    raw_data     |   Data mentah (mirror API)
                  +--------+--------+
                           |  Transform & Validasi
                  +--------v--------+
                  |  staging_area   |   Data bersih & tervalidasi
                  +--------+--------+
                           |  Load
                  +--------v--------+
                  |       dwh        |   Star schema (dim_* & fact_*)
                  |  (Data Warehouse)|
                  +-----------------+
```

## Alur ETL

Setiap pipeline sumber data dijalankan oleh **satu DAG terpusat** bernama `ETL-Warehouse` (lih. `dags/main.py`). DAG tersebut mengorkestrasi pipeline dari keempat dinas secara berurutan.

| Tahap | Tujuan | Deskripsi |
| --- | --- | --- |
| **Extract** | `REST API` → `raw_data` | Menarik seluruh data dari setiap endpoint API (paginasi 100 record/batch), kemudian `DROP` & `CREATE` tabel `raw_<tabel>` mengikuti skema kolom API, lalu insert data dalam batch 1000 baris. Setiap tabel ditambah kolom `sumber_database` (URL API) dan `waktu_ekstraksi` (WIB). |
| **Transform** | `raw_data` → `staging_area` | Membuat tabel `stg_<tabel>` hasil pembersihan data: `TRIM`, `REGEXP_REPLACE`, `NULLIF`, `DISTINCT`, standarisasi enum (mis. `PRIA/L` → `L`), validasi NIK 16 digit, normalisasi tanggal, dan filter nilai yang tidak valid. |
| **Load** | `staging_area` → `dwh` | Membuat (jika belum ada) tabel dimensi & fakta, mengisi `dim_waktu`, memuat dimension dengan `INSERT ... ON DUPLICATE KEY UPDATE` (idempotent / SCD type 1), lalu memuat fact table dengan look-up ke dimension. |

Struktur DAG `ETL-Warehouse`:

```text
create_raw_database >> create_staging_database >> create_dwh_database
    >> extract_to_raw_dukcapil >> transform_staging_dukcapil  >> load_to_dwh_dukcapil
    >> extract_to_raw_disnaker >> transform_staging_disnaker
    >> extract_to_raw_dispenda >> transform_staging_dispenda  >> load_to_dwh_dispenda
    >> extract_to_raw_pendidikan >> transform_staging_pendidikan
```

Saat ini pipeline **Disnaker** dan **Pendidikan** berjalan sampai tahap *staging_area*; sedangkan **Dukcapil** dan **Dispenda** sudah mencapai Data Warehouse (`dwh`).

## Sumber Data

Keempat sumber data diekspos melalui REST API (FastAPI) yang membaca langsung dari basis data MySQL masing-masing dinas.

### Dukcapil (Kependudukan) — `http://192.168.222.152:8000/api`

| Endpoint | Tabel Sumber |
| --- | --- |
| `/agama` | `tb_agama` |
| `/alamat` | `tb_alamat` |
| `/desa` | `tb_desa` |
| `/kabupaten-kota` | `tb_kabupaten_kota` |
| `/kartu-keluarga` | `tb_kartu_keluarga` |
| `/kecamatan` | `tb_kecamatan` |
| `/penduduk` | `tb_penduduk` |
| `/provinsi` | `tb_provinsi` |
| `/status-penduduk` | `tb_status_penduduk` |
| `/status-perkawinan` | `tb_status_perkawinan` |

### Disnaker (Ketenagakerjaan) — `http://192.168.222.71:8000/api`

| Endpoint | Tabel Sumber |
| --- | --- |
| `/kasus-hi` | `tb_kasus_hi` |
| `/lowongan` | `tb_lowongan` |
| `/pelatihan-blk` | `tb_pelatihan_blk` |
| `/penduduk-pencaker` | `tb_penduduk_pencaker` |
| `/penempatan` | `tb_penempatan` |
| `/perusahaan` | `tb_perusahaan` |
| `/peserta-pelatihan` | `tb_peserta_pelatihan` |

### Dispenda (Pajak Daerah) — `http://192.168.222.154:8000/api`

| Endpoint | Tabel Sumber |
| --- | --- |
| `/wajib-pajak` | `tb_wajib_pajak` |
| `/kategori-pajak` | `tb_kategori_pajak` |
| `/objek-pajak` | `tb_objek_pajak` |
| `/tagihan` | `tb_tagihan` |
| `/pembayaran` | `tb_pembayaran` |

### Pendidikan — `http://192.168.222.180:5000/api`

| Endpoint | Tabel Sumber |
| --- | --- |
| `/waktu` | `tb_waktu` |
| `/sekolah` | `tb_sekolah` |
| `/ptk` | `tb_ptk` |
| `/siswa` | `tb_siswa` |
| `/sarana` | `tb_sarana` |
| `/pendidikan` | `tb_pendidikan` |

### Kontrak API

Semua endpoint API bersifat *read-only* dan mendukung paginasi `?page=1&limit=100`. Respon mengikuti format:

```json
{
  "success": true,
  "data": [ { ... } ],
  "pagination": {
    "current_page": 1,
    "per_page": 100,
    "total": 1000,
    "total_pages": 10,
    "has_next": true
  }
}
```

## Model Data Target

Data Warehouse `dwh` menggunakan **star schema** dengan tabel dimensi (`dim_*`) dan fakta (`fact_*`).

### Kependudukan (Dukcapil) — *snapshot harian per penduduk*

| Tabel | Keterangan |
| --- | --- |
| `dim_waktu` | Dimensi tanggal (key `YYYYMMDD`) |
| `dim_agama` | Dimensi agama |
| `dim_status_perkawinan` | Dimensi status perkawinan |
| `dim_status_penduduk` | Dimensi status penduduk (hidup/mati) |
| `dim_kartu_keluarga` | Dimensi Kartu Keluarga |
| `dim_wilayah` | Dimensi wilayah denormalisasi: alamat → desa → kecamatan → kabupaten/kota → provinsi |
| `dim_penduduk` | Dimensi penduduk (unik per NIK) |
| `fact_penduduk` | Fakta snapshot penduduk (1 baris/penduduk/hari) + perhitungan `umur` |

### Pajak Daerah (Dispenda)

| Tabel | Keterangan |
| --- | --- |
| `dim_waktu` | Dimensi tanggal (key `YYYYMMDD`) |
| `dim_wajib_pajak` | Dimensi wajib pajak (unik per NIK) |
| `dim_kategori_pajak` | Dimensi jenis pajak + tarif |
| `dim_objek_pajak` | Dimensi objek pajak |
| `dim_metode_bayar` | Dimensi metode pembayaran |
| `fact_tagihan` | Fakta tagihan: 1 tagihan per objek pajak per tahun |
| `fact_pembayaran` | Fakta pembayaran: 1 pembayaran per transaksi (termasuk denda & total bayar) |

## Struktur Direktori

```text
ETL 5 DATABASE/
├── .astro/                    # Konfigurasi & integritas DAG Astronomer
├── dags/                      # Definisi DAG Airflow
│   ├── main.py                # DAG utama "ETL-Warehouse" (orchestrator)
│   ├── dukcapil.py            # Pipeline kependudukan
│   ├── disnaker.py            # Pipeline ketenagakerjaan
│   ├── dispenda.py            # Pipeline pajak daerah
│   └── pendidikan.py          # Pipeline pendidikan
├── db/                        # Skema & data sumber (dump SQL)
│   ├── db_dukcapil.sql
│   ├── db_disnaker.sql
│   ├── db_dispenda.sql
│   └── db_pendidikan.sql
├── disnaker-api/              # Contoh REST API (FastAPI) untuk db_disnaker
│   ├── main.py
│   ├── requirements.txt
│   ├── run_windows.ps1
│   └── .env.example
├── include/                   # File tambahan (kosong)
├── plugins/                   # Plugin kustom Airflow (kosong)
├── tests/dags/                # Unit test DAG
├── Dockerfile                 # Image Astro Runtime
├── packages.txt               # Paket OS tambahan
├── requirements.txt           # Paket Python tambahan (mysql provider)
└── airflow_settings.yaml      # Koneksi/Variabel/Pool lokal Airflow
```

## Teknologi yang Digunakan

| Komponen | Teknologi |
| --- | --- |
| Orkestrasi ETL | Apache Airflow (Astro Runtime `3.3-7`) |
| Task API    | Airflow TaskFlow API (`@dag`, `@task`) |
| Database Warehouse | MySQL 8 (charset `utf8mb4`, collation `utf8mb4_0900_ai_ci`) |
| REST API Sumber Data | FastAPI + Uvicorn |
| Driver MySQL | PyMySQL (`apache-airflow-providers-mysql`) |
| HTTP Client | `requests` |
| Waktu | `pendulum` (timezone `Asia/Jakarta`) |

## Cara Menjalankan

### 1. Prasyarat

- Docker Desktop berjalan
- Astronomer CLI (`astro`)
- MySQL 8 sebagai target Data Warehouse (tersambung jaringannya ke mesin Airflow)
- REST API keempat dinas dapat diakses dari mesin Airflow (lihat [Sumber Data](#sumber-data))

### 2. Menjalankan REST API Sumber Data

Contoh untuk **Disnaker** (folder `disnaker-api/`), jalankan pada komputer yang menyimpan `db_disnaker`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```powershell
$env:DISNAKER_DB_HOST="127.0.0.1"
$env:DISNAKER_DB_PORT="3306"
$env:DISNAKER_DB_USER="root"
$env:DISNAKER_DB_PASSWORD="PASSWORD_MYSQL"
$env:DISNAKER_DB_NAME="db_disnaker"
uvicorn main:app --host 0.0.0.0 --port 8000
```

API dapat diuji di Swagger `http://IP-KOMPUTER-SUMBER:8000/docs`. Pastikan IP yang tercantum di `dags/main.py` (variabel `api_base_url` pada `PIPELINE_TASKS`) sesuai dengan IP komputer sumber saat ini.

### 3. Konfigurasi Koneksi Airflow

Tambahkan koneksi MySQL **`mysql_warehouse`** sehingga DAG dapat mengakses server MySQL tempat `raw_data`, `staging_area`, dan `dwh` dibuat.

Via UI Airflow (`Admin → Connections`):

| Field | Nilai |
| --- | --- |
| Conn Id | `mysql_warehouse` |
| Conn Type | MySQL |
| Host | IP/Host server MySQL target |
| Schema | *(dibiarkan kosong — database dibuat otomatis oleh DAG)* |
| Login | username MySQL |
| Password | password MySQL |
| Port | `3306` |

Anda juga dapat mengisinya pada file lokal `airflow_settings.yaml`.

### 4. Menjalankan Airflow & DAG

```bash
astro dev start
```

Setelah semua kontainer siap, Airflow UI terbuka di <http://localhost:8080/>. Aktifkan dan jalankan DAG **`ETL-Warehouse`** secara manual (`Trigger DAG`).

DAG akan:

1. Membuat database `raw_data`, `staging_area`, dan `dwh` bila belum ada.
2. Menjalankan pipeline Extract → Transform → Load berturut-turut untuk keempat sumber data.

Pemantauan status tiap task dapat dilakukan dari tab **Graph** pada Airflow UI.

## Menambah Sumber Data Baru

Untuk menambahkan dinas/sumber data baru (misal: `kesehatan`) sebagai pipeline di DAG utama:

1. Buat file baru di `dags/`, misal `kesehatan.py`.
2. Definisikan fungsi `create_kesehatan_tasks(execute_sql, get_mysql_hook, raw_db, staging_db, dwh_db, api_base_url)` berisi task `extract_to_raw`, `transform_staging`, dan (opsional) `load_to_dwh`; kembalikan task terakhir.
3. Import fungsi tersebut di `dags/main.py`.
4. Tambahkan entri ke list `PIPELINE_TASKS` beserta `api_base_url` sumber yang bersangkutan:

```python
{
    "name": "kesehatan",
    "create_tasks": create_kesehatan_tasks,
    "api_base_url": "http://10.0.0.35:8080/api",
},
```

---

*Dibuat dalam rangka program magang Semester 7 Tahun 2026 — Dinas Komunikasi, Informatika dan Persandian Banda Aceh bersama Politeknik Negeri Lhokseumawe.*
=======
Overview
========

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Project Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. By default, this directory includes one example DAG:
    - `example_astronauts`: This DAG shows a simple ETL pipeline example that queries the list of astronauts currently in space from the Open Notify API and prints a statement for each astronaut. The DAG uses the TaskFlow API to define tasks in Python, and dynamic task mapping to dynamically print a statement for each astronaut. For more on how this DAG works, see our [Getting started tutorial](https://www.astronomer.io/docs/learn/get-started-with-airflow).
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

Deploy Your Project Locally
===========================

Start Airflow on your local machine by running 'astro dev start'.

This command will spin up five Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- DAG Processor: The Airflow component responsible for parsing DAGs
- API Server: The Airflow component responsible for serving the Airflow UI and API
- Triggerer: The Airflow component responsible for triggering deferred tasks

When all five containers are ready the command will open the browser to the Airflow UI at http://localhost:8080/. You should also be able to access your Postgres Database at 'localhost:5432/postgres' with username 'postgres' and password 'postgres'.

Note: If you already have either of the above ports allocated, you can either [stop your existing Docker containers or change the port](https://www.astronomer.io/docs/astro/cli/troubleshoot-locally#ports-are-not-available-for-my-local-airflow-webserver).

Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://www.astronomer.io/docs/astro/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support.
>>>>>>> origin/etl/dinsos
