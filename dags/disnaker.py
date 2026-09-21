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
                        id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
            CREATE TABLE `{staging_db}`.`stg_kasus_hi`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(id_kasus AS UNSIGNED)
                    AS id_kasus,

                NULLIF(
                    TRIM(nib_perusahaan),
                    ''
                ) AS nib_perusahaan,

                CASE
                    WHEN TRIM(kategori_kasus)
                        IN (
                            'PHK',
                            'Sengketa Gaji',
                            'Kecelakaan Kerja',
                            'Pelanggaran K3'
                        )
                    THEN TRIM(kategori_kasus)
                    ELSE NULL
                END AS kategori_kasus,

                NULLIF(
                    TRIM(deskripsi_kejadian),
                    ''
                ) AS deskripsi_kejadian,

                CASE
                    WHEN tanggal_laporan <= CURDATE()
                    AND tanggal_laporan >= '1900-01-01'
                    THEN tanggal_laporan
                    ELSE NULL
                END AS tanggal_laporan,

                CASE
                    WHEN TRIM(status_penyelesaian)
                        IN (
                            'Proses Mediasi',
                            'Selesai',
                            'Eskalasi Pengadilan'
                        )
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
            CREATE TABLE `{staging_db}`.`stg_lowongan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                NULLIF(
                    TRIM(nib_perusahaan),
                    ''
                ) AS nib_perusahaan,

                NULLIF(
                    TRIM(posisi_jabatan),
                    ''
                ) AS posisi_jabatan,

                NULLIF(
                    TRIM(syarat_pendidikan),
                    ''
                ) AS syarat_pendidikan,

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
            CREATE TABLE `{staging_db}`.`stg_pelatihan_blk`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(id_pelatihan AS UNSIGNED)
                    AS id_pelatihan,

                NULLIF(
                    TRIM(nama_program),
                    ''
                ) AS nama_program,

                NULLIF(
                    TRIM(jenis_kejuruan),
                    ''
                ) AS jenis_kejuruan,

                CAST(kuota_peserta AS UNSIGNED)
                    AS kuota_peserta,

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
            CREATE TABLE `{staging_db}`.`stg_penduduk_pencaker`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                REGEXP_REPLACE(
                    nik,
                    '[^0-9]',
                    ''
                ) AS nik,

                TRIM(nama_lengkap)
                    AS nama_lengkap,

                CASE
                    WHEN TRIM(jenis_kelamin) IN ('L', 'P')
                    THEN TRIM(jenis_kelamin)
                    ELSE NULL
                END AS jenis_kelamin,

                CASE
                    WHEN tanggal_lahir >= '1900-01-01'
                    AND tanggal_lahir <= CURDATE()
                    THEN tanggal_lahir
                    ELSE NULL
                END AS tanggal_lahir,

                NULLIF(
                    TRIM(pendidikan_terakhir),
                    ''
                ) AS pendidikan_terakhir,

                NULLIF(
                    TRIM(keahlian_utama),
                    ''
                ) AS keahlian_utama,

                CASE
                    WHEN CAST(status_bekerja AS UNSIGNED) IN (0, 1)
                    THEN CAST(status_bekerja AS UNSIGNED)
                    ELSE NULL
                END AS status_bekerja,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_penduduk_pencaker`

            WHERE
                CHAR_LENGTH(
                    REGEXP_REPLACE(
                        nik,
                        '[^0-9]',
                        ''
                    )
                ) = 16
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
            CREATE TABLE `{staging_db}`.`stg_penempatan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(id_penempatan AS UNSIGNED)
                    AS id_penempatan,

                REGEXP_REPLACE(
                    nik_pencaker,
                    '[^0-9]',
                    ''
                ) AS nik_pencaker,

                CAST(id_lowongan AS UNSIGNED)
                    AS id_lowongan,

                CASE
                    WHEN tanggal_diterima >= '1900-01-01'
                    AND tanggal_diterima <= CURDATE()
                    THEN tanggal_diterima
                    ELSE NULL
                END AS tanggal_diterima,

                NULLIF(
                    TRIM(jenis_kontrak),
                    ''
                ) AS jenis_kontrak,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_penempatan`

            WHERE
                id_penempatan IS NOT NULL
                AND CAST(id_penempatan AS UNSIGNED) > 0
                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        nik_pencaker,
                        '[^0-9]',
                        ''
                    )
                ) = 16
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
            CREATE TABLE `{staging_db}`.`stg_perusahaan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                NULLIF(
                    TRIM(nib),
                    ''
                ) AS nib,

                NULLIF(
                    TRIM(nama_perusahaan),
                    ''
                ) AS nama_perusahaan,

                NULLIF(
                    TRIM(sektor_industri),
                    ''
                ) AS sektor_industri,

                NULLIF(
                    TRIM(alamat_perusahaan),
                    ''
                ) AS alamat_perusahaan,

                CAST(
                    jml_pekerja_tetap
                    AS UNSIGNED
                ) AS jml_pekerja_tetap,

                CAST(
                    jml_pekerja_kontrak
                    AS UNSIGNED
                ) AS jml_pekerja_kontrak,

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
            CREATE TABLE `{staging_db}`.`stg_peserta_pelatihan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(
                    id_peserta_pelatihan
                    AS UNSIGNED
                ) AS id_peserta_pelatihan,

                REGEXP_REPLACE(
                    nik_pencaker,
                    '[^0-9]',
                    ''
                ) AS nik_pencaker,

                CAST(id_pelatihan AS UNSIGNED)
                    AS id_pelatihan,

                CASE
                    WHEN tanggal_daftar >= '1900-01-01'
                    AND tanggal_daftar <= CURDATE()
                    THEN tanggal_daftar
                    ELSE NULL
                END AS tanggal_daftar,

                CASE
                    WHEN TRIM(status_peserta)
                        IN (
                            'Terdaftar',
                            'Mengikuti',
                            'Lulus',
                            'Tidak Lulus'
                        )
                    THEN TRIM(status_peserta)
                    ELSE NULL
                END AS status_peserta,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_peserta_pelatihan`

            WHERE
                id_peserta_pelatihan IS NOT NULL
                AND CAST(id_peserta_pelatihan AS UNSIGNED) > 0
                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        nik_pencaker,
                        '[^0-9]',
                        ''
                    )
                ) = 16
                AND id_pelatihan IS NOT NULL
                AND CAST(id_pelatihan AS UNSIGNED) > 0
                AND tanggal_daftar IS NOT NULL
                AND TRIM(status_peserta) IN (
                    'Terdaftar',
                    'Mengikuti',
                    'Lulus',
                    'Tidak Lulus'
                );
            """,
        ]

        # raw_data dan staging_area SUDAH ADA.
        # Tidak ada CREATE DATABASE atau ALTER DATABASE di sini.
        execute_sql(transformations)

        logging.info(
            "Transform staging Disnaker selesai."
        )

    # ========================================================
    # WIRING
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()

    t1 >> t2

    return t2
