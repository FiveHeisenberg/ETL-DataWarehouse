from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN PENDIDIKAN
# ============================================================
#
# TODO: isi endpoint di bawah sesuai API pendidikan kamu.
# Base URL-nya (api_base_url) diisi di main.py, bukan di sini
# -- lihat instruksi di bagian bawah file ini.
#
# Kalau nama endpoint di API kamu beda dari tebakan di bawah,
# tinggal sesuaikan value-nya (key kiri = nama tabel, JANGAN
# diubah; value kanan = path endpoint, SESUAIKAN).
# ============================================================

SOURCE_ENDPOINTS = {
    "tb_waktu":      "/extraction/waktu",
    "tb_sekolah":    "/extraction/sekolah",
    "tb_ptk":        "/extraction/ptk",
    "tb_sarana":     "/extraction/sarana",
    "tb_siswa":      "/extraction/siswa",
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

        logging.info(
            "Memulai proses transform..."
        )

        transformations = [

            # =================================================
            # WAKTU
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_waktu`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_waktu` AS

            SELECT DISTINCT
                TRIM(id_waktu) AS id_waktu,
                TRIM(tahun) AS tahun,
                TRIM(semester) AS semester,
                tanggal_mulai,
                tanggal_selesai,
                TRIM(status_periode) AS status_periode,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_waktu`

            WHERE
                id_waktu IS NOT NULL;
            """,

            # =================================================
            # SEKOLAH
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sekolah`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_sekolah` AS

            SELECT DISTINCT
                TRIM(id_sekolah) AS id_sekolah,
                TRIM(npsn) AS npsn,
                TRIM(nama_sekolah) AS nama_sekolah,
                TRIM(jenjang) AS jenjang,
                TRIM(status_sekolah) AS status_sekolah,
                TRIM(akreditasi) AS akreditasi,
                TRIM(id_desa) AS id_desa,
                TRIM(alamat_sekolah) AS alamat_sekolah,
                TRIM(status_operasional) AS status_operasional,
                TRIM(tahun_berdiri) AS tahun_berdiri,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_sekolah`

            WHERE
                id_sekolah IS NOT NULL
                AND TRIM(nama_sekolah) <> '';
            """,

            # =================================================
            # PTK (Guru & Tenaga Kependidikan)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_ptk`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_ptk` AS

            SELECT DISTINCT
                TRIM(id_ptk) AS id_ptk,

                REGEXP_REPLACE(nik, '[^0-9]', '')
                    AS nik,

                NULLIF(
                    REGEXP_REPLACE(nuptk, '[^0-9]', ''),
                    ''
                ) AS nuptk,

                TRIM(nama_ptk) AS nama_ptk,

                CASE
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'L'
                        THEN 'L'
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'P'
                        THEN 'P'
                    ELSE NULL
                END AS jenis_kelamin,

                TRIM(id_sekolah) AS id_sekolah,
                TRIM(jenis_ptk) AS jenis_ptk,
                TRIM(status_kepegawaian) AS status_kepegawaian,
                TRIM(pendidikan_terakhir) AS pendidikan_terakhir,
                TRIM(bidang_studi) AS bidang_studi,
                TRIM(jabatan) AS jabatan,
                TRIM(tahun_masuk) AS tahun_masuk,
                TRIM(status_ptk) AS status_ptk,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_ptk`

            WHERE
                CHAR_LENGTH(
                    REGEXP_REPLACE(nik, '[^0-9]', '')
                ) = 16
                AND id_ptk IS NOT NULL
                AND TRIM(nama_ptk) <> '';
            """,

            # =================================================
            # SARANA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sarana`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_sarana` AS

            SELECT DISTINCT
                TRIM(id_sarana) AS id_sarana,
                TRIM(id_sekolah) AS id_sekolah,
                TRIM(id_waktu) AS id_waktu,

                CAST(jumlah_ruang_kelas AS UNSIGNED)
                    AS jumlah_ruang_kelas,
                CAST(jumlah_laboratorium AS UNSIGNED)
                    AS jumlah_laboratorium,
                CAST(jumlah_perpustakaan AS UNSIGNED)
                    AS jumlah_perpustakaan,
                CAST(jumlah_toilet AS UNSIGNED)
                    AS jumlah_toilet,
                CAST(jumlah_ruang_guru AS UNSIGNED)
                    AS jumlah_ruang_guru,
                CAST(jumlah_ruang_kepala AS UNSIGNED)
                    AS jumlah_ruang_kepala,
                CAST(jumlah_ruang_rusak AS UNSIGNED)
                    AS jumlah_ruang_rusak,

                TRIM(kondisi_sarana) AS kondisi_sarana,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_sarana`

            WHERE
                id_sarana IS NOT NULL
                AND id_sekolah IS NOT NULL
                AND id_waktu IS NOT NULL;
            """,

            # =================================================
            # SISWA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_siswa`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_siswa` AS

            SELECT DISTINCT
                REGEXP_REPLACE(nik, '[^0-9]', '')
                    AS nik,

                TRIM(nisn) AS nisn,
                TRIM(nama_siswa) AS nama_siswa,

                CASE
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'L'
                        THEN 'L'
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'P'
                        THEN 'P'
                    ELSE NULL
                END AS jenis_kelamin,

                CASE
                    WHEN tanggal_lahir <= CURDATE()
                        THEN tanggal_lahir
                    ELSE NULL
                END AS tanggal_lahir,

                TRIM(id_sekolah) AS id_sekolah,
                TRIM(id_waktu) AS id_waktu,
                TRIM(kelas) AS kelas,

                NULLIF(TRIM(jurusan), '') AS jurusan,

                TRIM(tahun_masuk) AS tahun_masuk,
                TRIM(status_siswa) AS status_siswa,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_siswa`

            WHERE
                CHAR_LENGTH(
                    REGEXP_REPLACE(nik, '[^0-9]', '')
                ) = 16
                AND TRIM(nama_siswa) <> ''
                AND UPPER(TRIM(jenis_kelamin)) IN ('L', 'P');
            """,

            # =================================================
            # PENDIDIKAN (metrik sekolah per periode)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pendidikan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pendidikan` AS

            SELECT DISTINCT
                TRIM(id_pendidikan) AS id_pendidikan,
                TRIM(id_sekolah) AS id_sekolah,
                TRIM(id_waktu) AS id_waktu,

                CAST(jumlah_siswa AS UNSIGNED)
                    AS jumlah_siswa,
                CAST(jumlah_guru AS UNSIGNED)
                    AS jumlah_guru,
                CAST(jumlah_rombel AS UNSIGNED)
                    AS jumlah_rombel,
                CAST(jumlah_mapel AS UNSIGNED)
                    AS jumlah_mapel,
                CAST(jumlah_jam_pembelajaran AS UNSIGNED)
                    AS jumlah_jam_pembelajaran,
                CAST(rata_rata_nilai AS DECIMAL(5,2))
                    AS rata_rata_nilai,
                CAST(persentase_kelulusan AS DECIMAL(5,2))
                    AS persentase_kelulusan,
                CAST(jumlah_lulus AS UNSIGNED)
                    AS jumlah_lulus,
                CAST(jumlah_mengulang AS UNSIGNED)
                    AS jumlah_mengulang,
                CAST(jumlah_putus_sekolah AS UNSIGNED)
                    AS jumlah_putus_sekolah,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_pendidikan`

            WHERE
                id_pendidikan IS NOT NULL
                AND id_sekolah IS NOT NULL
                AND id_waktu IS NOT NULL;
            """,
        ]

        execute_sql(transformations)

        logging.info(
            "Transform staging selesai."
        )

    # ========================================================
    # WIRING
    # Cuma sampai staging dulu sesuai arahan -> load_to_dwh
    # menyusul belakangan setelah semua source aman di staging.
    # ========================================================
    
        # ========================================================
    # TASK: LOAD STAGING -> DATA WAREHOUSE
    # ========================================================

    @task
    def load_to_dwh():

        logging.info("Memulai proses load ke Data Warehouse...")

        transformations = [

            # =================================================
            # DIM WAKTU
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{dwh_db}`.`dim_waktu`;
            """,

            f"""
            CREATE TABLE `{dwh_db}`.`dim_waktu` AS

            SELECT
                id_waktu,
                tahun,
                semester,
                tanggal_mulai,
                tanggal_selesai,
                status_periode
            FROM `{staging_db}`.`stg_waktu`;
            """,

            # =================================================
            # DIM SEKOLAH
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{dwh_db}`.`dim_sekolah`;
            """,

            f"""
            CREATE TABLE `{dwh_db}`.`dim_sekolah` AS

            SELECT
                id_sekolah,
                npsn,
                nama_sekolah,
                jenjang,
                status_sekolah,
                akreditasi,
                id_desa,
                alamat_sekolah,
                status_operasional,
                tahun_berdiri
            FROM `{staging_db}`.`stg_sekolah`;
            """,

            # =================================================
            # DIM PTK
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{dwh_db}`.`dim_ptk`;
            """,

            f"""
            CREATE TABLE `{dwh_db}`.`dim_ptk` AS

            SELECT
                id_ptk,
                nik,
                nuptk,
                nama_ptk,
                jenis_kelamin,
                id_sekolah,
                jenis_ptk,
                status_kepegawaian,
                pendidikan_terakhir,
                bidang_studi,
                jabatan,
                tahun_masuk,
                status_ptk
            FROM `{staging_db}`.`stg_ptk`;
            """,

            # =================================================
            # FACT PENDIDIKAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{dwh_db}`.`fact_pendidikan`;
            """,

            f"""
            CREATE TABLE `{dwh_db}`.`fact_pendidikan` AS

            SELECT
                id_pendidikan,
                id_sekolah,
                id_waktu,
                jumlah_siswa,
                jumlah_guru,
                jumlah_rombel,
                jumlah_mapel,
                jumlah_jam_pembelajaran,
                rata_rata_nilai,
                persentase_kelulusan,
                jumlah_lulus,
                jumlah_mengulang,
                jumlah_putus_sekolah
            FROM `{staging_db}`.`stg_pendidikan`;
            """,

        ]

        execute_sql(transformations)

        logging.info(
            "Load Data Warehouse Pendidikan selesai."
        )
    t1 = extract_to_raw()
    t2 = transform_staging()
    t3 = load_to_dwh()

    t1 >> t2 >> t3



    return t2