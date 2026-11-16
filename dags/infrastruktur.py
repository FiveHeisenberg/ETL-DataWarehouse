from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN INFRASTRUKTUR
# ============================================================

SOURCE_ENDPOINTS = {
    "tb_jalan":        "/jalan",
    "tb_jembatan":     "/jembatan",
    "tb_perumahan":    "/perumahan",
    "tb_pengairan":    "/pengairan",
    "tb_transportasi": "/transportasi",
}


# ============================================================
# PIPELINE INFRASTRUKTUR
# ============================================================

def create_infrastruktur_tasks(
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

    @task(task_id="extract_to_raw_infrastruktur")
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

    @task(task_id="transform_staging_infrastruktur")
    def transform_staging():

        logging.info(
            "Memulai proses transform Infrastruktur..."
        )

        transformations = [

            # =================================================
            # JALAN (ROADS)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_jalan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_jalan` (
                id_jalan INT UNSIGNED PRIMARY KEY,
                nama_jalan VARCHAR(80),
                lokasi VARCHAR(80),
                tipe_jalan VARCHAR(50),
                panjang_km DECIMAL(6,2),
                lebar_m DECIMAL(4,2),
                jenis_permukaan VARCHAR(50),
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_pemeliharaan_terakhir YEAR,
                nama_proyek VARCHAR(120),
                kontraktor_pelaksana VARCHAR(80),
                anggaran_rupiah BIGINT,
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_jalan`
            SELECT DISTINCT
                CAST(id_jalan AS UNSIGNED) AS id_jalan,
                NULLIF(TRIM(nama_jalan), '') AS nama_jalan,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                CASE
                    WHEN TRIM(tipe_jalan) IN ('nasional','provinsi','kabupaten','desa')
                    THEN TRIM(tipe_jalan)
                    ELSE NULL
                END AS tipe_jalan,
                CASE
                    WHEN CAST(panjang_km AS DECIMAL(6,2)) > 0
                    THEN CAST(panjang_km AS DECIMAL(6,2))
                    ELSE NULL
                END AS panjang_km,
                CASE
                    WHEN CAST(lebar_m AS DECIMAL(4,2)) > 0
                    THEN CAST(lebar_m AS DECIMAL(4,2))
                    ELSE NULL
                END AS lebar_m,
                CASE
                    WHEN TRIM(jenis_permukaan) IN ('aspal','beton','tanah','kerikil')
                    THEN TRIM(jenis_permukaan)
                    ELSE NULL
                END AS jenis_permukaan,
                CASE
                    WHEN TRIM(kondisi) IN ('baik','sedang','rusak ringan','rusak berat')
                    THEN TRIM(kondisi)
                    ELSE NULL
                END AS kondisi,
                CASE
                    WHEN CAST(tahun_pembangunan AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pembangunan AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pembangunan,
                CASE
                    WHEN tahun_pemeliharaan_terakhir IS NOT NULL
                    AND CAST(tahun_pemeliharaan_terakhir AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pemeliharaan_terakhir AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pemeliharaan_terakhir,
                NULLIF(TRIM(nama_proyek), '') AS nama_proyek,
                NULLIF(TRIM(kontraktor_pelaksana), '') AS kontraktor_pelaksana,
                CASE
                    WHEN anggaran_rupiah IS NOT NULL
                    AND CAST(anggaran_rupiah AS UNSIGNED) > 0
                    THEN CAST(anggaran_rupiah AS UNSIGNED)
                    ELSE NULL
                END AS anggaran_rupiah,
                CASE
                    WHEN TRIM(status_proyek) IN ('operasional','dalam perbaikan','perencanaan')
                    THEN TRIM(status_proyek)
                    ELSE NULL
                END AS status_proyek,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_jalan`
            WHERE
                id_jalan IS NOT NULL
                AND CAST(id_jalan AS UNSIGNED) > 0
                AND nama_jalan IS NOT NULL
                AND TRIM(nama_jalan) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> '';
            """,

            # =================================================
            # JEMBATAN (BRIDGES)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_jembatan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_jembatan` (
                id_jembatan INT UNSIGNED PRIMARY KEY,
                nama_jembatan VARCHAR(80),
                lokasi VARCHAR(80),
                panjang_m DECIMAL(6,2),
                lebar_m DECIMAL(4,2),
                tipe_jembatan VARCHAR(50),
                kapasitas_beban_ton TINYINT UNSIGNED,
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_pemeliharaan_terakhir YEAR,
                nama_proyek VARCHAR(120),
                kontraktor_pelaksana VARCHAR(80),
                anggaran_rupiah BIGINT,
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_jembatan`
            SELECT DISTINCT
                CAST(id_jembatan AS UNSIGNED) AS id_jembatan,
                NULLIF(TRIM(nama_jembatan), '') AS nama_jembatan,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                CASE
                    WHEN CAST(panjang_m AS DECIMAL(6,2)) > 0
                    THEN CAST(panjang_m AS DECIMAL(6,2))
                    ELSE NULL
                END AS panjang_m,
                CASE
                    WHEN CAST(lebar_m AS DECIMAL(4,2)) > 0
                    THEN CAST(lebar_m AS DECIMAL(4,2))
                    ELSE NULL
                END AS lebar_m,
                CASE
                    WHEN TRIM(tipe_jembatan) IN ('beton','baja','gantung','bailey','kayu')
                    THEN TRIM(tipe_jembatan)
                    ELSE NULL
                END AS tipe_jembatan,
                CASE
                    WHEN CAST(kapasitas_beban_ton AS UNSIGNED) > 0
                    THEN CAST(kapasitas_beban_ton AS UNSIGNED)
                    ELSE NULL
                END AS kapasitas_beban_ton,
                CASE
                    WHEN TRIM(kondisi) IN ('baik','sedang','rusak ringan','rusak berat')
                    THEN TRIM(kondisi)
                    ELSE NULL
                END AS kondisi,
                CASE
                    WHEN CAST(tahun_pembangunan AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pembangunan AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pembangunan,
                CASE
                    WHEN tahun_pemeliharaan_terakhir IS NOT NULL
                    AND CAST(tahun_pemeliharaan_terakhir AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pemeliharaan_terakhir AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pemeliharaan_terakhir,
                NULLIF(TRIM(nama_proyek), '') AS nama_proyek,
                NULLIF(TRIM(kontraktor_pelaksana), '') AS kontraktor_pelaksana,
                CASE
                    WHEN anggaran_rupiah IS NOT NULL
                    AND CAST(anggaran_rupiah AS UNSIGNED) > 0
                    THEN CAST(anggaran_rupiah AS UNSIGNED)
                    ELSE NULL
                END AS anggaran_rupiah,
                CASE
                    WHEN TRIM(status_proyek) IN ('operasional','dalam perbaikan','perencanaan')
                    THEN TRIM(status_proyek)
                    ELSE NULL
                END AS status_proyek,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_jembatan`
            WHERE
                id_jembatan IS NOT NULL
                AND CAST(id_jembatan AS UNSIGNED) > 0
                AND nama_jembatan IS NOT NULL
                AND TRIM(nama_jembatan) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> '';
            """,

            # =================================================
            # PERUMAHAN (HOUSING)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_perumahan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_perumahan` (
                id_perumahan INT UNSIGNED PRIMARY KEY,
                nama_proyek VARCHAR(120),
                lokasi VARCHAR(80),
                jenis_program VARCHAR(100),
                jumlah_unit SMALLINT UNSIGNED,
                luas_area_m2 DECIMAL(8,2),
                status_kepemilikan VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_selesai YEAR,
                persentase_penyelesaian TINYINT UNSIGNED,
                pengelola VARCHAR(80),
                anggaran_rupiah BIGINT,
                jumlah_penghuni INT UNSIGNED,
                kondisi_bangunan VARCHAR(50),
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_perumahan`
            SELECT DISTINCT
                CAST(id_perumahan AS UNSIGNED) AS id_perumahan,
                NULLIF(TRIM(nama_proyek), '') AS nama_proyek,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                CASE
                    WHEN TRIM(jenis_program) IN ('rumah rakyat','subsidi','relokasi bencana','kampung layak','rusunawa')
                    THEN TRIM(jenis_program)
                    ELSE NULL
                END AS jenis_program,
                CASE
                    WHEN CAST(jumlah_unit AS UNSIGNED) > 0
                    THEN CAST(jumlah_unit AS UNSIGNED)
                    ELSE NULL
                END AS jumlah_unit,
                CASE
                    WHEN luas_area_m2 IS NOT NULL
                    AND CAST(luas_area_m2 AS DECIMAL(8,2)) > 0
                    THEN CAST(luas_area_m2 AS DECIMAL(8,2))
                    ELSE NULL
                END AS luas_area_m2,
                CASE
                    WHEN TRIM(status_kepemilikan) IN ('hak milik','sewa','hibah')
                    THEN TRIM(status_kepemilikan)
                    ELSE NULL
                END AS status_kepemilikan,
                CASE
                    WHEN CAST(tahun_pembangunan AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pembangunan AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pembangunan,
                CASE
                    WHEN tahun_selesai IS NOT NULL
                    AND CAST(tahun_selesai AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())+10
                    THEN CAST(tahun_selesai AS UNSIGNED)
                    ELSE NULL
                END AS tahun_selesai,
                CASE
                    WHEN CAST(persentase_penyelesaian AS UNSIGNED) BETWEEN 0 AND 100
                    THEN CAST(persentase_penyelesaian AS UNSIGNED)
                    ELSE 0
                END AS persentase_penyelesaian,
                NULLIF(TRIM(pengelola), '') AS pengelola,
                CASE
                    WHEN anggaran_rupiah IS NOT NULL
                    AND CAST(anggaran_rupiah AS UNSIGNED) > 0
                    THEN CAST(anggaran_rupiah AS UNSIGNED)
                    ELSE NULL
                END AS anggaran_rupiah,
                CASE
                    WHEN jumlah_penghuni IS NOT NULL
                    AND CAST(jumlah_penghuni AS UNSIGNED) >= 0
                    THEN CAST(jumlah_penghuni AS UNSIGNED)
                    ELSE NULL
                END AS jumlah_penghuni,
                CASE
                    WHEN TRIM(kondisi_bangunan) IN ('baik','sedang','rusak')
                    THEN TRIM(kondisi_bangunan)
                    ELSE NULL
                END AS kondisi_bangunan,
                CASE
                    WHEN TRIM(status_proyek) IN ('perencanaan','konstruksi','selesai','ditangguhkan')
                    THEN TRIM(status_proyek)
                    ELSE NULL
                END AS status_proyek,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_perumahan`
            WHERE
                id_perumahan IS NOT NULL
                AND CAST(id_perumahan AS UNSIGNED) > 0
                AND nama_proyek IS NOT NULL
                AND TRIM(nama_proyek) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> '';
            """,

            # =================================================
            # PENGAIRAN (IRRIGATION)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pengairan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pengairan` (
                id_pengairan INT UNSIGNED PRIMARY KEY,
                nama_aset VARCHAR(80),
                jenis_aset VARCHAR(100),
                lokasi VARCHAR(80),
                luas_layanan_ha DECIMAL(8,2),
                panjang_saluran_km DECIMAL(6,2),
                kapasitas_debit_m3 DECIMAL(8,2),
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_pemeliharaan_terakhir YEAR,
                nama_proyek VARCHAR(120),
                kontraktor_pelaksana VARCHAR(80),
                anggaran_rupiah BIGINT,
                status_operasional VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_pengairan`
            SELECT DISTINCT
                CAST(id_pengairan AS UNSIGNED) AS id_pengairan,
                NULLIF(TRIM(nama_aset), '') AS nama_aset,
                CASE
                    WHEN TRIM(jenis_aset) IN ('bendungan','saluran primer','saluran sekunder','embung','sumur bor')
                    THEN TRIM(jenis_aset)
                    ELSE NULL
                END AS jenis_aset,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                CASE
                    WHEN luas_layanan_ha IS NOT NULL
                    AND CAST(luas_layanan_ha AS DECIMAL(8,2)) > 0
                    THEN CAST(luas_layanan_ha AS DECIMAL(8,2))
                    ELSE NULL
                END AS luas_layanan_ha,
                CASE
                    WHEN panjang_saluran_km IS NOT NULL
                    AND CAST(panjang_saluran_km AS DECIMAL(6,2)) > 0
                    THEN CAST(panjang_saluran_km AS DECIMAL(6,2))
                    ELSE NULL
                END AS panjang_saluran_km,
                CASE
                    WHEN kapasitas_debit_m3 IS NOT NULL
                    AND CAST(kapasitas_debit_m3 AS DECIMAL(8,2)) > 0
                    THEN CAST(kapasitas_debit_m3 AS DECIMAL(8,2))
                    ELSE NULL
                END AS kapasitas_debit_m3,
                CASE
                    WHEN TRIM(kondisi) IN ('baik','sedang','rusak ringan','rusak berat')
                    THEN TRIM(kondisi)
                    ELSE NULL
                END AS kondisi,
                CASE
                    WHEN CAST(tahun_pembangunan AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pembangunan AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pembangunan,
                CASE
                    WHEN tahun_pemeliharaan_terakhir IS NOT NULL
                    AND CAST(tahun_pemeliharaan_terakhir AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pemeliharaan_terakhir AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pemeliharaan_terakhir,
                NULLIF(TRIM(nama_proyek), '') AS nama_proyek,
                NULLIF(TRIM(kontraktor_pelaksana), '') AS kontraktor_pelaksana,
                CASE
                    WHEN anggaran_rupiah IS NOT NULL
                    AND CAST(anggaran_rupiah AS UNSIGNED) > 0
                    THEN CAST(anggaran_rupiah AS UNSIGNED)
                    ELSE NULL
                END AS anggaran_rupiah,
                CASE
                    WHEN TRIM(status_operasional) IN ('beroperasi','tidak beroperasi','dalam perbaikan')
                    THEN TRIM(status_operasional)
                    ELSE NULL
                END AS status_operasional,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_pengairan`
            WHERE
                id_pengairan IS NOT NULL
                AND CAST(id_pengairan AS UNSIGNED) > 0
                AND nama_aset IS NOT NULL
                AND TRIM(nama_aset) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> '';
            """,

            # =================================================
            # TRANSPORTASI (PUBLIC TRANSPORTATION)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_transportasi`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_transportasi` (
                id_transportasi INT UNSIGNED PRIMARY KEY,
                nama_aset VARCHAR(80),
                jenis_aset VARCHAR(100),
                lokasi VARCHAR(80),
                kapasitas_penumpang INT UNSIGNED,
                luas_area_m2 DECIMAL(8,2),
                fasilitas VARCHAR(120),
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_renovasi_terakhir YEAR,
                pengelola VARCHAR(80),
                anggaran_pembangunan_rupiah BIGINT,
                status_operasional VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_transportasi`
            SELECT DISTINCT
                CAST(id_transportasi AS UNSIGNED) AS id_transportasi,
                NULLIF(TRIM(nama_aset), '') AS nama_aset,
                CASE
                    WHEN TRIM(jenis_aset) IN ('terminal bus','pelabuhan','bandara','halte','pool','dermaga')
                    THEN TRIM(jenis_aset)
                    ELSE NULL
                END AS jenis_aset,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                CASE
                    WHEN kapasitas_penumpang IS NOT NULL
                    AND CAST(kapasitas_penumpang AS UNSIGNED) >= 0
                    THEN CAST(kapasitas_penumpang AS UNSIGNED)
                    ELSE NULL
                END AS kapasitas_penumpang,
                CASE
                    WHEN luas_area_m2 IS NOT NULL
                    AND CAST(luas_area_m2 AS DECIMAL(8,2)) > 0
                    THEN CAST(luas_area_m2 AS DECIMAL(8,2))
                    ELSE NULL
                END AS luas_area_m2,
                NULLIF(TRIM(fasilitas), '') AS fasilitas,
                CASE
                    WHEN TRIM(kondisi) IN ('baik','sedang','rusak')
                    THEN TRIM(kondisi)
                    ELSE NULL
                END AS kondisi,
                CASE
                    WHEN CAST(tahun_pembangunan AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_pembangunan AS UNSIGNED)
                    ELSE NULL
                END AS tahun_pembangunan,
                CASE
                    WHEN tahun_renovasi_terakhir IS NOT NULL
                    AND CAST(tahun_renovasi_terakhir AS UNSIGNED) BETWEEN 1900 AND YEAR(CURDATE())
                    THEN CAST(tahun_renovasi_terakhir AS UNSIGNED)
                    ELSE NULL
                END AS tahun_renovasi_terakhir,
                NULLIF(TRIM(pengelola), '') AS pengelola,
                CASE
                    WHEN anggaran_pembangunan_rupiah IS NOT NULL
                    AND CAST(anggaran_pembangunan_rupiah AS UNSIGNED) > 0
                    THEN CAST(anggaran_pembangunan_rupiah AS UNSIGNED)
                    ELSE NULL
                END AS anggaran_pembangunan_rupiah,
                CASE
                    WHEN TRIM(status_operasional) IN ('beroperasi','tutup sementara','dalam renovasi')
                    THEN TRIM(status_operasional)
                    ELSE NULL
                END AS status_operasional,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_transportasi`
            WHERE
                id_transportasi IS NOT NULL
                AND CAST(id_transportasi AS UNSIGNED) > 0
                AND nama_aset IS NOT NULL
                AND TRIM(nama_aset) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> '';
            """,
        ]

        execute_sql(transformations)

        logging.info(
            "Transform staging Infrastruktur selesai."
        )


    # ========================================================
    # TASK: LOAD -> DATA WAREHOUSE
    # ========================================================

    @task(task_id="load_to_dwh_infrastruktur")
    def load_to_dwh():

        logging.info(
            "Membuat dimension dan fact Infrastruktur..."
        )

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        dwh_tables = [
            "dim_waktu",
            "dim_lokasi",
            "dim_kontraktor",
            "fact_jalan",
            "fact_jembatan",
            "fact_perumahan",
            "fact_pengairan",
            "fact_transportasi",
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
            # DIM LOKASI
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_lokasi`
            (
                lokasi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                lokasi VARCHAR(80) NOT NULL,
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_lokasi (lokasi)
            );
            """,

            # ------------------------------------------------
            # DIM KONTRAKTOR
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kontraktor`
            (
                kontraktor_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                kontraktor_pelaksana VARCHAR(80) NOT NULL,
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_kontraktor (kontraktor_pelaksana)
            );
            """,

            # ------------------------------------------------
            # FACT JALAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_jalan`
            (
                fact_jalan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_jalan INT NOT NULL,
                nama_jalan VARCHAR(80),
                lokasi_key BIGINT,
                kontraktor_key BIGINT,
                waktu_key INT NOT NULL,
                tipe_jalan VARCHAR(50),
                panjang_km DECIMAL(6,2),
                lebar_m DECIMAL(4,2),
                jenis_permukaan VARCHAR(50),
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_pemeliharaan_terakhir YEAR,
                nama_proyek VARCHAR(120),
                anggaran_rupiah BIGINT,
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_jalan (id_jalan),
                KEY idx_fact_jalan_lokasi (lokasi_key),
                KEY idx_fact_jalan_kontraktor (kontraktor_key),
                KEY idx_fact_jalan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT JEMBATAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_jembatan`
            (
                fact_jembatan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_jembatan INT NOT NULL,
                nama_jembatan VARCHAR(80),
                lokasi_key BIGINT,
                kontraktor_key BIGINT,
                waktu_key INT NOT NULL,
                panjang_m DECIMAL(6,2),
                lebar_m DECIMAL(4,2),
                tipe_jembatan VARCHAR(50),
                kapasitas_beban_ton TINYINT UNSIGNED,
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_pemeliharaan_terakhir YEAR,
                nama_proyek VARCHAR(120),
                anggaran_rupiah BIGINT,
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_jembatan (id_jembatan),
                KEY idx_fact_jembatan_lokasi (lokasi_key),
                KEY idx_fact_jembatan_kontraktor (kontraktor_key),
                KEY idx_fact_jembatan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT PERUMAHAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_perumahan`
            (
                fact_perumahan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_perumahan INT NOT NULL,
                nama_proyek VARCHAR(120),
                lokasi_key BIGINT,
                waktu_key INT NOT NULL,
                jenis_program VARCHAR(100),
                jumlah_unit SMALLINT UNSIGNED,
                luas_area_m2 DECIMAL(8,2),
                status_kepemilikan VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_selesai YEAR,
                persentase_penyelesaian TINYINT UNSIGNED,
                pengelola VARCHAR(80),
                anggaran_rupiah BIGINT,
                jumlah_penghuni INT UNSIGNED,
                kondisi_bangunan VARCHAR(50),
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_perumahan (id_perumahan),
                KEY idx_fact_perumahan_lokasi (lokasi_key),
                KEY idx_fact_perumahan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT PENGAIRAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pengairan`
            (
                fact_pengairan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_pengairan INT NOT NULL,
                nama_aset VARCHAR(80),
                lokasi_key BIGINT,
                kontraktor_key BIGINT,
                waktu_key INT NOT NULL,
                jenis_aset VARCHAR(100),
                luas_layanan_ha DECIMAL(8,2),
                panjang_saluran_km DECIMAL(6,2),
                kapasitas_debit_m3 DECIMAL(8,2),
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_pemeliharaan_terakhir YEAR,
                nama_proyek VARCHAR(120),
                anggaran_rupiah BIGINT,
                status_operasional VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_pengairan (id_pengairan),
                KEY idx_fact_pengairan_lokasi (lokasi_key),
                KEY idx_fact_pengairan_kontraktor (kontraktor_key),
                KEY idx_fact_pengairan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT TRANSPORTASI
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_transportasi`
            (
                fact_transportasi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_transportasi INT NOT NULL,
                nama_aset VARCHAR(80),
                lokasi_key BIGINT,
                waktu_key INT NOT NULL,
                jenis_aset VARCHAR(100),
                kapasitas_penumpang INT UNSIGNED,
                luas_area_m2 DECIMAL(8,2),
                fasilitas VARCHAR(120),
                kondisi VARCHAR(50),
                tahun_pembangunan YEAR,
                tahun_renovasi_terakhir YEAR,
                pengelola VARCHAR(80),
                anggaran_pembangunan_rupiah BIGINT,
                status_operasional VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_transportasi (id_transportasi),
                KEY idx_fact_transportasi_lokasi (lokasi_key),
                KEY idx_fact_transportasi_waktu (waktu_key)
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
            # Menggunakan tahun_pembangunan dari semua tabel
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
                SELECT CONCAT(tahun_pembangunan, '-01-01') AS tanggal
                FROM `{staging_db}`.`stg_jalan`
                WHERE tahun_pembangunan IS NOT NULL

                UNION

                SELECT CONCAT(tahun_pembangunan, '-01-01')
                FROM `{staging_db}`.`stg_jembatan`
                WHERE tahun_pembangunan IS NOT NULL

                UNION

                SELECT CONCAT(tahun_pembangunan, '-01-01')
                FROM `{staging_db}`.`stg_perumahan`
                WHERE tahun_pembangunan IS NOT NULL

                UNION

                SELECT CONCAT(tahun_pembangunan, '-01-01')
                FROM `{staging_db}`.`stg_pengairan`
                WHERE tahun_pembangunan IS NOT NULL

                UNION

                SELECT CONCAT(tahun_pembangunan, '-01-01')
                FROM `{staging_db}`.`stg_transportasi`
                WHERE tahun_pembangunan IS NOT NULL
            ) t
            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM LOKASI
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_lokasi`
            (
                lokasi,
                waktu_load
            )
            SELECT DISTINCT
                lokasi,
                NOW()
            FROM
            (
                SELECT lokasi FROM `{staging_db}`.`stg_jalan`
                WHERE lokasi IS NOT NULL
                UNION
                SELECT lokasi FROM `{staging_db}`.`stg_jembatan`
                WHERE lokasi IS NOT NULL
                UNION
                SELECT lokasi FROM `{staging_db}`.`stg_perumahan`
                WHERE lokasi IS NOT NULL
                UNION
                SELECT lokasi FROM `{staging_db}`.`stg_pengairan`
                WHERE lokasi IS NOT NULL
                UNION
                SELECT lokasi FROM `{staging_db}`.`stg_transportasi`
                WHERE lokasi IS NOT NULL
            ) t
            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM KONTRAKTOR
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kontraktor`
            (
                kontraktor_pelaksana,
                waktu_load
            )
            SELECT DISTINCT
                kontraktor_pelaksana,
                NOW()
            FROM
            (
                SELECT kontraktor_pelaksana FROM `{staging_db}`.`stg_jalan`
                WHERE kontraktor_pelaksana IS NOT NULL
                UNION
                SELECT kontraktor_pelaksana FROM `{staging_db}`.`stg_jembatan`
                WHERE kontraktor_pelaksana IS NOT NULL
                UNION
                SELECT kontraktor_pelaksana FROM `{staging_db}`.`stg_pengairan`
                WHERE kontraktor_pelaksana IS NOT NULL
            ) t
            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FACT
        # ====================================================

        load_facts = [

            # ------------------------------------------------
            # FACT JALAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_jalan`
            (
                id_jalan,
                nama_jalan,
                lokasi_key,
                kontraktor_key,
                waktu_key,
                tipe_jalan,
                panjang_km,
                lebar_m,
                jenis_permukaan,
                kondisi,
                tahun_pembangunan,
                tahun_pemeliharaan_terakhir,
                nama_proyek,
                anggaran_rupiah,
                status_proyek,
                sumber_database,
                waktu_load
            )
            SELECT
                s.id_jalan,
                s.nama_jalan,
                dl.lokasi_key,
                dk.kontraktor_key,
                CAST(
                    DATE_FORMAT(CONCAT(s.tahun_pembangunan, '-01-01'), '%Y%m%d')
                    AS UNSIGNED
                ),
                s.tipe_jalan,
                s.panjang_km,
                s.lebar_m,
                s.jenis_permukaan,
                s.kondisi,
                s.tahun_pembangunan,
                s.tahun_pemeliharaan_terakhir,
                s.nama_proyek,
                s.anggaran_rupiah,
                s.status_proyek,
                s.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_jalan` s
            LEFT JOIN `{dwh_db}`.`dim_lokasi` dl
                ON s.lokasi = dl.lokasi
            LEFT JOIN `{dwh_db}`.`dim_kontraktor` dk
                ON s.kontraktor_pelaksana = dk.kontraktor_pelaksana
            ON DUPLICATE KEY UPDATE
                nama_jalan = VALUES(nama_jalan),
                lokasi_key = VALUES(lokasi_key),
                kontraktor_key = VALUES(kontraktor_key),
                waktu_key = VALUES(waktu_key),
                tipe_jalan = VALUES(tipe_jalan),
                panjang_km = VALUES(panjang_km),
                lebar_m = VALUES(lebar_m),
                jenis_permukaan = VALUES(jenis_permukaan),
                kondisi = VALUES(kondisi),
                tahun_pembangunan = VALUES(tahun_pembangunan),
                tahun_pemeliharaan_terakhir = VALUES(tahun_pemeliharaan_terakhir),
                nama_proyek = VALUES(nama_proyek),
                anggaran_rupiah = VALUES(anggaran_rupiah),
                status_proyek = VALUES(status_proyek),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT JEMBATAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_jembatan`
            (
                id_jembatan,
                nama_jembatan,
                lokasi_key,
                kontraktor_key,
                waktu_key,
                panjang_m,
                lebar_m,
                tipe_jembatan,
                kapasitas_beban_ton,
                kondisi,
                tahun_pembangunan,
                tahun_pemeliharaan_terakhir,
                nama_proyek,
                anggaran_rupiah,
                status_proyek,
                sumber_database,
                waktu_load
            )
            SELECT
                s.id_jembatan,
                s.nama_jembatan,
                dl.lokasi_key,
                dk.kontraktor_key,
                CAST(
                    DATE_FORMAT(CONCAT(s.tahun_pembangunan, '-01-01'), '%Y%m%d')
                    AS UNSIGNED
                ),
                s.panjang_m,
                s.lebar_m,
                s.tipe_jembatan,
                s.kapasitas_beban_ton,
                s.kondisi,
                s.tahun_pembangunan,
                s.tahun_pemeliharaan_terakhir,
                s.nama_proyek,
                s.anggaran_rupiah,
                s.status_proyek,
                s.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_jembatan` s
            LEFT JOIN `{dwh_db}`.`dim_lokasi` dl
                ON s.lokasi = dl.lokasi
            LEFT JOIN `{dwh_db}`.`dim_kontraktor` dk
                ON s.kontraktor_pelaksana = dk.kontraktor_pelaksana
            ON DUPLICATE KEY UPDATE
                nama_jembatan = VALUES(nama_jembatan),
                lokasi_key = VALUES(lokasi_key),
                kontraktor_key = VALUES(kontraktor_key),
                waktu_key = VALUES(waktu_key),
                panjang_m = VALUES(panjang_m),
                lebar_m = VALUES(lebar_m),
                tipe_jembatan = VALUES(tipe_jembatan),
                kapasitas_beban_ton = VALUES(kapasitas_beban_ton),
                kondisi = VALUES(kondisi),
                tahun_pembangunan = VALUES(tahun_pembangunan),
                tahun_pemeliharaan_terakhir = VALUES(tahun_pemeliharaan_terakhir),
                nama_proyek = VALUES(nama_proyek),
                anggaran_rupiah = VALUES(anggaran_rupiah),
                status_proyek = VALUES(status_proyek),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT PERUMAHAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_perumahan`
            (
                id_perumahan,
                nama_proyek,
                lokasi_key,
                waktu_key,
                jenis_program,
                jumlah_unit,
                luas_area_m2,
                status_kepemilikan,
                tahun_pembangunan,
                tahun_selesai,
                persentase_penyelesaian,
                pengelola,
                anggaran_rupiah,
                jumlah_penghuni,
                kondisi_bangunan,
                status_proyek,
                sumber_database,
                waktu_load
            )
            SELECT
                s.id_perumahan,
                s.nama_proyek,
                dl.lokasi_key,
                CAST(
                    DATE_FORMAT(CONCAT(s.tahun_pembangunan, '-01-01'), '%Y%m%d')
                    AS UNSIGNED
                ),
                s.jenis_program,
                s.jumlah_unit,
                s.luas_area_m2,
                s.status_kepemilikan,
                s.tahun_pembangunan,
                s.tahun_selesai,
                s.persentase_penyelesaian,
                s.pengelola,
                s.anggaran_rupiah,
                s.jumlah_penghuni,
                s.kondisi_bangunan,
                s.status_proyek,
                s.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_perumahan` s
            LEFT JOIN `{dwh_db}`.`dim_lokasi` dl
                ON s.lokasi = dl.lokasi
            ON DUPLICATE KEY UPDATE
                nama_proyek = VALUES(nama_proyek),
                lokasi_key = VALUES(lokasi_key),
                waktu_key = VALUES(waktu_key),
                jenis_program = VALUES(jenis_program),
                jumlah_unit = VALUES(jumlah_unit),
                luas_area_m2 = VALUES(luas_area_m2),
                status_kepemilikan = VALUES(status_kepemilikan),
                tahun_pembangunan = VALUES(tahun_pembangunan),
                tahun_selesai = VALUES(tahun_selesai),
                persentase_penyelesaian = VALUES(persentase_penyelesaian),
                pengelola = VALUES(pengelola),
                anggaran_rupiah = VALUES(anggaran_rupiah),
                jumlah_penghuni = VALUES(jumlah_penghuni),
                kondisi_bangunan = VALUES(kondisi_bangunan),
                status_proyek = VALUES(status_proyek),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT PENGAIRAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_pengairan`
            (
                id_pengairan,
                nama_aset,
                lokasi_key,
                kontraktor_key,
                waktu_key,
                jenis_aset,
                luas_layanan_ha,
                panjang_saluran_km,
                kapasitas_debit_m3,
                kondisi,
                tahun_pembangunan,
                tahun_pemeliharaan_terakhir,
                nama_proyek,
                anggaran_rupiah,
                status_operasional,
                sumber_database,
                waktu_load
            )
            SELECT
                s.id_pengairan,
                s.nama_aset,
                dl.lokasi_key,
                dk.kontraktor_key,
                CAST(
                    DATE_FORMAT(CONCAT(s.tahun_pembangunan, '-01-01'), '%Y%m%d')
                    AS UNSIGNED
                ),
                s.jenis_aset,
                s.luas_layanan_ha,
                s.panjang_saluran_km,
                s.kapasitas_debit_m3,
                s.kondisi,
                s.tahun_pembangunan,
                s.tahun_pemeliharaan_terakhir,
                s.nama_proyek,
                s.anggaran_rupiah,
                s.status_operasional,
                s.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_pengairan` s
            LEFT JOIN `{dwh_db}`.`dim_lokasi` dl
                ON s.lokasi = dl.lokasi
            LEFT JOIN `{dwh_db}`.`dim_kontraktor` dk
                ON s.kontraktor_pelaksana = dk.kontraktor_pelaksana
            ON DUPLICATE KEY UPDATE
                nama_aset = VALUES(nama_aset),
                lokasi_key = VALUES(lokasi_key),
                kontraktor_key = VALUES(kontraktor_key),
                waktu_key = VALUES(waktu_key),
                jenis_aset = VALUES(jenis_aset),
                luas_layanan_ha = VALUES(luas_layanan_ha),
                panjang_saluran_km = VALUES(panjang_saluran_km),
                kapasitas_debit_m3 = VALUES(kapasitas_debit_m3),
                kondisi = VALUES(kondisi),
                tahun_pembangunan = VALUES(tahun_pembangunan),
                tahun_pemeliharaan_terakhir = VALUES(tahun_pemeliharaan_terakhir),
                nama_proyek = VALUES(nama_proyek),
                anggaran_rupiah = VALUES(anggaran_rupiah),
                status_operasional = VALUES(status_operasional),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT TRANSPORTASI
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_transportasi`
            (
                id_transportasi,
                nama_aset,
                lokasi_key,
                waktu_key,
                jenis_aset,
                kapasitas_penumpang,
                luas_area_m2,
                fasilitas,
                kondisi,
                tahun_pembangunan,
                tahun_renovasi_terakhir,
                pengelola,
                anggaran_pembangunan_rupiah,
                status_operasional,
                sumber_database,
                waktu_load
            )
            SELECT
                s.id_transportasi,
                s.nama_aset,
                dl.lokasi_key,
                CAST(
                    DATE_FORMAT(CONCAT(s.tahun_pembangunan, '-01-01'), '%Y%m%d')
                    AS UNSIGNED
                ),
                s.jenis_aset,
                s.kapasitas_penumpang,
                s.luas_area_m2,
                s.fasilitas,
                s.kondisi,
                s.tahun_pembangunan,
                s.tahun_renovasi_terakhir,
                s.pengelola,
                s.anggaran_pembangunan_rupiah,
                s.status_operasional,
                s.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_transportasi` s
            LEFT JOIN `{dwh_db}`.`dim_lokasi` dl
                ON s.lokasi = dl.lokasi
            ON DUPLICATE KEY UPDATE
                nama_aset = VALUES(nama_aset),
                lokasi_key = VALUES(lokasi_key),
                waktu_key = VALUES(waktu_key),
                jenis_aset = VALUES(jenis_aset),
                kapasitas_penumpang = VALUES(kapasitas_penumpang),
                luas_area_m2 = VALUES(luas_area_m2),
                fasilitas = VALUES(fasilitas),
                kondisi = VALUES(kondisi),
                tahun_pembangunan = VALUES(tahun_pembangunan),
                tahun_renovasi_terakhir = VALUES(tahun_renovasi_terakhir),
                pengelola = VALUES(pengelola),
                anggaran_pembangunan_rupiah = VALUES(anggaran_pembangunan_rupiah),
                status_operasional = VALUES(status_operasional),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

        logging.info(
            "Load Infrastruktur ke Data Warehouse selesai."
        )


    # ========================================================
    # WIRING
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()
    t3 = load_to_dwh()

    t1 >> t2 >> t3

    return t3
