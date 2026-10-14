from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN PENDUDUK
# ============================================================

SOURCE_ENDPOINTS = {
    "tb_agama":              "/agama",
    "tb_alamat":             "/alamat",
    "tb_desa":               "/desa",
    "tb_kabupaten_kota":     "/kabupaten-kota",
    "tb_kartu_keluarga":     "/kartu-keluarga",
    "tb_kecamatan":          "/kecamatan",
    "tb_penduduk":           "/penduduk",
    "tb_provinsi":           "/provinsi",
    "tb_status_penduduk":    "/status-penduduk",
    "tb_status_perkawinan":  "/status-perkawinan",
}


# ============================================================
# PIPELINE PENDUDUK
# ============================================================

def create_dukcapil_tasks2025(
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

        # Daftar kolom yang memerlukan standarisasi kapitalisasi (Title Case)
        # Menangkap nama, alamat, tempat lahir, dan entitas wilayah/status lainnya
        title_case_columns = {
            "nama_lengkap",
            "nama_agama",
            "nama_provinsi",
            "nama_kabupaten_kota",
            "nama_kecamatan",
            "nama_desa",
            "jalan",
            "tempat_lahir",
            "status_perkawinan",
            "status_penduduk",
            "kewarganegaraan",
        }

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

                if table_name == "tb_penduduk" and len(records) > 1000:
                    records = records[:1000]
                    logging.info("Membatasi data penduduk menjadi 1000 records.")

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
                # Insert data dengan standarisasi teks
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
                        row = []
                        for c in columns:
                            val = rec.get(c)
                            if val is not None:
                                val_str = str(val).strip()
                                
                                # TERAPKAN TITLE CASE (Kapital di awal setiap kata)
                                if c in title_case_columns and val_str:
                                    val_str = val_str.title()
                                
                                row.append(val_str)
                            else:
                                row.append(None)
                        
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
        
        align_collation = f"""
        ALTER DATABASE `{staging_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        create_initcap = f"""
        DROP FUNCTION IF EXISTS `{staging_db}`.`INITCAP`;
        """

        create_initcap_body = f"""
        CREATE FUNCTION `{staging_db}`.`INITCAP`(input VARCHAR(255))
        RETURNS VARCHAR(255)
        DETERMINISTIC
        BEGIN
            DECLARE result VARCHAR(255) DEFAULT '';
            DECLARE word VARCHAR(255) DEFAULT '';
            DECLARE i INT DEFAULT 1;
            DECLARE len INT DEFAULT 0;
            DECLARE ch VARCHAR(1);

            IF input IS NULL THEN
                RETURN NULL;
            END IF;

            SET input = LOWER(TRIM(input));
            SET len = CHAR_LENGTH(input);

            WHILE i <= len DO
                SET ch = SUBSTRING(input, i, 1);
                IF ch = ' ' OR ch = CHAR(9) OR ch = CHAR(10) OR ch = CHAR(13) THEN
                    IF word <> '' THEN
                        SET result = CONCAT(result, UPPER(LEFT(word,1)), SUBSTRING(word,2));
                        SET word = '';
                    END IF;
                    SET result = CONCAT(result, ' ');
                ELSE
                    SET word = CONCAT(word, ch);
                END IF;
                SET i = i + 1;
            END WHILE;

            IF word <> '' THEN
                SET result = CONCAT(result, UPPER(LEFT(word,1)), SUBSTRING(word,2));
            END IF;

            RETURN TRIM(REGEXP_REPLACE(result, '[[:space:]]+', ' '));
        END;
        """

        transformations = [

            # =================================================
            # AGAMA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_agama`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_agama`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_agama) AS id_agama,
                TRIM(nama_agama) AS nama_agama,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tb_agama`

            WHERE
                id_agama IS NOT NULL
                AND TRIM(nama_agama) <> '';
            """,

            # =================================================
            # PROVINSI
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_provinsi`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_provinsi`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_provinsi)
                    AS id_provinsi,
                    
                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(TRIM(nama_provinsi), '[[:space:]]+', ' ')
                    ),
                    ''
                ) AS nama_provinsi,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_provinsi`

            WHERE
                id_provinsi IS NOT NULL
                AND TRIM(nama_provinsi) <> '';
            """,

            # =================================================
            # KABUPATEN KOTA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kabupaten_kota`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_kabupaten_kota`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_kabupaten_kota)
                    AS id_kabupaten_kota,

                TRIM(id_provinsi)
                    AS id_provinsi,
                    
                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(TRIM(nama_kabupaten_kota), '[[:space:]]+', ' ')
                    ),
                    ''
                ) AS nama_kabupaten_kota,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_kabupaten_kota`

            WHERE
                id_kabupaten_kota IS NOT NULL
                AND id_provinsi IS NOT NULL;
            """,

            # =================================================
            # KECAMATAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kecamatan`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_kecamatan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_kecamatan)
                    AS id_kecamatan,

                TRIM(id_kabupaten_kota)
                    AS id_kabupaten_kota,

                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(TRIM(nama_kecamatan), '[[:space:]]+', ' ')
                    ),
                    ''
                ) AS nama_kecamatan,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_kecamatan`

            WHERE
                id_kecamatan IS NOT NULL
                AND id_kabupaten_kota IS NOT NULL;
            """,

            # =================================================
            # DESA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_desa`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_desa`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_desa)
                    AS id_desa,

                TRIM(id_kecamatan)
                    AS id_kecamatan,

                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                TRIM(nama_desa),
                                '^[[:space:]]*(desa|kelurahan|gampong|kampung)[[:space:]]+',
                                '',
                                1,
                                0,
                                'i'
                            ),
                            '[[:space:]]+',
                            ' '
                        )
                    ),
                    ''
                ) AS nama_desa,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_desa`

            WHERE
                id_desa IS NOT NULL
                AND id_kecamatan IS NOT NULL;
            """,

            # =================================================
            # ALAMAT
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_alamat`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_alamat`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_alamat)
                    AS id_alamat,

                TRIM(id_desa)
                    AS id_desa,

                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(TRIM(jalan), '[[:space:]]+', ' ')
                    ),
                    ''
                ) AS jalan,

                NULLIF(
                    TRIM(kode_pos),
                    ''
                ) AS kode_pos,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_alamat`

            WHERE
                id_alamat IS NOT NULL
                AND id_desa IS NOT NULL;
            """,

            # =================================================
            # STATUS PERKAWINAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_status_perkawinan`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_status_perkawinan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_status_perkawinan)
                    AS id_status_perkawinan,

                TRIM(status_perkawinan)
                    AS status_perkawinan,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_status_perkawinan`

            WHERE
                id_status_perkawinan IS NOT NULL;
            """,

            # =================================================
            # STATUS PENDUDUK
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_status_penduduk`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_status_penduduk`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_status_penduduk)
                    AS id_status_penduduk,

                TRIM(status_penduduk)
                    AS status_penduduk,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_status_penduduk`

            WHERE
                id_status_penduduk IS NOT NULL;
            """,

            # =================================================
            # KARTU KELUARGA
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kartu_keluarga`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_kartu_keluarga`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_kk)
                    AS id_kk,

                REGEXP_REPLACE(
                    no_kk,
                    '[^0-9]',
                    ''
                ) AS no_kk,

                REGEXP_REPLACE(
                    nik_kepala_keluarga,
                    '[^0-9]',
                    ''
                ) AS nik_kepala_keluarga,

                tanggal_terbit,

                sumber_database,
                waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_kartu_keluarga`

            WHERE
                CHAR_LENGTH(
                    REGEXP_REPLACE(
                        no_kk,
                        '[^0-9]',
                        ''
                    )
                ) = 16

                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        nik_kepala_keluarga,
                        '[^0-9]',
                        ''
                    )
                ) = 16;
            """,

            # =================================================
            # PENDUDUK
            # Data Cleansing
            # Standardization
            # Validation
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_penduduk`;
            """,

            f"""
            CREATE TABLE
            `{staging_db}`.`stg_penduduk`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                REGEXP_REPLACE(
                    p.nik,
                    '[^0-9]',
                    ''
                ) AS nik,
                
                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(TRIM(p.nama_lengkap), '[[:space:]]+', ' ')
                    ),
                    ''
                ) AS nama_lengkap,

                NULLIF(
                    INITCAP(
                        REGEXP_REPLACE(TRIM(p.tempat_lahir), '[[:space:]]+', ' ')
                    ),
                    ''
                ) AS tempat_lahir,

                CASE
                    WHEN p.tanggal_lahir <= CURDATE()
                    THEN p.tanggal_lahir
                    ELSE NULL
                END AS tanggal_lahir,

                CASE
                    WHEN UPPER(TRIM(p.jenis_kelamin))
                        = 'L'
                    THEN 'L'

                    WHEN UPPER(TRIM(p.jenis_kelamin))
                        = 'P'
                    THEN 'P'

                    ELSE NULL
                END AS jenis_kelamin,

                TRIM(p.id_agama)
                    AS id_agama,

                TRIM(p.id_alamat)
                    AS id_alamat,

                TRIM(p.id_status_perkawinan)
                    AS id_status_perkawinan,

                CASE
                    WHEN UPPER(TRIM(p.kewarganegaraan))
                        = 'WNI'
                    THEN 'WNI'

                    WHEN UPPER(TRIM(p.kewarganegaraan))
                        = 'WNA'
                    THEN 'WNA'

                    ELSE 'TIDAK DIKETAHUI'
                END AS kewarganegaraan,

                TRIM(p.id_status_penduduk)
                    AS id_status_penduduk,

                TRIM(p.id_kk)
                    AS id_kk,

                p.sumber_database,
                p.waktu_ekstraksi

            FROM
                `{raw_db}`.`raw_tb_penduduk` p

            WHERE

                -- Validasi NIK 16 digit
                CHAR_LENGTH(
                    REGEXP_REPLACE(
                        p.nik,
                        '[^0-9]',
                        ''
                    )
                ) = 16

                -- Nama tidak boleh kosong
                AND p.nama_lengkap IS NOT NULL
                AND TRIM(p.nama_lengkap) <> ''

                -- Validasi jenis kelamin
                AND p.jenis_kelamin IN ('L', 'P');
            """,
        ]

        execute_sql(
            [f"USE `{staging_db}`;"] + [align_collation, create_initcap, create_initcap_body] + transformations
        )

        logging.info(
            "Transform staging selesai."
        )

    # ========================================================
    # TASK: LOAD -> DATA WAREHOUSE
    # ========================================================

    @task
    def load_to_dwh():

        logging.info(
            "Membuat dimension dan fact..."
        )

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        dim_tables = [
            "dim_waktu",
            "dim_agama",
            "dim_status_perkawinan",
            "dim_status_penduduk",
            "dim_kartu_keluarga",
            "dim_provinsi",
            "dim_kabupaten_kota",
            "dim_kecamatan",
            "dim_desa",
            "dim_alamat",
            "dim_penduduk",
            "fact_penduduk",
        ]

        convert_dim_tables = [align_collation]

        hook = get_mysql_hook()
        check_conn = hook.get_conn()
        check_cursor = check_conn.cursor()

        try:
            for dim_table in dim_tables:
                check_cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_name = %s
                    """,
                    (dwh_db, dim_table),
                )

                if check_cursor.fetchone()[0]:
                    convert_dim_tables.append(
                        f"""
                        ALTER TABLE `{dwh_db}`.`{dim_table}`
                        CONVERT TO CHARACTER SET utf8mb4
                        COLLATE utf8mb4_0900_ai_ci;
                        """
                    )
        finally:
            check_cursor.close()
            check_conn.close()

        execute_sql(convert_dim_tables)

        # ====================================================
        # DROP TABEL LEGACY (SKEMA LAMA)
        #
        # dim_wilayah_penduduk lama diganti hierarki snowflake:
        # dim_provinsi -> dim_kabupaten_kota -> dim_kecamatan
        # -> dim_desa -> dim_alamat
        # fact_penduduk lama memakai wilayah_key, dibuat ulang
        # dengan alamat_key.
        # ====================================================

        execute_sql([
            f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_penduduk`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_wilayah_penduduk`;",
        ])

        create_tables = [

            # =================================================
            # DIM WAKTU
            # =================================================

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

            # =================================================
            # DIM AGAMA
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_agama`
            (
                agama_key INT AUTO_INCREMENT
                    PRIMARY KEY,

                id_agama VARCHAR(10)
                    NOT NULL,

                nama_agama VARCHAR(50),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_agama
                    (id_agama)
            );
            """,

            # =================================================
            # DIM STATUS PERKAWINAN
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_status_perkawinan`
            (
                status_perkawinan_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_status_perkawinan
                    VARCHAR(10) NOT NULL,

                status_perkawinan
                    VARCHAR(50),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_status_perkawinan
                    (id_status_perkawinan)
            );
            """,

            # =================================================
            # DIM STATUS PENDUDUK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_status_penduduk`
            (
                status_penduduk_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_status_penduduk
                    VARCHAR(10) NOT NULL,

                status_penduduk
                    VARCHAR(50),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_status_penduduk
                    (id_status_penduduk)
            );
            """,

            # =================================================
            # DIM KARTU KELUARGA
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kartu_keluarga`
            (
                kartu_keluarga_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kk VARCHAR(20)
                    NOT NULL,

                no_kk VARCHAR(16),

                nik_kepala_keluarga VARCHAR(16),

                tanggal_terbit DATE,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_kk
                    (id_kk)
            );
            """,

            # =================================================
            # DIM PROVINSI
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_provinsi`
            (
                provinsi_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_provinsi
                    VARCHAR(10) NOT NULL,

                nama_provinsi
                    VARCHAR(100),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_provinsi
                    (id_provinsi)
            );
            """,

            # =================================================
            # DIM KABUPATEN KOTA
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kabupaten_kota`
            (
                kabupaten_kota_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kabupaten_kota
                    VARCHAR(10) NOT NULL,

                id_provinsi
                    VARCHAR(10),

                nama_kabupaten_kota
                    VARCHAR(100),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_kabupaten_kota
                    (id_kabupaten_kota)
            );
            """,

            # =================================================
            # DIM KECAMATAN
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kecamatan`
            (
                kecamatan_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kecamatan
                    VARCHAR(10) NOT NULL,

                id_kabupaten_kota
                    VARCHAR(10),

                nama_kecamatan
                    VARCHAR(100),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_kecamatan
                    (id_kecamatan)
            );
            """,

            # =================================================
            # DIM DESA
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_desa`
            (
                desa_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_desa
                    VARCHAR(10) NOT NULL,

                id_kecamatan
                    VARCHAR(10),

                nama_desa
                    VARCHAR(100),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_desa
                    (id_desa)
            );
            """,

            # =================================================
            # DIM ALAMAT
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_alamat`
            (
                alamat_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_alamat
                    VARCHAR(10) NOT NULL,

                id_desa
                    VARCHAR(10),

                jalan
                    TEXT,

                kode_pos
                    VARCHAR(10),

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_alamat
                    (id_alamat)
            );
            """,

            # =================================================
            # DIM PENDUDUK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_penduduk`
            (
                penduduk_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                nik VARCHAR(16)
                    NOT NULL,

                nama_lengkap VARCHAR(100),

                tempat_lahir VARCHAR(100),

                tanggal_lahir DATE,

                jenis_kelamin CHAR(1),

                kewarganegaraan VARCHAR(30),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_penduduk
                    (nik)
            );
            """,

            # =================================================
            # FACT PENDUDUK
            #
            # Grain:
            # 1 penduduk = 1 record per hari snapshot
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_penduduk`
            (
                fact_penduduk_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                penduduk_key BIGINT NOT NULL,

                alamat_key INT,

                agama_key INT,

                status_perkawinan_key INT,

                status_penduduk_key INT,

                kartu_keluarga_key INT,

                waktu_key INT NOT NULL,

                umur INT,

                jumlah_penduduk INT
                    DEFAULT 1,

                sumber_database
                    VARCHAR(100),

                waktu_load
                    DATETIME NOT NULL,

                UNIQUE KEY uk_fact_snapshot
                (
                    penduduk_key,
                    waktu_key
                ),

                KEY idx_fact_alamat
                    (alamat_key),

                KEY idx_fact_agama
                    (agama_key),

                KEY idx_fact_waktu
                    (waktu_key)
            );
            """,
        ]

        execute_sql(create_tables)

        # ====================================================
        # LOAD DIMENSION
        # ====================================================
        # ====================================================
        # SNAPSHOT DATE (TETAP)
        # ====================================================
        snapshot_date_str = "2025-12-31"
        snapshot_key = 20251231
        snapshot_day = 31
        snapshot_month = 12
        snapshot_year = 2025

        load_dimensions = [

            # -----------------------------------------------
            # DIM WAKTU
            # -----------------------------------------------

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
                {snapshot_key},

                '{snapshot_date_str}',

                {snapshot_day},

                {snapshot_month},

                CASE {snapshot_month}
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

                QUARTER('{snapshot_date_str}'),

                {snapshot_year},

                NOW()

            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM AGAMA
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_agama`
            (
                id_agama,
                nama_agama,
                sumber_database,
                waktu_load
            )

            SELECT
                id_agama,
                nama_agama,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_agama`

            ON DUPLICATE KEY UPDATE

                nama_agama =
                    VALUES(nama_agama),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM STATUS PERKAWINAN
            # -----------------------------------------------

            f"""
            INSERT INTO
            `{dwh_db}`.`dim_status_perkawinan`
            (
                id_status_perkawinan,
                status_perkawinan,
                sumber_database,
                waktu_load
            )

            SELECT
                id_status_perkawinan,
                status_perkawinan,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_status_perkawinan`

            ON DUPLICATE KEY UPDATE

                status_perkawinan =
                    VALUES(status_perkawinan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM STATUS PENDUDUK
            # -----------------------------------------------

            f"""
            INSERT INTO
            `{dwh_db}`.`dim_status_penduduk`
            (
                id_status_penduduk,
                status_penduduk,
                sumber_database,
                waktu_load
            )

            SELECT
                id_status_penduduk,
                status_penduduk,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_status_penduduk`

            ON DUPLICATE KEY UPDATE

                status_penduduk =
                    VALUES(status_penduduk),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM KK
            # -----------------------------------------------

            f"""
            INSERT INTO
            `{dwh_db}`.`dim_kartu_keluarga`
            (
                id_kk,
                no_kk,
                nik_kepala_keluarga,
                tanggal_terbit,
                sumber_database,
                waktu_load
            )

            SELECT
                id_kk,
                no_kk,
                nik_kepala_keluarga,
                tanggal_terbit,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_kartu_keluarga`

            ON DUPLICATE KEY UPDATE

                no_kk =
                    VALUES(no_kk),

                nik_kepala_keluarga =
                    VALUES(nik_kepala_keluarga),

                tanggal_terbit =
                    VALUES(tanggal_terbit),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM PROVINSI
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_provinsi`
            (
                id_provinsi,
                nama_provinsi,
                sumber_database,
                waktu_load
            )

            SELECT
                id_provinsi,
                nama_provinsi,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_provinsi`

            ON DUPLICATE KEY UPDATE

                nama_provinsi =
                    VALUES(nama_provinsi),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM KABUPATEN KOTA
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kabupaten_kota`
            (
                id_kabupaten_kota,
                id_provinsi,
                nama_kabupaten_kota,
                sumber_database,
                waktu_load
            )

            SELECT
                id_kabupaten_kota,
                id_provinsi,
                nama_kabupaten_kota,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_kabupaten_kota`

            ON DUPLICATE KEY UPDATE

                id_provinsi =
                    VALUES(id_provinsi),

                nama_kabupaten_kota =
                    VALUES(nama_kabupaten_kota),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM KECAMATAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kecamatan`
            (
                id_kecamatan,
                id_kabupaten_kota,
                nama_kecamatan,
                sumber_database,
                waktu_load
            )

            SELECT
                id_kecamatan,
                id_kabupaten_kota,
                nama_kecamatan,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_kecamatan`

            ON DUPLICATE KEY UPDATE

                id_kabupaten_kota =
                    VALUES(id_kabupaten_kota),

                nama_kecamatan =
                    VALUES(nama_kecamatan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM DESA
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_desa`
            (
                id_desa,
                id_kecamatan,
                nama_desa,
                sumber_database,
                waktu_load
            )

            SELECT
                id_desa,
                id_kecamatan,
                nama_desa,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_desa`

            ON DUPLICATE KEY UPDATE

                id_kecamatan =
                    VALUES(id_kecamatan),

                nama_desa =
                    VALUES(nama_desa),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM ALAMAT
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_alamat`
            (
                id_alamat,
                id_desa,
                jalan,
                kode_pos,
                sumber_database,
                waktu_load
            )

            SELECT
                id_alamat,
                id_desa,
                jalan,
                kode_pos,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_alamat`

            ON DUPLICATE KEY UPDATE

                id_desa =
                    VALUES(id_desa),

                jalan =
                    VALUES(jalan),

                kode_pos =
                    VALUES(kode_pos),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM PENDUDUK
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_penduduk`
            (
                nik,
                nama_lengkap,
                tempat_lahir,
                tanggal_lahir,
                jenis_kelamin,
                kewarganegaraan,
                sumber_database,
                waktu_load
            )

            SELECT
                nik,
                nama_lengkap,
                tempat_lahir,
                tanggal_lahir,
                jenis_kelamin,
                kewarganegaraan,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_penduduk`

            ON DUPLICATE KEY UPDATE

                nama_lengkap =
                    VALUES(nama_lengkap),

                tempat_lahir =
                    VALUES(tempat_lahir),

                tanggal_lahir =
                    VALUES(tanggal_lahir),

                jenis_kelamin =
                    VALUES(jenis_kelamin),

                kewarganegaraan =
                    VALUES(kewarganegaraan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FACT
        # ====================================================

        load_fact = f"""
        INSERT INTO `{dwh_db}`.`fact_penduduk`
        (
            penduduk_key,
            alamat_key,
            agama_key,
            status_perkawinan_key,
            status_penduduk_key,
            kartu_keluarga_key,
            waktu_key,
            umur,
            jumlah_penduduk,
            sumber_database,
            waktu_load
        )

        SELECT

            dp.penduduk_key,

            dal.alamat_key,

            da.agama_key,

            dsp.status_perkawinan_key,

            dstatus.status_penduduk_key,

            dkk.kartu_keluarga_key,

            CAST({snapshot_key} AS UNSIGNED) AS waktu_key,

            CASE
                WHEN sp.tanggal_lahir IS NOT NULL
                THEN
                    TIMESTAMPDIFF(
                        YEAR,
                        sp.tanggal_lahir,
                        '{snapshot_date_str}'
                    )
                ELSE NULL
            END AS umur,

            1 AS jumlah_penduduk,

            sp.sumber_database,

            NOW() AS waktu_load

        FROM
            `{staging_db}`.`stg_penduduk` sp

        INNER JOIN
            `{dwh_db}`.`dim_penduduk` dp
            ON sp.nik = dp.nik

        LEFT JOIN
            `{dwh_db}`.`dim_alamat` dal
            ON sp.id_alamat =
               dal.id_alamat

        LEFT JOIN
            `{dwh_db}`.`dim_agama` da
            ON sp.id_agama =
               da.id_agama

        LEFT JOIN
            `{dwh_db}`.`dim_status_perkawinan` dsp
            ON sp.id_status_perkawinan =
               dsp.id_status_perkawinan

        LEFT JOIN
            `{dwh_db}`.`dim_status_penduduk` dstatus
            ON sp.id_status_penduduk =
               dstatus.id_status_penduduk

        LEFT JOIN
            `{dwh_db}`.`dim_kartu_keluarga` dkk
            ON sp.id_kk =
               dkk.id_kk

        ON DUPLICATE KEY UPDATE

            alamat_key =
                VALUES(alamat_key),

            agama_key =
                VALUES(agama_key),

            status_perkawinan_key =
                VALUES(status_perkawinan_key),

            status_penduduk_key =
                VALUES(status_penduduk_key),

            kartu_keluarga_key =
                VALUES(kartu_keluarga_key),

            umur =
                VALUES(umur),

            waktu_load =
                VALUES(waktu_load);
        """

        execute_sql([load_fact])

        logging.info(
            "Load ke Data Warehouse selesai."
        )

    # ========================================================
    # WIRING
    # ========================================================

    t1 = extract_to_raw()
    t2 = transform_staging()
    t3 = load_to_dwh()

    t1 >> t2 >> t3

    return t3