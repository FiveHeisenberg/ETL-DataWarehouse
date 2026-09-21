from __future__ import annotations

import logging
import requests
import pendulum

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN DINAS SOSIAL
# ============================================================

SOURCE_ENDPOINTS = {
    "penduduk": "/extraction/penduduk",
    "penyaluran_bansos": "/extraction/penyaluran-bansos",
    "ppks": "/extraction/ppks",
    "program_bansos": "/extraction/program-bansos",
    "psks": "/extraction/psks",
    "rumah_tangga": "/extraction/rumah-tangga",
    "wilayah": "/extraction/wilayah",
}


# ============================================================
# PIPELINE DINAS SOSIAL
# ============================================================

def create_dinsos_tasks(
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

                raw_table = f"raw_dinsos_{table_name}"
                url = f"{api_base_url}{endpoint}"

                logging.info(
                    "Extract API %s -> %s.%s",
                    url,
                    raw_db,
                    raw_table,
                )

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

                columns = list(records[0].keys())

                cursor.execute(
                    f"DROP TABLE IF EXISTS "
                    f"`{raw_db}`.`{raw_table}`"
                )

                # Semua kolom API disimpan sebagai VARCHAR pada RAW.
                # Tujuannya agar data mentah dari API tidak gagal
                # hanya karena perbedaan tipe data.
                col_defs = ", ".join(
                    f"`{col}` VARCHAR(1000)"
                    for col in columns
                )

                cursor.execute(
                    f"""
                    CREATE TABLE `{raw_db}`.`{raw_table}`
                    (
                        id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        {col_defs},
                        `sumber_database` VARCHAR(255),
                        `waktu_ekstraksi` DATETIME
                    )
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_general_ci;
                    """
                )

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

                    batch = records[i:i + batch_size]

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
            "Memulai transformasi data Dinas Sosial..."
        )

        align_collation = f"""
        ALTER DATABASE `{staging_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_general_ci;
        """

        transformations = [

            # =================================================
            # WILAYAH
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_wilayah`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_wilayah`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_wilayah) AS id_wilayah,
                TRIM(nama_wilayah) AS nama_wilayah,
                TRIM(level_wilayah) AS level_wilayah,
                NULLIF(TRIM(parent_id), '') AS parent_id,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_wilayah`

            WHERE
                id_wilayah IS NOT NULL
                AND TRIM(id_wilayah) <> ''
                AND nama_wilayah IS NOT NULL
                AND TRIM(nama_wilayah) <> '';
            """,

            # =================================================
            # PROGRAM BANSOS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_program_bansos`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_program_bansos`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                CAST(TRIM(id_program) AS UNSIGNED)
                    AS id_program,

                TRIM(nama_program)
                    AS nama_program,

                NULLIF(
                    TRIM(kriteria_penerima),
                    ''
                ) AS kriteria_penerima,

                CASE
                    WHEN TRIM(anggaran_tahun) REGEXP '^[0-9]{{4}}$'
                    THEN CAST(TRIM(anggaran_tahun) AS UNSIGNED)
                    ELSE NULL
                END AS anggaran_tahun,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_program_bansos`

            WHERE
                id_program IS NOT NULL
                AND TRIM(id_program) <> ''
                AND nama_program IS NOT NULL
                AND TRIM(nama_program) <> '';
            """,

            # =================================================
            # PENDUDUK
            # Data cleansing + standardization
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_penduduk`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_penduduk`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                REGEXP_REPLACE(
                    TRIM(nik),
                    '[^0-9]',
                    ''
                ) AS nik,

                REGEXP_REPLACE(
                    TRIM(no_kk),
                    '[^0-9]',
                    ''
                ) AS no_kk,

                TRIM(nama_lengkap)
                    AS nama_lengkap,

                NULLIF(
                    TRIM(tempat_lahir),
                    ''
                ) AS tempat_lahir,

                CASE
                    WHEN TRIM(tanggal_lahir) <= CURDATE()
                    THEN DATE(tanggal_lahir)
                    ELSE NULL
                END AS tanggal_lahir,

                CASE
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'L'
                    THEN 'L'
                    WHEN UPPER(TRIM(jenis_kelamin)) = 'P'
                    THEN 'P'
                    ELSE NULL
                END AS jenis_kelamin,

                TRIM(alamat_ktp)
                    AS alamat_ktp,

                TRIM(id_wilayah)
                    AS id_wilayah,

                CASE
                    WHEN TRIM(status_kesejahteraan_desil)
                         REGEXP '^[0-9]+$'
                    THEN
                        CASE
                            WHEN CAST(
                                TRIM(status_kesejahteraan_desil)
                                AS UNSIGNED
                            ) BETWEEN 1 AND 10
                            THEN CAST(
                                TRIM(status_kesejahteraan_desil)
                                AS UNSIGNED
                            )
                            ELSE NULL
                        END
                    ELSE NULL
                END AS status_kesejahteraan_desil,

                CASE
                    WHEN created_at IS NOT NULL
                    THEN created_at
                    ELSE NULL
                END AS created_at,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_penduduk`

            WHERE

                CHAR_LENGTH(
                    REGEXP_REPLACE(
                        TRIM(nik),
                        '[^0-9]',
                        ''
                    )
                ) = 16

                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        TRIM(no_kk),
                        '[^0-9]',
                        ''
                    )
                ) = 16

                AND nama_lengkap IS NOT NULL
                AND TRIM(nama_lengkap) <> ''

                AND jenis_kelamin IN ('L', 'P');
            """,

            # =================================================
            # PENYALURAN BANSOS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_penyaluran_bansos`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_penyaluran_bansos`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(TRIM(id_penyaluran) AS UNSIGNED)
                    AS id_penyaluran,

                CAST(TRIM(id_program) AS UNSIGNED)
                    AS id_program,

                REGEXP_REPLACE(
                    TRIM(nik),
                    '[^0-9]',
                    ''
                ) AS nik,

                CASE
                    WHEN TRIM(periode_tahun) REGEXP '^[0-9]{{4}}$'
                    THEN CAST(TRIM(periode_tahun) AS UNSIGNED)
                    ELSE NULL
                END AS periode_tahun,

                TRIM(periode_tahap)
                    AS periode_tahap,

                CASE
                    WHEN TRIM(status_penyaluran)
                         IN (
                            'Pending',
                            'Disalurkan',
                            'Gagal',
                            'Valid'
                         )
                    THEN TRIM(status_penyaluran)
                    WHEN TRIM(status_penyaluran) = ''
                    THEN 'Pending'
                    ELSE 'Pending'
                END AS status_penyaluran,

                NULLIF(
                    TRIM(nominal_atau_bentuk),
                    ''
                ) AS nominal_atau_bentuk,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_penyaluran_bansos`

            WHERE
                id_penyaluran IS NOT NULL
                AND id_program IS NOT NULL
                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        TRIM(nik),
                        '[^0-9]',
                        ''
                    )
                ) = 16
                AND periode_tahun IS NOT NULL
                AND periode_tahap IS NOT NULL
                AND TRIM(periode_tahap) <> '';
            """,

            # =================================================
            # PPKS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_ppks`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_ppks`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(TRIM(id_ppks) AS UNSIGNED)
                    AS id_ppks,

                REGEXP_REPLACE(
                    TRIM(nik),
                    '[^0-9]',
                    ''
                ) AS nik,

                TRIM(kategori_ppks)
                    AS kategori_ppks,

                NULLIF(
                    TRIM(derajat_keparahan),
                    ''
                ) AS derajat_keparahan,

                CASE
                    WHEN TRIM(tanggal_terdata) <= CURDATE()
                    THEN DATE(tanggal_terdata)
                    ELSE NULL
                END AS tanggal_terdata,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_ppks`

            WHERE
                id_ppks IS NOT NULL
                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        TRIM(nik),
                        '[^0-9]',
                        ''
                    )
                ) = 16
                AND kategori_ppks IS NOT NULL
                AND TRIM(kategori_ppks) <> ''
                AND tanggal_terdata IS NOT NULL;
            """,

            # =================================================
            # PSKS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_psks`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_psks`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                CAST(TRIM(id_psks) AS UNSIGNED)
                    AS id_psks,

                TRIM(nama_sumber)
                    AS nama_sumber,

                TRIM(jenis_psks)
                    AS jenis_psks,

                TRIM(id_wilayah)
                    AS id_wilayah,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_psks`

            WHERE
                id_psks IS NOT NULL
                AND nama_sumber IS NOT NULL
                AND TRIM(nama_sumber) <> ''
                AND jenis_psks IS NOT NULL
                AND TRIM(jenis_psks) <> ''
                AND id_wilayah IS NOT NULL;
            """,

            # =================================================
            # RUMAH TANGGA
            # JSON + VALIDATION
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dinsos_rumah_tangga`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_dinsos_rumah_tangga`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_rt)
                    AS id_rt,

                REGEXP_REPLACE(
                    TRIM(no_kk),
                    '[^0-9]',
                    ''
                ) AS no_kk,

                REGEXP_REPLACE(
                    TRIM(kepala_keluarga_nik),
                    '[^0-9]',
                    ''
                ) AS kepala_keluarga_nik,

                CASE
                    WHEN JSON_VALID(kondisi_rumah)
                    THEN kondisi_rumah
                    ELSE NULL
                END AS kondisi_rumah,

                CASE
                    WHEN TRIM(score_kelayakan)
                         REGEXP '^[0-9]+(\\.[0-9]+)?$'
                    THEN CAST(
                        TRIM(score_kelayakan)
                        AS DECIMAL(5,2)
                    )
                    ELSE NULL
                END AS score_kelayakan,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dinsos_rumah_tangga`

            WHERE
                id_rt IS NOT NULL
                AND TRIM(id_rt) <> ''

                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        TRIM(no_kk),
                        '[^0-9]',
                        ''
                    )
                ) = 16

                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        TRIM(kepala_keluarga_nik),
                        '[^0-9]',
                        ''
                    )
                ) = 16;
            """,
        ]

        execute_sql(
            [align_collation] + transformations
        )

        logging.info(
            "Transform staging Dinas Sosial selesai."
        )

    # ========================================================
    # TASK: LOAD -> DATA WAREHOUSE
    # ========================================================

    @task
    def load_to_dwh():

        logging.info(
            "Membuat dimension dan fact Dinas Sosial..."
        )

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_general_ci
        ;
        """

        create_tables = [

            # =================================================
            # DIM WAKTU
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_waktu`
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

            # =================================================
            # DIM WILAYAH
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_wilayah`
            (
                wilayah_key INT AUTO_INCREMENT PRIMARY KEY,
                id_wilayah VARCHAR(10) NOT NULL,
                nama_wilayah VARCHAR(100),
                level_wilayah VARCHAR(30),
                parent_id VARCHAR(10),
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_dinsos_wilayah (id_wilayah)
            );
            """,

            # =================================================
            # DIM PENDUDUK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_penduduk`
            (
                penduduk_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                nik VARCHAR(16) NOT NULL,
                no_kk VARCHAR(16),
                nama_lengkap VARCHAR(150),
                tempat_lahir VARCHAR(100),
                tanggal_lahir DATE,
                jenis_kelamin CHAR(1),
                alamat_ktp TEXT,
                id_wilayah VARCHAR(10),
                status_kesejahteraan_desil TINYINT,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_dinsos_penduduk (nik)
            );
            """,

            # =================================================
            # DIM PROGRAM BANSOS
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_program_bansos`
            (
                program_key INT AUTO_INCREMENT PRIMARY KEY,
                id_program INT NOT NULL,
                nama_program VARCHAR(100),
                kriteria_penerima TEXT,
                anggaran_tahun YEAR,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_dinsos_program (id_program)
            );
            """,

            # =================================================
            # DIM PPKS
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_ppks`
            (
                ppks_key INT AUTO_INCREMENT PRIMARY KEY,
                id_ppks INT NOT NULL,
                nik VARCHAR(16) NOT NULL,
                kategori_ppks VARCHAR(100),
                derajat_keparahan VARCHAR(50),
                tanggal_terdata DATE,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_dinsos_ppks (id_ppks)
            );
            """,

            # =================================================
            # DIM PSKS
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_psks`
            (
                psks_key INT AUTO_INCREMENT PRIMARY KEY,
                id_psks INT NOT NULL,
                nama_sumber VARCHAR(150),
                jenis_psks VARCHAR(50),
                id_wilayah VARCHAR(10),
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_dinsos_psks (id_psks)
            );
            """,

            # =================================================
            # DIM RUMAH TANGGA
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dinsos_rumah_tangga`
            (
                rumah_tangga_key INT AUTO_INCREMENT PRIMARY KEY,
                id_rt VARCHAR(30) NOT NULL,
                no_kk VARCHAR(16),
                kepala_keluarga_nik VARCHAR(16),
                kondisi_rumah JSON,
                score_kelayakan DECIMAL(5,2),
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_dinsos_rt (id_rt)
            );
            """,

            # =================================================
            # FACT PENDUDUK
            # Grain: 1 penduduk = 1 record per snapshot
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dinsos_penduduk`
            (
                fact_penduduk_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                penduduk_key BIGINT NOT NULL,
                wilayah_key INT,
                waktu_key INT NOT NULL,
                desil_kesejahteraan TINYINT,
                umur INT,
                jumlah_penduduk INT DEFAULT 1,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_dinsos_penduduk
                (
                    penduduk_key,
                    waktu_key
                ),

                KEY idx_fact_dinsos_penduduk_wilayah
                (wilayah_key),

                KEY idx_fact_dinsos_penduduk_waktu
                (waktu_key)
            );
            """,

            # =================================================
            # FACT PENYALURAN BANSOS
            # Grain: 1 penyaluran bansos = 1 record
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dinsos_penyaluran_bansos`
            (
                fact_penyaluran_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                id_penyaluran INT NOT NULL,
                program_key INT,
                penduduk_key BIGINT,
                waktu_key INT NOT NULL,
                periode_tahun YEAR,
                periode_tahap VARCHAR(50),
                status_penyaluran VARCHAR(20),
                nominal_atau_bentuk VARCHAR(100),
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_dinsos_penyaluran
                (id_penyaluran),

                KEY idx_fact_dinsos_bansos_program
                (program_key),

                KEY idx_fact_dinsos_bansos_penduduk
                (penduduk_key),

                KEY idx_fact_dinsos_bansos_waktu
                (waktu_key)
            );
            """,

            # =================================================
            # FACT PPKS
            # Grain: 1 pendataan PPKS = 1 record
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dinsos_ppks`
            (
                fact_ppks_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                ppks_key INT NOT NULL,
                penduduk_key BIGINT,
                wilayah_key INT,
                waktu_key INT NOT NULL,
                jumlah_ppks INT DEFAULT 1,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_dinsos_ppks
                (ppks_key),

                KEY idx_fact_dinsos_ppks_wilayah
                (wilayah_key),

                KEY idx_fact_dinsos_ppks_waktu
                (waktu_key)
            );
            """,

            # =================================================
            # FACT RUMAH TANGGA
            # Grain: 1 rumah tangga = 1 record
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dinsos_rumah_tangga`
            (
                fact_rumah_tangga_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                rumah_tangga_key INT NOT NULL,
                penduduk_key BIGINT,
                waktu_key INT NOT NULL,
                score_kelayakan DECIMAL(5,2),
                jumlah_rumah_tangga INT DEFAULT 1,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_dinsos_rt
                (rumah_tangga_key),

                KEY idx_fact_dinsos_rt_waktu
                (waktu_key)
            );
            """,

            # =================================================
            # FACT PSKS
            # Grain: 1 PSKS = 1 record
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dinsos_psks`
            (
                fact_psks_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                psks_key INT NOT NULL,
                wilayah_key INT,
                waktu_key INT NOT NULL,
                jumlah_psks INT DEFAULT 1,
                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_dinsos_psks
                (psks_key),

                KEY idx_fact_dinsos_psks_wilayah
                (wilayah_key),

                KEY idx_fact_dinsos_psks_waktu
                (waktu_key)
            );
            """,
        ]

        execute_sql(
            [align_collation] + create_tables
        )

        # ====================================================
        # LOAD DIMENSIONS
        # ====================================================

        load_dimensions = [

            # DIM WAKTU
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_waktu`
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
                CAST(
                    DATE_FORMAT(CURDATE(), '%Y%m%d')
                    AS UNSIGNED
                ),
                CURDATE(),
                DAY(CURDATE()),
                MONTH(CURDATE()),
                CASE MONTH(CURDATE())
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
                QUARTER(CURDATE()),
                YEAR(CURDATE()),
                NOW()
            ON DUPLICATE KEY UPDATE
                tanggal = VALUES(tanggal),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM WILAYAH
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_wilayah`
            (
                id_wilayah,
                nama_wilayah,
                level_wilayah,
                parent_id,
                sumber_database,
                waktu_load
            )
            SELECT
                id_wilayah,
                nama_wilayah,
                level_wilayah,
                parent_id,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_dinsos_wilayah`
            ON DUPLICATE KEY UPDATE
                nama_wilayah = VALUES(nama_wilayah),
                level_wilayah = VALUES(level_wilayah),
                parent_id = VALUES(parent_id),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM PENDUDUK
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_penduduk`
            (
                nik,
                no_kk,
                nama_lengkap,
                tempat_lahir,
                tanggal_lahir,
                jenis_kelamin,
                alamat_ktp,
                id_wilayah,
                status_kesejahteraan_desil,
                sumber_database,
                waktu_load
            )
            SELECT
                nik,
                no_kk,
                nama_lengkap,
                tempat_lahir,
                tanggal_lahir,
                jenis_kelamin,
                alamat_ktp,
                id_wilayah,
                status_kesejahteraan_desil,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_dinsos_penduduk`
            ON DUPLICATE KEY UPDATE
                no_kk = VALUES(no_kk),
                nama_lengkap = VALUES(nama_lengkap),
                tempat_lahir = VALUES(tempat_lahir),
                tanggal_lahir = VALUES(tanggal_lahir),
                jenis_kelamin = VALUES(jenis_kelamin),
                alamat_ktp = VALUES(alamat_ktp),
                id_wilayah = VALUES(id_wilayah),
                status_kesejahteraan_desil =
                    VALUES(status_kesejahteraan_desil),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM PROGRAM
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_program_bansos`
            (
                id_program,
                nama_program,
                kriteria_penerima,
                anggaran_tahun,
                sumber_database,
                waktu_load
            )
            SELECT
                id_program,
                nama_program,
                kriteria_penerima,
                anggaran_tahun,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_dinsos_program_bansos`
            ON DUPLICATE KEY UPDATE
                nama_program = VALUES(nama_program),
                kriteria_penerima = VALUES(kriteria_penerima),
                anggaran_tahun = VALUES(anggaran_tahun),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM PPKS
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_ppks`
            (
                id_ppks,
                nik,
                kategori_ppks,
                derajat_keparahan,
                tanggal_terdata,
                sumber_database,
                waktu_load
            )
            SELECT
                id_ppks,
                nik,
                kategori_ppks,
                derajat_keparahan,
                tanggal_terdata,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_dinsos_ppks`
            ON DUPLICATE KEY UPDATE
                nik = VALUES(nik),
                kategori_ppks = VALUES(kategori_ppks),
                derajat_keparahan =
                    VALUES(derajat_keparahan),
                tanggal_terdata =
                    VALUES(tanggal_terdata),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM PSKS
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_psks`
            (
                id_psks,
                nama_sumber,
                jenis_psks,
                id_wilayah,
                sumber_database,
                waktu_load
            )
            SELECT
                id_psks,
                nama_sumber,
                jenis_psks,
                id_wilayah,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_dinsos_psks`
            ON DUPLICATE KEY UPDATE
                nama_sumber = VALUES(nama_sumber),
                jenis_psks = VALUES(jenis_psks),
                id_wilayah = VALUES(id_wilayah),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM RUMAH TANGGA
            f"""
            INSERT INTO `{dwh_db}`.`dim_dinsos_rumah_tangga`
            (
                id_rt,
                no_kk,
                kepala_keluarga_nik,
                kondisi_rumah,
                score_kelayakan,
                sumber_database,
                waktu_load
            )
            SELECT
                id_rt,
                no_kk,
                kepala_keluarga_nik,
                kondisi_rumah,
                score_kelayakan,
                sumber_database,
                NOW()
            FROM `{staging_db}`.`stg_dinsos_rumah_tangga`
            ON DUPLICATE KEY UPDATE
                no_kk = VALUES(no_kk),
                kepala_keluarga_nik =
                    VALUES(kepala_keluarga_nik),
                kondisi_rumah =
                    VALUES(kondisi_rumah),
                score_kelayakan =
                    VALUES(score_kelayakan),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FACT PENDUDUK
        # ====================================================

        load_fact_penduduk = f"""
        INSERT INTO `{dwh_db}`.`fact_dinsos_penduduk`
        (
            penduduk_key,
            wilayah_key,
            waktu_key,
            desil_kesejahteraan,
            umur,
            jumlah_penduduk,
            sumber_database,
            waktu_load
        )
        SELECT
            dp.penduduk_key,
            dw.wilayah_key,

            CAST(
                DATE_FORMAT(CURDATE(), '%Y%m%d')
                AS UNSIGNED
            ) AS waktu_key,

            dp.status_kesejahteraan_desil,

            TIMESTAMPDIFF(
                YEAR,
                dp.tanggal_lahir,
                CURDATE()
            ) AS umur,

            1 AS jumlah_penduduk,

            dp.sumber_database,
            NOW()

        FROM `{dwh_db}`.`dim_dinsos_penduduk` dp

        LEFT JOIN `{dwh_db}`.`dim_dinsos_wilayah` dw
            ON dp.id_wilayah = dw.id_wilayah

        ON DUPLICATE KEY UPDATE
            wilayah_key = VALUES(wilayah_key),
            desil_kesejahteraan =
                VALUES(desil_kesejahteraan),
            umur = VALUES(umur),
            jumlah_penduduk = VALUES(jumlah_penduduk),
            waktu_load = VALUES(waktu_load);
        """

        # ====================================================
        # LOAD FACT PENYALURAN BANSOS
        # ====================================================

        load_fact_bansos = f"""
        INSERT INTO `{dwh_db}`.`fact_dinsos_penyaluran_bansos`
        (
            id_penyaluran,
            program_key,
            penduduk_key,
            waktu_key,
            periode_tahun,
            periode_tahap,
            status_penyaluran,
            nominal_atau_bentuk,
            sumber_database,
            waktu_load
        )
        SELECT
            sb.id_penyaluran,
            pr.program_key,
            pd.penduduk_key,

            CAST(
                DATE_FORMAT(CURDATE(), '%Y%m%d')
                AS UNSIGNED
            ),

            sb.periode_tahun,
            sb.periode_tahap,
            sb.status_penyaluran,
            sb.nominal_atau_bentuk,
            sb.sumber_database,
            NOW()

        FROM `{staging_db}`.`stg_dinsos_penyaluran_bansos` sb

        LEFT JOIN `{dwh_db}`.`dim_dinsos_program_bansos` pr
            ON sb.id_program = pr.id_program

        LEFT JOIN `{dwh_db}`.`dim_dinsos_penduduk` pd
            ON sb.nik = pd.nik

        ON DUPLICATE KEY UPDATE
            program_key = VALUES(program_key),
            penduduk_key = VALUES(penduduk_key),
            periode_tahun = VALUES(periode_tahun),
            periode_tahap = VALUES(periode_tahap),
            status_penyaluran =
                VALUES(status_penyaluran),
            nominal_atau_bentuk =
                VALUES(nominal_atau_bentuk),
            sumber_database =
                VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """

        # ====================================================
        # LOAD FACT PPKS
        # ====================================================

        load_fact_ppks = f"""
        INSERT INTO `{dwh_db}`.`fact_dinsos_ppks`
        (
            ppks_key,
            penduduk_key,
            wilayah_key,
            waktu_key,
            jumlah_ppks,
            sumber_database,
            waktu_load
        )
        SELECT
            pp.ppks_key,
            pd.penduduk_key,
            dw.wilayah_key,

            CAST(
                DATE_FORMAT(CURDATE(), '%Y%m%d')
                AS UNSIGNED
            ),

            1,
            pp.sumber_database,
            NOW()

        FROM `{dwh_db}`.`dim_dinsos_ppks` pp

        LEFT JOIN `{dwh_db}`.`dim_dinsos_penduduk` pd
            ON pp.nik = pd.nik

        LEFT JOIN `{dwh_db}`.`dim_dinsos_wilayah` dw
            ON pd.id_wilayah = dw.id_wilayah

        ON DUPLICATE KEY UPDATE
            penduduk_key = VALUES(penduduk_key),
            wilayah_key = VALUES(wilayah_key),
            jumlah_ppks = VALUES(jumlah_ppks),
            waktu_load = VALUES(waktu_load);
        """

        # ====================================================
        # LOAD FACT RUMAH TANGGA
        # ====================================================

        load_fact_rt = f"""
        INSERT INTO `{dwh_db}`.`fact_dinsos_rumah_tangga`
        (
            rumah_tangga_key,
            penduduk_key,
            waktu_key,
            score_kelayakan,
            jumlah_rumah_tangga,
            sumber_database,
            waktu_load
        )
        SELECT
            rt.rumah_tangga_key,
            pd.penduduk_key,

            CAST(
                DATE_FORMAT(CURDATE(), '%Y%m%d')
                AS UNSIGNED
            ),

            rt.score_kelayakan,
            1,
            rt.sumber_database,
            NOW()

        FROM `{dwh_db}`.`dim_dinsos_rumah_tangga` rt

        LEFT JOIN `{dwh_db}`.`dim_dinsos_penduduk` pd
            ON rt.kepala_keluarga_nik = pd.nik

        ON DUPLICATE KEY UPDATE
            penduduk_key = VALUES(penduduk_key),
            score_kelayakan = VALUES(score_kelayakan),
            jumlah_rumah_tangga =
                VALUES(jumlah_rumah_tangga),
            waktu_load = VALUES(waktu_load);
        """

        # ====================================================
        # LOAD FACT PSKS
        # ====================================================

        load_fact_psks = f"""
        INSERT INTO `{dwh_db}`.`fact_dinsos_psks`
        (
            psks_key,
            wilayah_key,
            waktu_key,
            jumlah_psks,
            sumber_database,
            waktu_load
        )
        SELECT
            ps.psks_key,
            dw.wilayah_key,

            CAST(
                DATE_FORMAT(CURDATE(), '%Y%m%d')
                AS UNSIGNED
            ),

            1,
            ps.sumber_database,
            NOW()

        FROM `{dwh_db}`.`dim_dinsos_psks` ps

        LEFT JOIN `{dwh_db}`.`dim_dinsos_wilayah` dw
            ON ps.id_wilayah = dw.id_wilayah

        ON DUPLICATE KEY UPDATE
            wilayah_key = VALUES(wilayah_key),
            jumlah_psks = VALUES(jumlah_psks),
            waktu_load = VALUES(waktu_load);
        """

        execute_sql(
            [
                load_fact_penduduk,
                load_fact_bansos,
                load_fact_ppks,
                load_fact_rt,
                load_fact_psks,
            ]
        )

        logging.info(
            "Load Dinas Sosial ke Data Warehouse selesai."
        )

    # ========================================================
    # WIRING
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()
    t3 = load_to_dwh()

    t1 >> t2 >> t3

    return t3
