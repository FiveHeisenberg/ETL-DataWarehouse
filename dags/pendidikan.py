from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN PENDIDIKAN
# ============================================================
# Sesuai skema db_pendidikan:
# tb_waktu, tb_sekolah, tb_ptk, tb_siswa, tb_sarana, tb_pendidikan
SOURCE_ENDPOINTS = {
    "tb_waktu":      "/extraction/waktu",
    "tb_sekolah":    "/extraction/sekolah",
    "tb_ptk":        "/extraction/ptk",
    "tb_siswa":      "/extraction/siswa",
    "tb_sarana":     "/extraction/sarana",
    "tb_pendidikan": "/extraction/pendidikan",
}


# ============================================================
# PIPELINE PENDIDIKAN
# ============================================================

def create_pendidikan_tasks(
    execute_sql,
    get_mysql_hook,
    raw_db,
    staging_db,
    dwh_db,
    api_base_url,
):
    """
    execute_sql      : helper untuk jalanin list query SQL (didefinisikan di main.py)
    get_mysql_hook   : helper untuk koneksi ke server raw_data & staging_area
    raw_db           : nama database raw_data
    staging_db       : nama database staging_area
    dwh_db           : nama database dwh
    api_base_url     : base URL API sumber pendidikan, mis. "http://...:5000/api"
    """

    # ========================================================
    # TASK: EXTRACT API -> RAW_DATA
    # ========================================================

    @task
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
                # Fetch data dari API
                # --------------------------------------------

                response = requests.get(url, timeout=120)
                response.raise_for_status()

                payload = response.json()

                if isinstance(payload, list):
                    records = payload
                elif isinstance(payload, dict):
                    records = (
                        payload.get("data")
                        or payload.get("results")
                        or [payload]
                    )
                else:
                    records = []

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

    @task
    def transform_staging():

        logging.info("Memulai proses transform...")

        align_collation = f"""
        ALTER DATABASE `{staging_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        transformations = [

            # =================================================
            # WAKTU (referensi, harus bersih duluan)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_waktu`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_waktu`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                CAST(id_waktu AS UNSIGNED) AS id_waktu,
                CAST(tahun AS UNSIGNED) AS tahun,

                CASE
                    WHEN UPPER(TRIM(semester)) = 'GANJIL' THEN 'Ganjil'
                    WHEN UPPER(TRIM(semester)) = 'GENAP' THEN 'Genap'
                    ELSE NULL
                END AS semester,

                CASE
                    WHEN tanggal_mulai REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                    THEN tanggal_mulai
                    ELSE NULL
                END AS tanggal_mulai,

                CASE
                    WHEN tanggal_selesai REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                    THEN tanggal_selesai
                    ELSE NULL
                END AS tanggal_selesai,

                CASE
                    WHEN UPPER(TRIM(status_periode)) = 'AKTIF' THEN 'Aktif'
                    WHEN UPPER(TRIM(status_periode)) = 'TIDAK AKTIF' THEN 'Tidak Aktif'
                    ELSE 'Tidak Aktif'
                END AS status_periode,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_waktu`

            WHERE
                id_waktu IS NOT NULL
                AND tahun IS NOT NULL;
            """,

            # =================================================
            # SEKOLAH (referensi, harus bersih duluan)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sekolah`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_sekolah`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_sekolah) AS id_sekolah,
                TRIM(npsn) AS npsn,
                TRIM(nama_sekolah) AS nama_sekolah,

                CASE
                    WHEN UPPER(TRIM(jenjang)) IN
                        ('PAUD','TK','SD','SMP','SMA','SMK','SLB')
                    THEN UPPER(TRIM(jenjang))
                    ELSE NULL
                END AS jenjang,

                CASE
                    WHEN UPPER(TRIM(status_sekolah)) = 'NEGERI' THEN 'Negeri'
                    WHEN UPPER(TRIM(status_sekolah)) = 'SWASTA' THEN 'Swasta'
                    ELSE NULL
                END AS status_sekolah,

                CASE
                    WHEN UPPER(TRIM(akreditasi)) IN ('A','B','C')
                    THEN UPPER(TRIM(akreditasi))
                    WHEN akreditasi IS NULL
                        OR TRIM(akreditasi) = ''
                    THEN 'Belum Terakreditasi'
                    ELSE 'Belum Terakreditasi'
                END AS akreditasi,

                NULLIF(TRIM(id_desa), '') AS id_desa,
                NULLIF(TRIM(alamat_sekolah), '') AS alamat_sekolah,

                CASE
                    WHEN UPPER(TRIM(status_operasional)) = 'AKTIF' THEN 'Aktif'
                    WHEN UPPER(TRIM(status_operasional)) = 'TIDAK AKTIF' THEN 'Tidak Aktif'
                    ELSE 'Aktif'
                END AS status_operasional,

                CASE
                    WHEN tahun_berdiri REGEXP '^[0-9]{{4}}$'
                    THEN CAST(tahun_berdiri AS UNSIGNED)
                    ELSE NULL
                END AS tahun_berdiri,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_sekolah`

            WHERE
                id_sekolah IS NOT NULL
                AND TRIM(nama_sekolah) <> '';
            """,

            # =================================================
            # PTK (Pendidik & Tenaga Kependidikan)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_ptk`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_ptk`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_ptk) AS id_ptk,

                REGEXP_REPLACE(nik, '[^0-9]', '') AS nik,

                NULLIF(
                    REGEXP_REPLACE(nuptk, '[^0-9]', ''),
                    ''
                ) AS nuptk,

                TRIM(nama_ptk) AS nama_ptk,

                CASE
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'L' THEN 'L'
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'P' THEN 'P'
                    ELSE NULL
                END AS jenis_kelamin,

                TRIM(id_sekolah) AS id_sekolah,

                NULLIF(TRIM(jenis_ptk), '') AS jenis_ptk,
                NULLIF(TRIM(status_kepegawaian), '') AS status_kepegawaian,
                NULLIF(TRIM(pendidikan_terakhir), '') AS pendidikan_terakhir,
                NULLIF(TRIM(bidang_studi), '') AS bidang_studi,
                NULLIF(TRIM(jabatan), '') AS jabatan,

                CASE
                    WHEN tahun_masuk REGEXP '^[0-9]{{4}}$'
                    THEN CAST(tahun_masuk AS UNSIGNED)
                    ELSE NULL
                END AS tahun_masuk,

                CASE
                    WHEN UPPER(TRIM(status_ptk)) = 'AKTIF' THEN 'Aktif'
                    WHEN UPPER(TRIM(status_ptk)) = 'TIDAK AKTIF' THEN 'Tidak Aktif'
                    ELSE 'Aktif'
                END AS status_ptk,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_ptk`

            WHERE
                -- NIK wajib 16 digit
                CHAR_LENGTH(REGEXP_REPLACE(nik, '[^0-9]', '')) = 16

                -- Nama tidak boleh kosong
                AND nama_ptk IS NOT NULL
                AND TRIM(nama_ptk) <> ''

                -- Jenis kelamin harus valid
                AND jenis_kelamin IN ('L', 'P')

                AND id_sekolah IS NOT NULL;
            """,

            # =================================================
            # SISWA
            # Data Cleansing, Standardization, Validation
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_siswa`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_siswa`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                REGEXP_REPLACE(nik, '[^0-9]', '') AS nik,

                REGEXP_REPLACE(nisn, '[^0-9]', '') AS nisn,

                TRIM(nama_siswa) AS nama_siswa,

                CASE
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'L' THEN 'L'
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'P' THEN 'P'
                    ELSE NULL
                END AS jenis_kelamin,

                CASE
                    WHEN tanggal_lahir REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                        AND tanggal_lahir <= CURDATE()
                    THEN tanggal_lahir
                    ELSE NULL
                END AS tanggal_lahir,

                TRIM(id_sekolah) AS id_sekolah,
                CAST(id_waktu AS UNSIGNED) AS id_waktu,

                NULLIF(TRIM(kelas), '') AS kelas,
                NULLIF(TRIM(jurusan), '') AS jurusan,

                CASE
                    WHEN tahun_masuk REGEXP '^[0-9]{{4}}$'
                    THEN CAST(tahun_masuk AS UNSIGNED)
                    ELSE NULL
                END AS tahun_masuk,

                CASE
                    WHEN UPPER(TRIM(status_siswa)) = 'AKTIF' THEN 'Aktif'
                    WHEN UPPER(TRIM(status_siswa)) = 'LULUS' THEN 'Lulus'
                    WHEN UPPER(TRIM(status_siswa)) = 'PINDAH' THEN 'Pindah'
                    WHEN UPPER(TRIM(status_siswa)) = 'KELUAR' THEN 'Keluar'
                    ELSE NULL
                END AS status_siswa,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_siswa`

            WHERE
                -- NISN wajib 10 digit
                CHAR_LENGTH(REGEXP_REPLACE(nisn, '[^0-9]', '')) = 10

                -- NIK wajib 16 digit
                AND CHAR_LENGTH(REGEXP_REPLACE(nik, '[^0-9]', '')) = 16

                -- Nama tidak boleh kosong
                AND nama_siswa IS NOT NULL
                AND TRIM(nama_siswa) <> ''

                -- Jenis kelamin harus valid
                AND jenis_kelamin IN ('L', 'P')

                AND id_sekolah IS NOT NULL;
            """,

            # =================================================
            # SARANA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sarana`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_sarana`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                CAST(id_sarana AS UNSIGNED) AS id_sarana,
                TRIM(id_sekolah) AS id_sekolah,
                CAST(id_waktu AS UNSIGNED) AS id_waktu,

                COALESCE(CAST(jumlah_ruang_kelas AS UNSIGNED), 0) AS jumlah_ruang_kelas,
                COALESCE(CAST(jumlah_laboratorium AS UNSIGNED), 0) AS jumlah_laboratorium,
                COALESCE(CAST(jumlah_perpustakaan AS UNSIGNED), 0) AS jumlah_perpustakaan,
                COALESCE(CAST(jumlah_toilet AS UNSIGNED), 0) AS jumlah_toilet,
                COALESCE(CAST(jumlah_ruang_guru AS UNSIGNED), 0) AS jumlah_ruang_guru,
                COALESCE(CAST(jumlah_ruang_kepala AS UNSIGNED), 0) AS jumlah_ruang_kepala,
                COALESCE(CAST(jumlah_ruang_rusak AS UNSIGNED), 0) AS jumlah_ruang_rusak,

                CASE
                    WHEN UPPER(TRIM(kondisi_sarana)) = 'BAIK' THEN 'Baik'
                    WHEN UPPER(TRIM(kondisi_sarana)) = 'RUSAK RINGAN' THEN 'Rusak Ringan'
                    WHEN UPPER(TRIM(kondisi_sarana)) = 'RUSAK BERAT' THEN 'Rusak Berat'
                    ELSE NULL
                END AS kondisi_sarana,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_sarana`

            WHERE
                id_sarana IS NOT NULL
                AND id_sekolah IS NOT NULL;
            """,

            # =================================================
            # PENDIDIKAN (metrik agregat per sekolah per periode)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pendidikan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pendidikan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                CAST(id_pendidikan AS UNSIGNED) AS id_pendidikan,
                TRIM(id_sekolah) AS id_sekolah,
                CAST(id_waktu AS UNSIGNED) AS id_waktu,

                COALESCE(CAST(jumlah_siswa AS UNSIGNED), 0) AS jumlah_siswa,
                COALESCE(CAST(jumlah_guru AS UNSIGNED), 0) AS jumlah_guru,
                COALESCE(CAST(jumlah_rombel AS UNSIGNED), 0) AS jumlah_rombel,
                COALESCE(CAST(jumlah_mapel AS UNSIGNED), 0) AS jumlah_mapel,
                COALESCE(CAST(jumlah_jam_pembelajaran AS UNSIGNED), 0) AS jumlah_jam_pembelajaran,

                CASE
                    WHEN CAST(rata_rata_nilai AS DECIMAL(5,2)) BETWEEN 0 AND 100
                    THEN CAST(rata_rata_nilai AS DECIMAL(5,2))
                    ELSE NULL
                END AS rata_rata_nilai,

                CASE
                    WHEN CAST(persentase_kelulusan AS DECIMAL(5,2)) BETWEEN 0 AND 100
                    THEN CAST(persentase_kelulusan AS DECIMAL(5,2))
                    ELSE NULL
                END AS persentase_kelulusan,

                COALESCE(CAST(jumlah_lulus AS UNSIGNED), 0) AS jumlah_lulus,
                COALESCE(CAST(jumlah_mengulang AS UNSIGNED), 0) AS jumlah_mengulang,
                COALESCE(CAST(jumlah_putus_sekolah AS UNSIGNED), 0) AS jumlah_putus_sekolah,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_pendidikan`

            WHERE
                id_pendidikan IS NOT NULL
                AND id_sekolah IS NOT NULL
                AND id_waktu IS NOT NULL;
            """,
        ]

        execute_sql([align_collation] + transformations)

        logging.info("Transform staging pendidikan selesai.")

    # ========================================================
    # WIRING (sampai staging_area dulu)
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()

    t1 >> t2

    return t1