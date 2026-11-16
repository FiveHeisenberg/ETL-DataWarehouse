from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN TENAGA KERJA (DISNAKER)
# ============================================================

SOURCE_ENDPOINTS = {
    "tb_kasus_hi":          "/kasus-hi",
    "tb_lowongan":          "/lowongan",
    "tb_pelatihan_blk":     "/pelatihan-blk",
    "tb_penduduk_pencaker": "/penduduk-pencaker",
    "tb_penempatan":        "/penempatan",
    "tb_perusahaan":        "/perusahaan",
    "tb_peserta_pelatihan": "/peserta-pelatihan",
}


# ============================================================
# PIPELINE DISNAKER
# ============================================================

def create_disnaker_tasks(
    execute_sql,
    get_mysql_hook,
    raw_db,
    staging_db,
    dwh_db,
    api_base_url,
):

    # ========================================================
    # TASK: EXTRACT API -> RAW_DATA
    # ========================================================

    @task(task_id="extract_to_raw_disnaker")
    def extract_to_raw():

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            for table_name, endpoint in SOURCE_ENDPOINTS.items():

                raw_table = f"raw_{table_name}"
                url = f"{api_base_url}{endpoint}"

                logging.info(
                    "Extract API %s -> %s.%s",
                    url,
                    raw_db,
                    raw_table,
                )

                # --------------------------------------------
                # Fetch seluruh data dari API
                # --------------------------------------------

                page = 1
                limit = 100
                records = []

                while True:
                    response = requests.get(
                        url,
                        params={"page": page, "limit": limit},
                        timeout=120,
                    )
                    response.raise_for_status()

                    payload = response.json()

                    if isinstance(payload, list):
                        page_records = payload
                        records.extend(page_records)
                        break

                    if not isinstance(payload, dict):
                        break

                    page_records = (
                        payload.get("data")
                        or payload.get("results")
                        or []
                    )

                    if isinstance(page_records, dict):
                        page_records = [page_records]

                    records.extend(page_records)

                    pagination = payload.get("pagination") or {}

                    has_next = pagination.get("has_next")

                    if has_next is False:
                        break

                    if has_next is None:
                        if len(page_records) < limit:
                            break

                    page += 1

                if not records:
                    logging.warning(
                        "Tidak ada data dari %s, skip.",
                        endpoint,
                    )
                    continue

                # --------------------------------------------
                # Drop & buat raw table sesuai kolom API
                # --------------------------------------------

                columns = list(records[0].keys())

                cursor.execute(
                    f"DROP TABLE IF EXISTS "
                    f"`{raw_db}`.`{raw_table}`"
                )

                col_defs = ", ".join(
                    f"`{col}` VARCHAR(500)"
                    for col in columns
                )

                cursor.execute(
                    f"""
                    CREATE TABLE `{raw_db}`.`{raw_table}`
                    (
                        `_raw_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
                        {col_defs},
                        `sumber_database` VARCHAR(100),
                        `waktu_ekstraksi` DATETIME
                    )
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_0900_ai_ci;
                    """
                )

                # --------------------------------------------
                # Insert data
                # --------------------------------------------

                col_list = ", ".join(
                    f"`{c}`" for c in columns
                )

                now_str = (
                    pendulum
                    .now("Asia/Jakarta")
                    .to_datetime_string()
                )

                batch_size = 1000
                total = 0

                for i in range(0, len(records), batch_size):
                    batch = records[i : i + batch_size]

                    placeholders = ", ".join(
                        ["%s"] * len(columns)
                    )

                    sql_insert = (
                        f"INSERT INTO "
                        f"`{raw_db}`.`{raw_table}` "
                        f"({col_list}, "
                        f"`sumber_database`, "
                        f"`waktu_ekstraksi`) "
                        f"VALUES "
                        f"({placeholders}, %s, %s)"
                    )

                    rows = []

                    for rec in batch:
                        row = [
                            (
                                str(rec[c])
                                if rec.get(c) is not None
                                else None
                            )
                            for c in columns
                        ]
                        row.append(api_base_url)
                        row.append(now_str)
                        rows.append(row)

                    cursor.executemany(sql_insert, rows)
                    total += len(rows)

                logging.info(
                    "Extract %s selesai. %d records.",
                    table_name,
                    total,
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # ========================================================
    # TASK: TRANSFORM RAW_DATA -> STAGING_AREA
    # ========================================================

    @task(task_id="transform_staging_disnaker")
    def transform_staging():

        logging.info(
            "Memulai proses transform Disnaker..."
        )

        transformations = [

            # =================================================
            # KASUS HUBUNGAN INDUSTRIAL
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kasus_hi`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_kasus_hi` (
                id_kasus INT UNSIGNED PRIMARY KEY,
                nib_perusahaan VARCHAR(50),
                kategori_kasus VARCHAR(100),
                deskripsi_kejadian TEXT,
                tanggal_laporan DATE,
                status_penyelesaian VARCHAR(100),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_kasus_hi`
            SELECT DISTINCT
                CAST(id_kasus AS UNSIGNED) AS id_kasus,
                NULLIF(TRIM(nib_perusahaan), '') AS nib_perusahaan,
                CASE
                    WHEN TRIM(kategori_kasus) IN ('PHK', 'Sengketa Gaji', 'Kecelakaan Kerja', 'Pelanggaran K3')
                    THEN TRIM(kategori_kasus)
                    ELSE NULL
                END AS kategori_kasus,
                NULLIF(TRIM(deskripsi_kejadian), '') AS deskripsi_kejadian,
                CASE
                    WHEN tanggal_laporan <= CURDATE() AND tanggal_laporan >= '1900-01-01'
                    THEN tanggal_laporan
                    ELSE NULL
                END AS tanggal_laporan,
                CASE
                    WHEN TRIM(status_penyelesaian) IN ('Proses Mediasi', 'Selesai', 'Eskalasi Pengadilan')
                    THEN TRIM(status_penyelesaian)
                    ELSE NULL
                END AS status_penyelesaian,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_kasus_hi`
            WHERE
                id_kasus IS NOT NULL
                AND CAST(id_kasus AS UNSIGNED) > 0
                AND nib_perusahaan IS NOT NULL
                AND TRIM(nib_perusahaan) <> ''
                AND kategori_kasus IS NOT NULL
                AND TRIM(kategori_kasus) <> ''
                AND deskripsi_kejadian IS NOT NULL
                AND TRIM(deskripsi_kejadian) <> ''
                AND tanggal_laporan IS NOT NULL
                AND TRIM(status_penyelesaian) <> '';
            """,

            # =================================================
            # LOWONGAN
            # id_lowongan dan kuota_penerimaan tidak dibawa
            # ke staging karena tidak digunakan dalam rancangan DWH.
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_lowongan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_lowongan` (
                _stg_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                nib_perusahaan VARCHAR(50),
                posisi_jabatan VARCHAR(150),
                syarat_pendidikan VARCHAR(150),
                tanggal_buka DATE,
                tanggal_tutup DATE,
                status_aktif TINYINT,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_lowongan`
            (nib_perusahaan, posisi_jabatan, syarat_pendidikan, 
             tanggal_buka, tanggal_tutup, status_aktif, 
             sumber_database, waktu_ekstraksi)
            SELECT DISTINCT
                NULLIF(TRIM(nib_perusahaan), '') AS nib_perusahaan,
                NULLIF(TRIM(posisi_jabatan), '') AS posisi_jabatan,
                NULLIF(TRIM(syarat_pendidikan), '') AS syarat_pendidikan,
                CASE
                    WHEN tanggal_buka >= '1900-01-01'
                    AND tanggal_buka <= CURDATE()
                    THEN tanggal_buka
                    ELSE NULL
                END AS tanggal_buka,
                CASE
                    WHEN tanggal_tutup >= '1900-01-01'
                    AND tanggal_tutup >= tanggal_buka
                    THEN tanggal_tutup
                    ELSE NULL
                END AS tanggal_tutup,
                CASE
                    WHEN CAST(status_aktif AS UNSIGNED) IN (0, 1)
                    THEN CAST(status_aktif AS UNSIGNED)
                    ELSE NULL
                END AS status_aktif,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_lowongan`
            WHERE
                nib_perusahaan IS NOT NULL
                AND TRIM(nib_perusahaan) <> ''
                AND posisi_jabatan IS NOT NULL
                AND TRIM(posisi_jabatan) <> ''
                AND tanggal_buka IS NOT NULL
                AND tanggal_buka <= CURDATE()
                AND status_aktif IS NOT NULL
                AND CAST(status_aktif AS UNSIGNED) IN (0, 1);
            """,

            # =================================================
            # PELATIHAN BLK
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pelatihan_blk`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pelatihan_blk` (
                id_pelatihan INT UNSIGNED PRIMARY KEY,
                nama_program VARCHAR(150),
                jenis_kejuruan VARCHAR(100),
                kuota_peserta INT UNSIGNED,
                tanggal_pelaksanaan DATE,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_pelatihan_blk`
            SELECT DISTINCT
                CAST(id_pelatihan AS UNSIGNED) AS id_pelatihan,
                NULLIF(TRIM(nama_program), '') AS nama_program,
                NULLIF(TRIM(jenis_kejuruan), '') AS jenis_kejuruan,
                CAST(kuota_peserta AS UNSIGNED) AS kuota_peserta,
                CASE
                    WHEN tanggal_pelaksanaan >= '1900-01-01'
                    THEN tanggal_pelaksanaan
                    ELSE NULL
                END AS tanggal_pelaksanaan,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_pelatihan_blk`
            WHERE
                id_pelatihan IS NOT NULL
                AND CAST(id_pelatihan AS UNSIGNED) > 0
                AND nama_program IS NOT NULL
                AND TRIM(nama_program) <> ''
                AND jenis_kejuruan IS NOT NULL
                AND TRIM(jenis_kejuruan) <> ''
                AND kuota_peserta IS NOT NULL
                AND CAST(kuota_peserta AS UNSIGNED) >= 0
                AND tanggal_pelaksanaan IS NOT NULL;
            """,

            # =================================================
            # PENDUDUK PENCAKER
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_penduduk_pencaker`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_penduduk_pencaker` (
                nik VARCHAR(16) PRIMARY KEY,
                nama_lengkap VARCHAR(100),
                jenis_kelamin CHAR(1),
                tanggal_lahir DATE,
                pendidikan_terakhir VARCHAR(100),
                keahlian_utama VARCHAR(150),
                status_bekerja TINYINT,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_penduduk_pencaker`
            SELECT DISTINCT
                REGEXP_REPLACE(nik, '[^0-9]', '') AS nik,
                TRIM(nama_lengkap) AS nama_lengkap,
                CASE
                    WHEN TRIM(jenis_kelamin) IN ('L', 'P')
                    THEN TRIM(jenis_kelamin)
                    ELSE NULL
                END AS jenis_kelamin,
                CASE
                    WHEN tanggal_lahir >= '1900-01-01' AND tanggal_lahir <= CURDATE()
                    THEN tanggal_lahir
                    ELSE NULL
                END AS tanggal_lahir,
                NULLIF(TRIM(pendidikan_terakhir), '') AS pendidikan_terakhir,
                NULLIF(TRIM(keahlian_utama), '') AS keahlian_utama,
                CASE
                    WHEN CAST(status_bekerja AS UNSIGNED) IN (0, 1)
                    THEN CAST(status_bekerja AS UNSIGNED)
                    ELSE NULL
                END AS status_bekerja,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_penduduk_pencaker`
            WHERE
                CHAR_LENGTH(REGEXP_REPLACE(nik, '[^0-9]', '')) = 16
                AND nama_lengkap IS NOT NULL
                AND TRIM(nama_lengkap) <> ''
                AND TRIM(jenis_kelamin) IN ('L', 'P')
                AND tanggal_lahir IS NOT NULL
                AND status_bekerja IS NOT NULL
                AND CAST(status_bekerja AS UNSIGNED) IN (0, 1);
            """,

            # =================================================
            # PENEMPATAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_penempatan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_penempatan` (
                id_penempatan INT UNSIGNED PRIMARY KEY,
                nik_pencaker VARCHAR(16),
                id_lowongan INT UNSIGNED,
                tanggal_diterima DATE,
                jenis_kontrak VARCHAR(100),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_penempatan`
            SELECT DISTINCT
                CAST(id_penempatan AS UNSIGNED) AS id_penempatan,
                REGEXP_REPLACE(nik_pencaker, '[^0-9]', '') AS nik_pencaker,
                CAST(id_lowongan AS UNSIGNED) AS id_lowongan,
                CASE
                    WHEN tanggal_diterima >= '1900-01-01' AND tanggal_diterima <= CURDATE()
                    THEN tanggal_diterima
                    ELSE NULL
                END AS tanggal_diterima,
                NULLIF(TRIM(jenis_kontrak), '') AS jenis_kontrak,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_penempatan`
            WHERE
                id_penempatan IS NOT NULL
                AND CAST(id_penempatan AS UNSIGNED) > 0
                AND CHAR_LENGTH(REGEXP_REPLACE(nik_pencaker, '[^0-9]', '')) = 16
                AND id_lowongan IS NOT NULL
                AND CAST(id_lowongan AS UNSIGNED) > 0
                AND tanggal_diterima IS NOT NULL
                AND jenis_kontrak IS NOT NULL
                AND TRIM(jenis_kontrak) <> '';
            """,

            # =================================================
            # PERUSAHAAN
            # NIB BUKAN NIK — hanya dibersihkan dengan TRIM.
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_perusahaan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_perusahaan` (
                nib VARCHAR(50) PRIMARY KEY,
                nama_perusahaan VARCHAR(150),
                sektor_industri VARCHAR(100),
                alamat_perusahaan VARCHAR(255),
                jml_pekerja_tetap INT UNSIGNED,
                jml_pekerja_kontrak INT UNSIGNED,
                status_bpjs TINYINT,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_perusahaan`
            SELECT DISTINCT
                NULLIF(TRIM(nib), '') AS nib,
                NULLIF(TRIM(nama_perusahaan), '') AS nama_perusahaan,
                NULLIF(TRIM(sektor_industri), '') AS sektor_industri,
                NULLIF(TRIM(alamat_perusahaan), '') AS alamat_perusahaan,
                CAST(jml_pekerja_tetap AS UNSIGNED) AS jml_pekerja_tetap,
                CAST(jml_pekerja_kontrak AS UNSIGNED) AS jml_pekerja_kontrak,
                CASE
                    WHEN CAST(status_bpjs AS UNSIGNED) IN (0, 1)
                    THEN CAST(status_bpjs AS UNSIGNED)
                    ELSE NULL
                END AS status_bpjs,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_perusahaan`
            WHERE
                nib IS NOT NULL
                AND TRIM(nib) <> ''
                AND nama_perusahaan IS NOT NULL
                AND TRIM(nama_perusahaan) <> ''
                AND sektor_industri IS NOT NULL
                AND TRIM(sektor_industri) <> ''
                AND alamat_perusahaan IS NOT NULL
                AND TRIM(alamat_perusahaan) <> ''
                AND jml_pekerja_tetap IS NOT NULL
                AND CAST(jml_pekerja_tetap AS UNSIGNED) >= 0
                AND jml_pekerja_kontrak IS NOT NULL
                AND CAST(jml_pekerja_kontrak AS UNSIGNED) >= 0
                AND status_bpjs IS NOT NULL
                AND CAST(status_bpjs AS UNSIGNED) IN (0, 1);
            """,

            # =================================================
            # PESERTA PELATIHAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_peserta_pelatihan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_peserta_pelatihan` (
                id_peserta_pelatihan INT UNSIGNED PRIMARY KEY,
                nik_pencaker VARCHAR(16),
                id_pelatihan INT UNSIGNED,
                tanggal_daftar DATE,
                status_peserta VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_peserta_pelatihan`
            SELECT DISTINCT
                CAST(id_peserta_pelatihan AS UNSIGNED) AS id_peserta_pelatihan,
                REGEXP_REPLACE(nik_pencaker, '[^0-9]', '') AS nik_pencaker,
                CAST(id_pelatihan AS UNSIGNED) AS id_pelatihan,
                CASE
                    WHEN tanggal_daftar >= '1900-01-01' AND tanggal_daftar <= CURDATE()
                    THEN tanggal_daftar
                    ELSE NULL
                END AS tanggal_daftar,
                CASE
                    WHEN TRIM(status_peserta) IN ('Terdaftar', 'Mengikuti', 'Lulus', 'Tidak Lulus')
                    THEN TRIM(status_peserta)
                    ELSE NULL
                END AS status_peserta,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_peserta_pelatihan`
            WHERE
                id_peserta_pelatihan IS NOT NULL
                AND CAST(id_peserta_pelatihan AS UNSIGNED) > 0
                AND CHAR_LENGTH(REGEXP_REPLACE(nik_pencaker, '[^0-9]', '')) = 16
                AND id_pelatihan IS NOT NULL
                AND CAST(id_pelatihan AS UNSIGNED) > 0
                AND tanggal_daftar IS NOT NULL
                AND TRIM(status_peserta) IN ('Terdaftar', 'Mengikuti', 'Lulus', 'Tidak Lulus');
            """,
        ]

        # raw_data dan staging_area SUDAH ADA.
        # Tidak ada CREATE DATABASE atau ALTER DATABASE di sini.
        execute_sql(transformations)

        logging.info(
            "Transform staging Disnaker selesai."
        )



    # ========================================================
    # TASK: LOAD -> DATA WAREHOUSE
    # Format mengikuti pola load pada dukcapil.py:
    # - align collation
    # - create dimension/fact bila belum ada
    # - load dimension dengan ON DUPLICATE KEY UPDATE
    # - load fact dari staging menggunakan surrogate key
    # ========================================================

    @task(task_id="load_to_dwh_disnaker")
    def load_to_dwh():

        logging.info(
            "Membuat dimension dan fact Disnaker..."
        )

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        dwh_tables = [
            "dim_waktu",
            "dim_pencaker",
            "dim_perusahaan",
            "dim_pelatihan",
            "dim_lowongan",
            "fact_lowongan",
            "fact_penempatan",
            "fact_peserta_pelatihan",
            "fact_kasus_hi",
        ]

        convert_tables = [align_collation]

        hook = get_mysql_hook()
        check_conn = hook.get_conn()
        check_cursor = check_conn.cursor()

        try:
            for dwh_table in dwh_tables:
                check_cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_name = %s
                    """,
                    (dwh_db, dwh_table),
                )

                if check_cursor.fetchone()[0]:
                    convert_tables.append(
                        f"""
                        ALTER TABLE `{dwh_db}`.`{dwh_table}`
                        CONVERT TO CHARACTER SET utf8mb4
                        COLLATE utf8mb4_0900_ai_ci;
                        """
                    )
        finally:
            check_cursor.close()
            check_conn.close()

        execute_sql(convert_tables)

        # ====================================================
        # CREATE DIMENSION & FACT
        # ====================================================

        create_tables = [

            # ------------------------------------------------
            # DIM WAKTU
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_waktu`
            (
                waktu_key INT PRIMARY KEY,
                tanggal DATE NOT NULL,
                hari INT,
                bulan INT,
                nama_bulan VARCHAR(20),
                kuartal INT,
                tahun INT,
                waktu_load DATETIME NOT NULL
            );
            """,

            # ------------------------------------------------
            # DIM PENCAKER
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pencaker`
            (
                pencaker_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                nik VARCHAR(16) NOT NULL,
                nama_lengkap VARCHAR(100),
                jenis_kelamin CHAR(1),
                tanggal_lahir DATE,
                pendidikan_terakhir VARCHAR(100),
                keahlian_utama VARCHAR(150),
                status_bekerja TINYINT,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_pencaker (nik)
            );
            """,

            # ------------------------------------------------
            # DIM PERUSAHAAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_perusahaan`
            (
                perusahaan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                nib VARCHAR(50) NOT NULL,
                nama_perusahaan VARCHAR(150),
                sektor_industri VARCHAR(100),
                alamat_perusahaan VARCHAR(255),
                jml_pekerja_tetap INT,
                jml_pekerja_kontrak INT,
                status_bpjs TINYINT,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_perusahaan (nib)
            );
            """,

            # ------------------------------------------------
            # DIM PELATIHAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pelatihan`
            (
                pelatihan_key INT AUTO_INCREMENT PRIMARY KEY,
                id_pelatihan INT NOT NULL,
                nama_program VARCHAR(150),
                jenis_kejuruan VARCHAR(100),
                kuota_peserta INT,
                tanggal_pelaksanaan DATE,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_pelatihan (id_pelatihan)
            );
            """,

            # ------------------------------------------------
            # DIM LOWONGAN
            #
            # id_lowongan tidak tersedia pada staging_lowongan
            # karena memang dibuang pada tahap transform.
            # Oleh karena itu dim_lowongan menggunakan kombinasi
            # atribut lowongan sebagai business key.
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_lowongan`
            (
                lowongan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                nib_perusahaan VARCHAR(50) NOT NULL,
                posisi_jabatan VARCHAR(150) NOT NULL,
                syarat_pendidikan VARCHAR(150),
                tanggal_buka DATE,
                tanggal_tutup DATE,
                status_aktif TINYINT,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_lowongan
                (
                    nib_perusahaan,
                    posisi_jabatan,
                    tanggal_buka
                )
            );
            """,

            # ------------------------------------------------
            # FACT LOWONGAN
            # Grain: 1 lowongan per kombinasi business key
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_lowongan`
            (
                fact_lowongan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                lowongan_key BIGINT NOT NULL,
                perusahaan_key BIGINT,
                waktu_key INT NOT NULL,
                status_aktif TINYINT,
                jumlah_lowongan INT DEFAULT 1,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_lowongan
                (
                    lowongan_key,
                    waktu_key
                ),
                KEY idx_fact_lowongan_perusahaan
                    (perusahaan_key),
                KEY idx_fact_lowongan_waktu
                    (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT PENEMPATAN
            # Grain: 1 record penempatan
            # id_lowongan disimpan sebagai degenerate/source key
            # karena staging lowongan tidak membawa id_lowongan.
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_penempatan`
            (
                fact_penempatan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_penempatan INT NOT NULL,
                pencaker_key BIGINT,
                id_lowongan INT,
                waktu_key INT NOT NULL,
                jenis_kontrak VARCHAR(100),
                jumlah_penempatan INT DEFAULT 1,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_penempatan (id_penempatan),
                KEY idx_fact_penempatan_pencaker (pencaker_key),
                KEY idx_fact_penempatan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT PESERTA PELATIHAN
            # Grain: 1 pendaftaran peserta pada pelatihan
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_peserta_pelatihan`
            (
                fact_peserta_pelatihan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_peserta_pelatihan INT NOT NULL,
                pencaker_key BIGINT,
                pelatihan_key INT,
                waktu_key INT NOT NULL,
                tanggal_daftar DATE,
                status_peserta VARCHAR(50),
                jumlah_peserta INT DEFAULT 1,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_peserta_pelatihan
                (id_peserta_pelatihan),
                KEY idx_fact_peserta_pencaker (pencaker_key),
                KEY idx_fact_peserta_pelatihan (pelatihan_key),
                KEY idx_fact_peserta_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT KASUS HUBUNGAN INDUSTRIAL
            # Grain: 1 kasus hubungan industrial
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kasus_hi`
            (
                fact_kasus_hi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_kasus INT NOT NULL,
                perusahaan_key BIGINT,
                waktu_key INT NOT NULL,
                kategori_kasus VARCHAR(100),
                deskripsi_kejadian TEXT,
                status_penyelesaian VARCHAR(100),
                jumlah_kasus INT DEFAULT 1,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_kasus_hi (id_kasus),
                KEY idx_fact_kasus_perusahaan (perusahaan_key),
                KEY idx_fact_kasus_waktu (waktu_key)
            );
            """,
        ]

        execute_sql(create_tables)

        # ====================================================
        # LOAD DIMENSION
        # ====================================================

        load_dimensions = [

            # ------------------------------------------------
            # DIM WAKTU
            # Menggunakan tanggal-tanggal yang benar-benar muncul
            # pada data staging, bukan hanya tanggal hari ini.
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_waktu`
            (
                waktu_key,
                tanggal,
                hari,
                bulan,
                nama_bulan,
                kuartal,
                tahun,
                waktu_load
            )
            SELECT
                CAST(DATE_FORMAT(t.tanggal, '%Y%m%d') AS UNSIGNED),
                t.tanggal,
                DAY(t.tanggal),
                MONTH(t.tanggal),
                CASE MONTH(t.tanggal)
                    WHEN 1 THEN 'Januari'
                    WHEN 2 THEN 'Februari'
                    WHEN 3 THEN 'Maret'
                    WHEN 4 THEN 'April'
                    WHEN 5 THEN 'Mei'
                    WHEN 6 THEN 'Juni'
                    WHEN 7 THEN 'Juli'
                    WHEN 8 THEN 'Agustus'
                    WHEN 9 THEN 'September'
                    WHEN 10 THEN 'Oktober'
                    WHEN 11 THEN 'November'
                    WHEN 12 THEN 'Desember'
                END,
                QUARTER(t.tanggal),
                YEAR(t.tanggal),
                NOW()
            FROM
            (
                SELECT tanggal_buka AS tanggal
                FROM `{staging_db}`.`stg_lowongan`
                WHERE tanggal_buka IS NOT NULL

                UNION

                SELECT tanggal_diterima
                FROM `{staging_db}`.`stg_penempatan`
                WHERE tanggal_diterima IS NOT NULL

                UNION

                SELECT tanggal_daftar
                FROM `{staging_db}`.`stg_peserta_pelatihan`
                WHERE tanggal_daftar IS NOT NULL

                UNION

                SELECT tanggal_pelaksanaan
                FROM `{staging_db}`.`stg_pelatihan_blk`
                WHERE tanggal_pelaksanaan IS NOT NULL

                UNION

                SELECT tanggal_laporan
                FROM `{staging_db}`.`stg_kasus_hi`
                WHERE tanggal_laporan IS NOT NULL
            ) t
            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM PENCAKER
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pencaker`
            (
                nik,
                nama_lengkap,
                jenis_kelamin,
                tanggal_lahir,
                pendidikan_terakhir,
                keahlian_utama,
                status_bekerja,
                sumber_database,
                waktu_load
            )
            SELECT
                nik,
                nama_lengkap,
                jenis_kelamin,
                tanggal_lahir,
                pendidikan_terakhir,
                keahlian_utama,
                status_bekerja,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_penduduk_pencaker`
            ON DUPLICATE KEY UPDATE
                nama_lengkap = VALUES(nama_lengkap),
                jenis_kelamin = VALUES(jenis_kelamin),
                tanggal_lahir = VALUES(tanggal_lahir),
                pendidikan_terakhir = VALUES(pendidikan_terakhir),
                keahlian_utama = VALUES(keahlian_utama),
                status_bekerja = VALUES(status_bekerja),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM PERUSAHAAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_perusahaan`
            (
                nib,
                nama_perusahaan,
                sektor_industri,
                alamat_perusahaan,
                jml_pekerja_tetap,
                jml_pekerja_kontrak,
                status_bpjs,
                sumber_database,
                waktu_load
            )
            SELECT
                nib,
                nama_perusahaan,
                sektor_industri,
                alamat_perusahaan,
                jml_pekerja_tetap,
                jml_pekerja_kontrak,
                status_bpjs,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_perusahaan`
            ON DUPLICATE KEY UPDATE
                nama_perusahaan = VALUES(nama_perusahaan),
                sektor_industri = VALUES(sektor_industri),
                alamat_perusahaan = VALUES(alamat_perusahaan),
                jml_pekerja_tetap = VALUES(jml_pekerja_tetap),
                jml_pekerja_kontrak = VALUES(jml_pekerja_kontrak),
                status_bpjs = VALUES(status_bpjs),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM PELATIHAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pelatihan`
            (
                id_pelatihan,
                nama_program,
                jenis_kejuruan,
                kuota_peserta,
                tanggal_pelaksanaan,
                sumber_database,
                waktu_load
            )
            SELECT
                id_pelatihan,
                nama_program,
                jenis_kejuruan,
                kuota_peserta,
                tanggal_pelaksanaan,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_pelatihan_blk`
            ON DUPLICATE KEY UPDATE
                nama_program = VALUES(nama_program),
                jenis_kejuruan = VALUES(jenis_kejuruan),
                kuota_peserta = VALUES(kuota_peserta),
                tanggal_pelaksanaan = VALUES(tanggal_pelaksanaan),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM LOWONGAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_lowongan`
            (
                nib_perusahaan,
                posisi_jabatan,
                syarat_pendidikan,
                tanggal_buka,
                tanggal_tutup,
                status_aktif,
                sumber_database,
                waktu_load
            )
            SELECT
                nib_perusahaan,
                posisi_jabatan,
                syarat_pendidikan,
                tanggal_buka,
                tanggal_tutup,
                status_aktif,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_lowongan`
            ON DUPLICATE KEY UPDATE
                syarat_pendidikan = VALUES(syarat_pendidikan),
                tanggal_tutup = VALUES(tanggal_tutup),
                status_aktif = VALUES(status_aktif),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FACT
        # ====================================================

        load_facts = [

            # ------------------------------------------------
            # FACT LOWONGAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_lowongan`
            (
                lowongan_key,
                perusahaan_key,
                waktu_key,
                status_aktif,
                jumlah_lowongan,
                sumber_database,
                waktu_load
            )
            SELECT
                dl.lowongan_key,
                dp.perusahaan_key,
                CAST(
                    DATE_FORMAT(sl.tanggal_buka, '%Y%m%d')
                    AS UNSIGNED
                ),
                sl.status_aktif,
                1,
                sl.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_lowongan` sl
            INNER JOIN `{dwh_db}`.`dim_lowongan` dl
                ON dl.nib_perusahaan = sl.nib_perusahaan
                AND dl.posisi_jabatan = sl.posisi_jabatan
                AND dl.tanggal_buka = sl.tanggal_buka
            LEFT JOIN `{dwh_db}`.`dim_perusahaan` dp
                ON sl.nib_perusahaan = dp.nib
            ON DUPLICATE KEY UPDATE
                perusahaan_key = VALUES(perusahaan_key),
                status_aktif = VALUES(status_aktif),
                jumlah_lowongan = VALUES(jumlah_lowongan),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT PENEMPATAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_penempatan`
            (
                id_penempatan,
                pencaker_key,
                id_lowongan,
                waktu_key,
                jenis_kontrak,
                jumlah_penempatan,
                sumber_database,
                waktu_load
            )
            SELECT
                sp.id_penempatan,
                dp.pencaker_key,
                sp.id_lowongan,
                CAST(
                    DATE_FORMAT(sp.tanggal_diterima, '%Y%m%d')
                    AS UNSIGNED
                ),
                sp.jenis_kontrak,
                1,
                sp.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_penempatan` sp
            LEFT JOIN `{dwh_db}`.`dim_pencaker` dp
                ON sp.nik_pencaker = dp.nik
            ON DUPLICATE KEY UPDATE
                pencaker_key = VALUES(pencaker_key),
                id_lowongan = VALUES(id_lowongan),
                waktu_key = VALUES(waktu_key),
                jenis_kontrak = VALUES(jenis_kontrak),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT PESERTA PELATIHAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_peserta_pelatihan`
            (
                id_peserta_pelatihan,
                pencaker_key,
                pelatihan_key,
                waktu_key,
                tanggal_daftar,
                status_peserta,
                jumlah_peserta,
                sumber_database,
                waktu_load
            )
            SELECT
                spp.id_peserta_pelatihan,
                dp.pencaker_key,
                dpl.pelatihan_key,
                CAST(
                    DATE_FORMAT(spp.tanggal_daftar, '%Y%m%d')
                    AS UNSIGNED
                ),
                spp.tanggal_daftar,
                spp.status_peserta,
                1,
                spp.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_peserta_pelatihan` spp
            LEFT JOIN `{dwh_db}`.`dim_pencaker` dp
                ON spp.nik_pencaker = dp.nik
            LEFT JOIN `{dwh_db}`.`dim_pelatihan` dpl
                ON spp.id_pelatihan = dpl.id_pelatihan
            ON DUPLICATE KEY UPDATE
                pencaker_key = VALUES(pencaker_key),
                pelatihan_key = VALUES(pelatihan_key),
                waktu_key = VALUES(waktu_key),
                tanggal_daftar = VALUES(tanggal_daftar),
                status_peserta = VALUES(status_peserta),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT KASUS HI
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kasus_hi`
            (
                id_kasus,
                perusahaan_key,
                waktu_key,
                kategori_kasus,
                deskripsi_kejadian,
                status_penyelesaian,
                jumlah_kasus,
                sumber_database,
                waktu_load
            )
            SELECT
                sk.id_kasus,
                dp.perusahaan_key,
                CAST(
                    DATE_FORMAT(sk.tanggal_laporan, '%Y%m%d')
                    AS UNSIGNED
                ),
                sk.kategori_kasus,
                sk.deskripsi_kejadian,
                sk.status_penyelesaian,
                1,
                sk.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_kasus_hi` sk
            LEFT JOIN `{dwh_db}`.`dim_perusahaan` dp
                ON sk.nib_perusahaan = dp.nib
            ON DUPLICATE KEY UPDATE
                perusahaan_key = VALUES(perusahaan_key),
                waktu_key = VALUES(waktu_key),
                kategori_kasus = VALUES(kategori_kasus),
                deskripsi_kejadian = VALUES(deskripsi_kejadian),
                status_penyelesaian = VALUES(status_penyelesaian),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

        logging.info(
            "Load Disnaker ke Data Warehouse selesai."
        )


    # ========================================================
    # WIRING
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()
    t3 = load_to_dwh()

    t1 >> t2 >> t3

    return t3
