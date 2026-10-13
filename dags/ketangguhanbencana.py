from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN KETAHANAN BENCANA (KETABEN)
# ============================================================

SOURCE_ENDPOINTS = {
    "tb_bencana":           "/bencana",
    "tb_korban_bencana":    "/korban-bencana",
    "tb_kerusakan_bencana": "/kerusakan-bencana",
    "tb_bantuan":           "/bantuan",
    "tb_rehabilitasi":      "/rehabilitasi",
    "tb_rekonstruksi":      "/rekonstruksi",
}


# ============================================================
# PIPELINE KETANGGUHAN BENCANA
# ============================================================

def create_ketangguhanbencana_tasks(
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

    @task(task_id="extract_to_raw_ketaben")
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

    @task(task_id="transform_staging_ketaben")
    def transform_staging():

        logging.info(
            "Memulai proses transform Ketangguhan Bencana..."
        )

        transformations = [

            # =================================================
            # BENCANA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_bencana`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_bencana` (
                id_bencana INT UNSIGNED PRIMARY KEY,
                jenis_bencana VARCHAR(100),
                lokasi VARCHAR(150),
                deskripsi_kejadian TEXT,
                tanggal_kejadian DATETIME,
                tingkat_keparahan VARCHAR(50),
                status_tanggap VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_bencana`
            SELECT DISTINCT
                CAST(id_bencana AS UNSIGNED) AS id_bencana,
                NULLIF(TRIM(jenis_bencana), '') AS jenis_bencana,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                NULLIF(TRIM(deskripsi_kejadian), '') AS deskripsi_kejadian,
                CASE
                    WHEN tanggal_kejadian >= '1900-01-01' AND tanggal_kejadian <= NOW()
                    THEN tanggal_kejadian
                    ELSE NULL
                END AS tanggal_kejadian,
                CASE
                    WHEN TRIM(tingkat_keparahan) IN ('ringan', 'sedang', 'berat')
                    THEN TRIM(tingkat_keparahan)
                    ELSE NULL
                END AS tingkat_keparahan,
                CASE
                    WHEN TRIM(status_tanggap) IN ('tanggap darurat', 'pemulihan', 'selesai')
                    THEN TRIM(status_tanggap)
                    ELSE NULL
                END AS status_tanggap,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_bencana`
            WHERE
                id_bencana IS NOT NULL
                AND CAST(id_bencana AS UNSIGNED) > 0
                AND jenis_bencana IS NOT NULL
                AND TRIM(jenis_bencana) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> ''
                AND tanggal_kejadian IS NOT NULL;
            """,

            # =================================================
            # KORBAN BENCANA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_korban_bencana`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_korban_bencana` (
                id_korban INT UNSIGNED PRIMARY KEY,
                id_bencana INT UNSIGNED,
                jenis_korban VARCHAR(50),
                jumlah_korban INT UNSIGNED,
                keterangan VARCHAR(100),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_korban_bencana`
            SELECT DISTINCT
                CAST(id_korban AS UNSIGNED) AS id_korban,
                CAST(id_bencana AS UNSIGNED) AS id_bencana,
                CASE
                    WHEN TRIM(jenis_korban) IN ('meninggal', 'luka berat', 'luka ringan', 'hilang', 'mengungsi')
                    THEN TRIM(jenis_korban)
                    ELSE NULL
                END AS jenis_korban,
                CAST(jumlah_korban AS UNSIGNED) AS jumlah_korban,
                NULLIF(TRIM(keterangan), '') AS keterangan,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_korban_bencana`
            WHERE
                id_korban IS NOT NULL
                AND CAST(id_korban AS UNSIGNED) > 0
                AND id_bencana IS NOT NULL
                AND CAST(id_bencana AS UNSIGNED) > 0
                AND jenis_korban IS NOT NULL
                AND TRIM(jenis_korban) <> ''
                AND jumlah_korban IS NOT NULL
                AND CAST(jumlah_korban AS UNSIGNED) >= 0;
            """,

            # =================================================
            # KERUSAKAN BENCANA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kerusakan_bencana`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_kerusakan_bencana` (
                id_kerusakan INT UNSIGNED PRIMARY KEY,
                id_bencana INT UNSIGNED,
                jenis_objek VARCHAR(100),
                tingkat_kerusakan VARCHAR(50),
                jumlah_unit INT UNSIGNED,
                estimasi_kerugian_rupiah BIGINT,
                lokasi_kerusakan VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_kerusakan_bencana`
            SELECT DISTINCT
                CAST(id_kerusakan AS UNSIGNED) AS id_kerusakan,
                CAST(id_bencana AS UNSIGNED) AS id_bencana,
                NULLIF(TRIM(jenis_objek), '') AS jenis_objek,
                CASE
                    WHEN TRIM(tingkat_kerusakan) IN ('rusak ringan', 'rusak berat', 'rusak total')
                    THEN TRIM(tingkat_kerusakan)
                    ELSE NULL
                END AS tingkat_kerusakan,
                CAST(jumlah_unit AS UNSIGNED) AS jumlah_unit,
                CASE
                    WHEN estimasi_kerugian_rupiah IS NOT NULL 
                    AND CAST(estimasi_kerugian_rupiah AS SIGNED) >= 0
                    THEN CAST(estimasi_kerugian_rupiah AS SIGNED)
                    ELSE NULL
                END AS estimasi_kerugian_rupiah,
                NULLIF(TRIM(lokasi_kerusakan), '') AS lokasi_kerusakan,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_kerusakan_bencana`
            WHERE
                id_kerusakan IS NOT NULL
                AND CAST(id_kerusakan AS UNSIGNED) > 0
                AND id_bencana IS NOT NULL
                AND CAST(id_bencana AS UNSIGNED) > 0
                AND jenis_objek IS NOT NULL
                AND TRIM(jenis_objek) <> ''
                AND tingkat_kerusakan IS NOT NULL
                AND jumlah_unit IS NOT NULL
                AND lokasi_kerusakan IS NOT NULL
                AND TRIM(lokasi_kerusakan) <> '';
            """,

            # =================================================
            # BANTUAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_bantuan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_bantuan` (
                id_bantuan INT UNSIGNED PRIMARY KEY,
                id_bencana INT UNSIGNED,
                jenis_bantuan VARCHAR(150),
                sumber_bantuan VARCHAR(150),
                jumlah_bantuan VARCHAR(15),
                satuan VARCHAR(50),
                penerima_bantuan VARCHAR(200),
                tanggal_distribusi DATETIME,
                lokasi_distribusi VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_bantuan`
            SELECT DISTINCT
                CAST(id_bantuan AS UNSIGNED) AS id_bantuan,
                CAST(id_bencana AS UNSIGNED) AS id_bencana,
                NULLIF(TRIM(jenis_bantuan), '') AS jenis_bantuan,
                NULLIF(TRIM(sumber_bantuan), '') AS sumber_bantuan,
                NULLIF(TRIM(jumlah_bantuan), '') AS jumlah_bantuan,
                NULLIF(TRIM(satuan), '') AS satuan,
                NULLIF(TRIM(penerima_bantuan), '') AS penerima_bantuan,
                CASE
                    WHEN tanggal_distribusi >= '1900-01-01' AND tanggal_distribusi <= NOW()
                    THEN tanggal_distribusi
                    ELSE NULL
                END AS tanggal_distribusi,
                NULLIF(TRIM(lokasi_distribusi), '') AS lokasi_distribusi,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_bantuan`
            WHERE
                id_bantuan IS NOT NULL
                AND CAST(id_bantuan AS UNSIGNED) > 0
                AND id_bencana IS NOT NULL
                AND CAST(id_bencana AS UNSIGNED) > 0
                AND jenis_bantuan IS NOT NULL
                AND TRIM(jenis_bantuan) <> ''
                AND sumber_bantuan IS NOT NULL
                AND TRIM(sumber_bantuan) <> ''
                AND jumlah_bantuan IS NOT NULL
                AND satuan IS NOT NULL
                AND tanggal_distribusi IS NOT NULL
                AND lokasi_distribusi IS NOT NULL
                AND TRIM(lokasi_distribusi) <> '';
            """,

            # =================================================
            # REHABILITASI
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_rehabilitasi`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_rehabilitasi` (
                id_rehabilitasi INT UNSIGNED PRIMARY KEY,
                id_bencana INT UNSIGNED,
                jenis_rehabilitasi VARCHAR(150),
                lokasi VARCHAR(150),
                deskripsi_kegiatan TEXT,
                tanggal_mulai DATETIME,
                tanggal_selesai DATETIME,
                anggaran_rupiah BIGINT,
                sumber_dana VARCHAR(100),
                status_pelaksanaan VARCHAR(50),
                persentase_penyelesaian TINYINT UNSIGNED,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_rehabilitasi`
            SELECT DISTINCT
                CAST(id_rehabilitasi AS UNSIGNED) AS id_rehabilitasi,
                CAST(id_bencana AS UNSIGNED) AS id_bencana,
                NULLIF(TRIM(jenis_rehabilitasi), '') AS jenis_rehabilitasi,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                NULLIF(TRIM(deskripsi_kegiatan), '') AS deskripsi_kegiatan,
                CASE
                    WHEN tanggal_mulai >= '1900-01-01'
                    THEN tanggal_mulai
                    ELSE NULL
                END AS tanggal_mulai,
                CASE
                    WHEN tanggal_selesai >= '1900-01-01' 
                    AND tanggal_selesai >= tanggal_mulai
                    THEN tanggal_selesai
                    ELSE NULL
                END AS tanggal_selesai,
                CAST(anggaran_rupiah AS SIGNED) AS anggaran_rupiah,
                NULLIF(TRIM(sumber_dana), '') AS sumber_dana,
                CASE
                    WHEN TRIM(status_pelaksanaan) IN ('perencanaan', 'dalam proses', 'selesai', 'tertunda')
                    THEN TRIM(status_pelaksanaan)
                    ELSE NULL
                END AS status_pelaksanaan,
                CASE
                    WHEN CAST(persentase_penyelesaian AS UNSIGNED) <= 100
                    THEN CAST(persentase_penyelesaian AS UNSIGNED)
                    ELSE 0
                END AS persentase_penyelesaian,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_rehabilitasi`
            WHERE
                id_rehabilitasi IS NOT NULL
                AND CAST(id_rehabilitasi AS UNSIGNED) > 0
                AND id_bencana IS NOT NULL
                AND CAST(id_bencana AS UNSIGNED) > 0
                AND jenis_rehabilitasi IS NOT NULL
                AND TRIM(jenis_rehabilitasi) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> ''
                AND tanggal_mulai IS NOT NULL
                AND anggaran_rupiah IS NOT NULL
                AND sumber_dana IS NOT NULL
                AND status_pelaksanaan IS NOT NULL;
            """,

            # =================================================
            # REKONSTRUKSI
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_rekonstruksi`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_rekonstruksi` (
                id_rekonstruksi INT UNSIGNED PRIMARY KEY,
                id_bencana INT UNSIGNED,
                nama_proyek VARCHAR(200),
                jenis_pembangunan VARCHAR(150),
                lokasi VARCHAR(150),
                anggaran_rupiah BIGINT,
                sumber_dana VARCHAR(100),
                kontraktor_pelaksana VARCHAR(200),
                tanggal_mulai DATETIME,
                tanggal_target_selesai DATETIME,
                tanggal_selesai_aktual DATETIME,
                persentase_penyelesaian TINYINT UNSIGNED,
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            );
            """,

            f"""
            INSERT INTO `{staging_db}`.`stg_rekonstruksi`
            SELECT DISTINCT
                CAST(id_rekonstruksi AS UNSIGNED) AS id_rekonstruksi,
                CAST(id_bencana AS UNSIGNED) AS id_bencana,
                NULLIF(TRIM(nama_proyek), '') AS nama_proyek,
                NULLIF(TRIM(jenis_pembangunan), '') AS jenis_pembangunan,
                NULLIF(TRIM(lokasi), '') AS lokasi,
                CAST(anggaran_rupiah AS SIGNED) AS anggaran_rupiah,
                NULLIF(TRIM(sumber_dana), '') AS sumber_dana,
                NULLIF(TRIM(kontraktor_pelaksana), '') AS kontraktor_pelaksana,
                CASE
                    WHEN tanggal_mulai >= '1900-01-01'
                    THEN tanggal_mulai
                    ELSE NULL
                END AS tanggal_mulai,
                CASE
                    WHEN tanggal_target_selesai >= '1900-01-01'
                    AND tanggal_target_selesai >= tanggal_mulai
                    THEN tanggal_target_selesai
                    ELSE NULL
                END AS tanggal_target_selesai,
                CASE
                    WHEN tanggal_selesai_aktual >= '1900-01-01'
                    AND tanggal_selesai_aktual >= tanggal_mulai
                    THEN tanggal_selesai_aktual
                    ELSE NULL
                END AS tanggal_selesai_aktual,
                CASE
                    WHEN CAST(persentase_penyelesaian AS UNSIGNED) <= 100
                    THEN CAST(persentase_penyelesaian AS UNSIGNED)
                    ELSE 0
                END AS persentase_penyelesaian,
                CASE
                    WHEN TRIM(status_proyek) IN ('perencanaan', 'tender', 'konstruksi', 'selesai', 'ditangguhkan')
                    THEN TRIM(status_proyek)
                    ELSE NULL
                END AS status_proyek,
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_tb_rekonstruksi`
            WHERE
                id_rekonstruksi IS NOT NULL
                AND CAST(id_rekonstruksi AS UNSIGNED) > 0
                AND id_bencana IS NOT NULL
                AND CAST(id_bencana AS UNSIGNED) > 0
                AND nama_proyek IS NOT NULL
                AND TRIM(nama_proyek) <> ''
                AND jenis_pembangunan IS NOT NULL
                AND TRIM(jenis_pembangunan) <> ''
                AND lokasi IS NOT NULL
                AND TRIM(lokasi) <> ''
                AND anggaran_rupiah IS NOT NULL
                AND sumber_dana IS NOT NULL
                AND tanggal_mulai IS NOT NULL
                AND tanggal_target_selesai IS NOT NULL
                AND status_proyek IS NOT NULL;
            """,
        ]

        execute_sql(transformations)

        logging.info(
            "Transform staging Ketangguhan Bencana selesai."
        )

    # ========================================================
    # TASK: LOAD -> DATA WAREHOUSE
    # ========================================================

    @task(task_id="load_to_dwh_ketaben")
    def load_to_dwh():

        logging.info(
            "Membuat dimension dan fact Ketangguhan Bencana..."
        )

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        dwh_tables = [
            "dim_waktu",
            "dim_bencana",
            "dim_lokasi",
            "fact_korban",
            "fact_kerusakan",
            "fact_bantuan",
            "fact_rehabilitasi",
            "fact_rekonstruksi",
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
            # DIM BENCANA
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_bencana`
            (
                bencana_key INT AUTO_INCREMENT PRIMARY KEY,
                id_bencana INT NOT NULL,
                jenis_bencana VARCHAR(100),
                lokasi VARCHAR(150),
                tanggal_kejadian DATETIME,
                tingkat_keparahan VARCHAR(50),
                status_tanggap VARCHAR(50),
                deskripsi_kejadian TEXT,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_bencana (id_bencana)
            );
            """,

            # ------------------------------------------------
            # DIM LOKASI
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_lokasi`
            (
                lokasi_key INT AUTO_INCREMENT PRIMARY KEY,
                lokasi VARCHAR(150) NOT NULL,
                kabupaten_kota VARCHAR(100),
                kecamatan VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_lokasi (lokasi)
            );
            """,

            # ------------------------------------------------
            # FACT KORBAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_korban`
            (
                fact_korban_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_korban INT NOT NULL,
                bencana_key INT,
                waktu_key INT NOT NULL,
                jenis_korban VARCHAR(50),
                jumlah_korban INT,
                keterangan VARCHAR(100),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_korban (id_korban),
                KEY idx_fact_korban_bencana (bencana_key),
                KEY idx_fact_korban_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT KERUSAKAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kerusakan`
            (
                fact_kerusakan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_kerusakan INT NOT NULL,
                bencana_key INT,
                waktu_key INT NOT NULL,
                jenis_objek VARCHAR(100),
                tingkat_kerusakan VARCHAR(50),
                jumlah_unit INT,
                estimasi_kerugian_rupiah BIGINT,
                lokasi_kerusakan VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_kerusakan (id_kerusakan),
                KEY idx_fact_kerusakan_bencana (bencana_key),
                KEY idx_fact_kerusakan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT BANTUAN
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_bantuan`
            (
                fact_bantuan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_bantuan INT NOT NULL,
                bencana_key INT,
                waktu_key INT NOT NULL,
                jenis_bantuan VARCHAR(150),
                sumber_bantuan VARCHAR(150),
                jumlah_bantuan VARCHAR(15),
                satuan VARCHAR(50),
                penerima_bantuan VARCHAR(200),
                lokasi_distribusi VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_bantuan (id_bantuan),
                KEY idx_fact_bantuan_bencana (bencana_key),
                KEY idx_fact_bantuan_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT REHABILITASI
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_rehabilitasi`
            (
                fact_rehabilitasi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_rehabilitasi INT NOT NULL,
                bencana_key INT,
                waktu_key INT NOT NULL,
                jenis_rehabilitasi VARCHAR(150),
                lokasi VARCHAR(150),
                deskripsi_kegiatan TEXT,
                tanggal_mulai DATETIME,
                tanggal_selesai DATETIME,
                anggaran_rupiah BIGINT,
                sumber_dana VARCHAR(100),
                status_pelaksanaan VARCHAR(50),
                persentase_penyelesaian TINYINT,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_rehabilitasi (id_rehabilitasi),
                KEY idx_fact_rehabilitasi_bencana (bencana_key),
                KEY idx_fact_rehabilitasi_waktu (waktu_key)
            );
            """,

            # ------------------------------------------------
            # FACT REKONSTRUKSI
            # ------------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_rekonstruksi`
            (
                fact_rekonstruksi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_rekonstruksi INT NOT NULL,
                bencana_key INT,
                waktu_key INT NOT NULL,
                nama_proyek VARCHAR(200),
                jenis_pembangunan VARCHAR(150),
                lokasi VARCHAR(150),
                anggaran_rupiah BIGINT,
                sumber_dana VARCHAR(100),
                kontraktor_pelaksana VARCHAR(200),
                tanggal_mulai DATETIME,
                tanggal_target_selesai DATETIME,
                tanggal_selesai_aktual DATETIME,
                persentase_penyelesaian TINYINT,
                status_proyek VARCHAR(50),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_rekonstruksi (id_rekonstruksi),
                KEY idx_fact_rekonstruksi_bencana (bencana_key),
                KEY idx_fact_rekonstruksi_waktu (waktu_key)
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
                SELECT DATE(tanggal_kejadian) AS tanggal
                FROM `{staging_db}`.`stg_bencana`
                WHERE tanggal_kejadian IS NOT NULL

                UNION

                SELECT DATE(tanggal_distribusi)
                FROM `{staging_db}`.`stg_bantuan`
                WHERE tanggal_distribusi IS NOT NULL

                UNION

                SELECT DATE(tanggal_mulai)
                FROM `{staging_db}`.`stg_rehabilitasi`
                WHERE tanggal_mulai IS NOT NULL

                UNION

                SELECT DATE(tanggal_mulai)
                FROM `{staging_db}`.`stg_rekonstruksi`
                WHERE tanggal_mulai IS NOT NULL
            ) t
            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM BENCANA
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_bencana`
            (
                id_bencana,
                jenis_bencana,
                lokasi,
                tanggal_kejadian,
                tingkat_keparahan,
                status_tanggap,
                deskripsi_kejadian,
                sumber_database,
                waktu_load
            )
            SELECT
                id_bencana,
                jenis_bencana,
                lokasi,
                tanggal_kejadian,
                tingkat_keparahan,
                status_tanggap,
                deskripsi_kejadian,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_bencana`
            ON DUPLICATE KEY UPDATE
                jenis_bencana = VALUES(jenis_bencana),
                lokasi = VALUES(lokasi),
                tanggal_kejadian = VALUES(tanggal_kejadian),
                tingkat_keparahan = VALUES(tingkat_keparahan),
                status_tanggap = VALUES(status_tanggap),
                deskripsi_kejadian = VALUES(deskripsi_kejadian),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # DIM LOKASI
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_lokasi`
            (
                lokasi,
                kabupaten_kota,
                kecamatan,
                waktu_load
            )
            SELECT DISTINCT
                lokasi,
                SUBSTRING_INDEX(lokasi, ',', 1) AS kabupaten_kota,
                CASE 
                    WHEN LOCATE(',', lokasi) > 0 
                    THEN TRIM(SUBSTRING_INDEX(lokasi, ',', -1))
                    ELSE NULL
                END AS kecamatan,
                NOW()
            FROM `{staging_db}`.`stg_bencana`
            WHERE lokasi IS NOT NULL
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
            # FACT KORBAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_korban`
            (
                id_korban,
                bencana_key,
                waktu_key,
                jenis_korban,
                jumlah_korban,
                keterangan,
                sumber_database,
                waktu_load
            )
            SELECT
                sk.id_korban,
                db.bencana_key,
                CAST(
                    DATE_FORMAT(
                        (SELECT tanggal_kejadian FROM `{staging_db}`.`stg_bencana` WHERE id_bencana = sk.id_bencana),
                        '%Y%m%d'
                    ) AS UNSIGNED
                ),
                sk.jenis_korban,
                sk.jumlah_korban,
                sk.keterangan,
                sk.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_korban_bencana` sk
            LEFT JOIN `{dwh_db}`.`dim_bencana` db
                ON sk.id_bencana = db.id_bencana
            ON DUPLICATE KEY UPDATE
                bencana_key = VALUES(bencana_key),
                waktu_key = VALUES(waktu_key),
                jenis_korban = VALUES(jenis_korban),
                jumlah_korban = VALUES(jumlah_korban),
                keterangan = VALUES(keterangan),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT KERUSAKAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kerusakan`
            (
                id_kerusakan,
                bencana_key,
                waktu_key,
                jenis_objek,
                tingkat_kerusakan,
                jumlah_unit,
                estimasi_kerugian_rupiah,
                lokasi_kerusakan,
                sumber_database,
                waktu_load
            )
            SELECT
                sk.id_kerusakan,
                db.bencana_key,
                CAST(
                    DATE_FORMAT(
                        (SELECT tanggal_kejadian FROM `{staging_db}`.`stg_bencana` WHERE id_bencana = sk.id_bencana),
                        '%Y%m%d'
                    ) AS UNSIGNED
                ),
                sk.jenis_objek,
                sk.tingkat_kerusakan,
                sk.jumlah_unit,
                sk.estimasi_kerugian_rupiah,
                sk.lokasi_kerusakan,
                sk.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_kerusakan_bencana` sk
            LEFT JOIN `{dwh_db}`.`dim_bencana` db
                ON sk.id_bencana = db.id_bencana
            ON DUPLICATE KEY UPDATE
                bencana_key = VALUES(bencana_key),
                waktu_key = VALUES(waktu_key),
                jenis_objek = VALUES(jenis_objek),
                tingkat_kerusakan = VALUES(tingkat_kerusakan),
                jumlah_unit = VALUES(jumlah_unit),
                estimasi_kerugian_rupiah = VALUES(estimasi_kerugian_rupiah),
                lokasi_kerusakan = VALUES(lokasi_kerusakan),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT BANTUAN
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_bantuan`
            (
                id_bantuan,
                bencana_key,
                waktu_key,
                jenis_bantuan,
                sumber_bantuan,
                jumlah_bantuan,
                satuan,
                penerima_bantuan,
                lokasi_distribusi,
                sumber_database,
                waktu_load
            )
            SELECT
                sb.id_bantuan,
                db.bencana_key,
                CAST(
                    DATE_FORMAT(sb.tanggal_distribusi, '%Y%m%d')
                    AS UNSIGNED
                ),
                sb.jenis_bantuan,
                sb.sumber_bantuan,
                sb.jumlah_bantuan,
                sb.satuan,
                sb.penerima_bantuan,
                sb.lokasi_distribusi,
                sb.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_bantuan` sb
            LEFT JOIN `{dwh_db}`.`dim_bencana` db
                ON sb.id_bencana = db.id_bencana
            ON DUPLICATE KEY UPDATE
                bencana_key = VALUES(bencana_key),
                waktu_key = VALUES(waktu_key),
                jenis_bantuan = VALUES(jenis_bantuan),
                sumber_bantuan = VALUES(sumber_bantuan),
                jumlah_bantuan = VALUES(jumlah_bantuan),
                satuan = VALUES(satuan),
                penerima_bantuan = VALUES(penerima_bantuan),
                lokasi_distribusi = VALUES(lokasi_distribusi),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT REHABILITASI
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_rehabilitasi`
            (
                id_rehabilitasi,
                bencana_key,
                waktu_key,
                jenis_rehabilitasi,
                lokasi,
                deskripsi_kegiatan,
                tanggal_mulai,
                tanggal_selesai,
                anggaran_rupiah,
                sumber_dana,
                status_pelaksanaan,
                persentase_penyelesaian,
                sumber_database,
                waktu_load
            )
            SELECT
                sr.id_rehabilitasi,
                db.bencana_key,
                CAST(
                    DATE_FORMAT(sr.tanggal_mulai, '%Y%m%d')
                    AS UNSIGNED
                ),
                sr.jenis_rehabilitasi,
                sr.lokasi,
                sr.deskripsi_kegiatan,
                sr.tanggal_mulai,
                sr.tanggal_selesai,
                sr.anggaran_rupiah,
                sr.sumber_dana,
                sr.status_pelaksanaan,
                sr.persentase_penyelesaian,
                sr.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_rehabilitasi` sr
            LEFT JOIN `{dwh_db}`.`dim_bencana` db
                ON sr.id_bencana = db.id_bencana
            ON DUPLICATE KEY UPDATE
                bencana_key = VALUES(bencana_key),
                waktu_key = VALUES(waktu_key),
                jenis_rehabilitasi = VALUES(jenis_rehabilitasi),
                lokasi = VALUES(lokasi),
                deskripsi_kegiatan = VALUES(deskripsi_kegiatan),
                tanggal_mulai = VALUES(tanggal_mulai),
                tanggal_selesai = VALUES(tanggal_selesai),
                anggaran_rupiah = VALUES(anggaran_rupiah),
                sumber_dana = VALUES(sumber_dana),
                status_pelaksanaan = VALUES(status_pelaksanaan),
                persentase_penyelesaian = VALUES(persentase_penyelesaian),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # ------------------------------------------------
            # FACT REKONSTRUKSI
            # ------------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_rekonstruksi`
            (
                id_rekonstruksi,
                bencana_key,
                waktu_key,
                nama_proyek,
                jenis_pembangunan,
                lokasi,
                anggaran_rupiah,
                sumber_dana,
                kontraktor_pelaksana,
                tanggal_mulai,
                tanggal_target_selesai,
                tanggal_selesai_aktual,
                persentase_penyelesaian,
                status_proyek,
                sumber_database,
                waktu_load
            )
            SELECT
                sr.id_rekonstruksi,
                db.bencana_key,
                CAST(
                    DATE_FORMAT(sr.tanggal_mulai, '%Y%m%d')
                    AS UNSIGNED
                ),
                sr.nama_proyek,
                sr.jenis_pembangunan,
                sr.lokasi,
                sr.anggaran_rupiah,
                sr.sumber_dana,
                sr.kontraktor_pelaksana,
                sr.tanggal_mulai,
                sr.tanggal_target_selesai,
                sr.tanggal_selesai_aktual,
                sr.persentase_penyelesaian,
                sr.status_proyek,
                sr.sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_rekonstruksi` sr
            LEFT JOIN `{dwh_db}`.`dim_bencana` db
                ON sr.id_bencana = db.id_bencana
            ON DUPLICATE KEY UPDATE
                bencana_key = VALUES(bencana_key),
                waktu_key = VALUES(waktu_key),
                nama_proyek = VALUES(nama_proyek),
                jenis_pembangunan = VALUES(jenis_pembangunan),
                lokasi = VALUES(lokasi),
                anggaran_rupiah = VALUES(anggaran_rupiah),
                sumber_dana = VALUES(sumber_dana),
                kontraktor_pelaksana = VALUES(kontraktor_pelaksana),
                tanggal_mulai = VALUES(tanggal_mulai),
                tanggal_target_selesai = VALUES(tanggal_target_selesai),
                tanggal_selesai_aktual = VALUES(tanggal_selesai_aktual),
                persentase_penyelesaian = VALUES(persentase_penyelesaian),
                status_proyek = VALUES(status_proyek),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

        logging.info(
            "Load Ketangguhan Bencana ke Data Warehouse selesai."
        )

    # ========================================================
    # WIRING
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()
    t3 = load_to_dwh()

    t1 >> t2 >> t3

    return t3
