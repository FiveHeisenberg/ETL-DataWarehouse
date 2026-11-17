from __future__ import annotations

import logging
import math

import pendulum
import requests

from airflow.sdk import task

# KONFIGURASI DOMAIN PAJAK DAERAH (DISPENDA)
SOURCE_NAME = "dispenda"
SOURCE_DB = "db_dispenda"

SOURCE_ENDPOINTS = {
    "wajib_pajak": "/wajib-pajak",
    "kategori_pajak": "/kategori-pajak",
    "objek_pajak": "/objek-pajak",
    "tagihan": "/tagihan",
    "pembayaran": "/pembayaran",
    "metode_bayar": "/metode-bayar",
}

# Mapping dari endpoint ke nama tabel dengan prefix dispenda
TABLE_NAME_MAP = {
    "wajib_pajak": "raw_dispenda_wajib_pajak",
    "kategori_pajak": "raw_dispenda_kategori_pajak",
    "objek_pajak": "raw_dispenda_objek_pajak",
    "tagihan": "raw_dispenda_tagihan",
    "pembayaran": "raw_dispenda_pembayaran",
    "metode_bayar": "raw_dispenda_metode_bayar",
}

def create_dispenda_tasks(
    execute_sql,
    get_mysql_hook,
    raw_db,
    staging_db,
    dwh_db,
    api_base_url,
):

    # TASK: EXTRACT API -> RAW_DATA
    @task(task_id="extract_to_raw_dispenda")
    def extract_to_raw():

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            # Clear previous raw data
            logging.info("Truncate raw tables...")
            for table_name in SOURCE_ENDPOINTS.keys():
                raw_table = TABLE_NAME_MAP.get(
                    table_name,
                    f"raw_dispenda_{table_name}"
                )
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`{raw_table}`;")
                except:
                    pass
            conn.commit()

            for table_name, endpoint in SOURCE_ENDPOINTS.items():

                raw_table = TABLE_NAME_MAP.get(
                    table_name,
                    f"raw_dispenda_{table_name}"
                )

                url = f"{api_base_url}{endpoint}"

                logging.info(
                    "Extract API %s -> %s.%s",
                    url,
                    raw_db,
                    raw_table,
                )

                # --------------------------------------------
                # Fetch data dari API dengan pagination
                # Ambil semua records dengan limit=1000 per page
                # --------------------------------------------

                records = []
                page = 1
                max_pages = 100  # safety limit
                
                while page <= max_pages:
                    # Build URL dengan pagination
                    paginated_url = f"{url}?page={page}&limit=1000"
                    
                    logging.info(
                        "Fetching page %d: %s",
                        page,
                        paginated_url,
                    )
                    
                    try:
                        response = requests.get(paginated_url, timeout=120)
                        response.raise_for_status()
                        
                        payload = response.json()
                        
                        if isinstance(payload, list):
                            page_records = payload
                        elif isinstance(payload, dict):
                            page_records = (
                                payload.get("data")
                                or payload.get("results")
                                or [payload]
                            )
                        else:
                            page_records = []
                        
                        if not page_records:
                            logging.info(
                                "Page %d kosong, stop pagination",
                                page,
                            )
                            break
                        
                        records.extend(page_records)
                        logging.info(
                            "Page %d: %d records, total: %d",
                            page,
                            len(page_records),
                            len(records),
                        )
                        
                        page += 1
                        
                    except Exception as e:
                        logging.error(
                            "Error fetching page %d: %s",
                            page,
                            str(e),
                        )
                        break

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
                        # Skip completely empty records
                        has_data = any(
                            rec.get(c) is not None and str(rec.get(c, '')).strip() != ''
                            for c in columns
                        )
                        
                        if not has_data:
                            logging.warning(
                                "Skipping empty record in %s",
                                table_name,
                            )
                            continue
                        
                        row = [
                            (
                                str(rec[c])
                                if rec.get(c) is not None
                                else None
                            )
                            for c in columns
                        ]
                        row.append(SOURCE_DB)
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

    # TASK: TRANSFORM RAW_DATA -> STAGING_AREA
    @task(task_id="transform_staging_dispenda")
    def transform_staging():

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:

            logging.info("Memulai proses transform...")

            # ALIGN COLLATION
            cursor.execute(f"""
            ALTER DATABASE `{staging_db}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_0900_ai_ci;
            """)
            conn.commit()

            # WAJIB PAJAK
            logging.info("Transform: stg_dispenda_wajib_pajak ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dispenda_wajib_pajak`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_dispenda_wajib_pajak`
            (
                id              BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                nik_wp          VARCHAR(20),
                nama_lengkap    VARCHAR(200),
                jenis_kelamin   CHAR(1),
                alamat          VARCHAR(500),
                id_kabupaten_kota VARCHAR(10),
                npwpd           VARCHAR(30),
                tanggal_daftar  DATE,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_dispenda_wajib_pajak`
            (
                nik_wp, nama_lengkap, jenis_kelamin,
                alamat, id_kabupaten_kota, npwpd,
                tanggal_daftar, sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                REGEXP_REPLACE(
                    wp.nik_wp,
                    '[^0-9]',
                    ''
                ) AS nik_wp,

                TRIM(wp.nama_lengkap)
                    AS nama_lengkap,

                CASE
                    WHEN UPPER(TRIM(wp.jenis_kelamin))
                        IN ('PRIA', 'L', 'LAKI-LAKI')
                    THEN 'L'

                    WHEN UPPER(TRIM(wp.jenis_kelamin))
                        IN ('WANITA', 'P', 'PEREMPUAN')
                    THEN 'P'

                    ELSE NULL
                END AS jenis_kelamin,

                NULLIF(
                    TRIM(wp.alamat),
                    ''
                ) AS alamat,

                NULL AS id_kabupaten_kota,

                NULLIF(
                    TRIM(wp.npwpd),
                    ''
                ) AS npwpd,

                CASE
                    WHEN wp.tanggal_daftar <= CURDATE()
                    THEN wp.tanggal_daftar
                    ELSE NULL
                END AS tanggal_daftar,

                wp.sumber_database,
                wp.waktu_ekstraksi

            FROM `{raw_db}`.`raw_dispenda_wajib_pajak` wp

            WHERE
                wp.nik_wp IS NOT NULL
                AND TRIM(wp.nik_wp) <> ''

                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        wp.nik_wp,
                        '[^0-9]',
                        ''
                    )
                ) = 16

                AND wp.nama_lengkap IS NOT NULL
                AND TRIM(wp.nama_lengkap) <> ''

                AND wp.jenis_kelamin IS NOT NULL
                AND UPPER(TRIM(wp.jenis_kelamin))
                    IN ('PRIA', 'L', 'LAKI-LAKI', 'WANITA', 'P', 'PEREMPUAN');
            """)
            conn.commit()

            logging.info("Transform: stg_dispenda_wajib_pajak selesai.")

            # KATEGORI PAJAK
            logging.info("Transform: stg_dispenda_kategori_pajak ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dispenda_kategori_pajak`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_dispenda_kategori_pajak`
            (
                id                BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_kategori       VARCHAR(10),
                nama_pajak        VARCHAR(100),
                tarif_persentase  DECIMAL(5,2),
                sumber_database   VARCHAR(100),
                waktu_ekstraksi   DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_dispenda_kategori_pajak`
            (
                id_kategori, nama_pajak, tarif_persentase,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(id_kategori)
                    AS id_kategori,

                TRIM(nama_pajak)
                    AS nama_pajak,

                CAST(
                    tarif_persentase
                    AS DECIMAL(5,2)
                ) AS tarif_persentase,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dispenda_kategori_pajak`

            WHERE
                id_kategori IS NOT NULL
                AND TRIM(id_kategori) <> ''
                AND nama_pajak IS NOT NULL
                AND TRIM(nama_pajak) <> ''
                AND tarif_persentase IS NOT NULL
                AND CAST(tarif_persentase AS DECIMAL(5,2)) >= 0;
            """)
            conn.commit()

            logging.info("Transform: stg_dispenda_kategori_pajak selesai.")

            # OBJEK PAJAK
            logging.info("Transform: stg_dispenda_objek_pajak ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dispenda_objek_pajak`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_dispenda_objek_pajak`
            (
                id                    BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_objek              VARCHAR(20),
                nik_wp                VARCHAR(20),
                id_kategori           VARCHAR(10),
                nomor_identitas_aset  VARCHAR(50),
                rincian_objek         VARCHAR(200),
                nilai_aset            BIGINT UNSIGNED,
                sumber_database       VARCHAR(100),
                waktu_ekstraksi       DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_dispenda_objek_pajak`
            (
                id_objek, nik_wp, id_kategori,
                nomor_identitas_aset, rincian_objek, nilai_aset,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(id_objek)
                    AS id_objek,

                REGEXP_REPLACE(
                    nik_wp,
                    '[^0-9]',
                    ''
                ) AS nik_wp,

                TRIM(id_kategori)
                    AS id_kategori,

                NULLIF(
                    TRIM(nomor_identitas_aset),
                    ''
                ) AS nomor_identitas_aset,

                TRIM(rincian_objek)
                    AS rincian_objek,

                CAST(
                    nilai_aset
                    AS UNSIGNED
                ) AS nilai_aset,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dispenda_objek_pajak`

            WHERE
                id_objek IS NOT NULL
                AND TRIM(id_objek) <> ''
                AND id_kategori IS NOT NULL
                AND TRIM(id_kategori) <> ''

                AND CHAR_LENGTH(
                    REGEXP_REPLACE(
                        nik_wp,
                        '[^0-9]',
                        ''
                    )
                ) = 16

                AND rincian_objek IS NOT NULL
                AND TRIM(rincian_objek) <> ''

                AND nilai_aset IS NOT NULL
                AND CAST(nilai_aset AS UNSIGNED) > 0;
            """)
            conn.commit()

            logging.info("Transform: stg_dispenda_objek_pajak selesai.")

            # TAGIHAN
            logging.info("Transform: stg_dispenda_tagihan ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dispenda_tagihan`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_dispenda_tagihan`
            (
                id                  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_tagihan          VARCHAR(20),
                id_objek            VARCHAR(20),
                tahun_pajak         VARCHAR(4),
                nominal_tagihan     BIGINT UNSIGNED,
                tanggal_jatuh_tempo DATE,
                status_tagihan      VARCHAR(20),
                sumber_database     VARCHAR(100),
                waktu_ekstraksi     DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_dispenda_tagihan`
            (
                id_tagihan, id_objek, tahun_pajak,
                nominal_tagihan, tanggal_jatuh_tempo, status_tagihan,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(id_tagihan)
                    AS id_tagihan,

                TRIM(id_objek)
                    AS id_objek,

                TRIM(tahun_pajak)
                    AS tahun_pajak,

                CAST(
                    nominal_tagihan
                    AS UNSIGNED
                ) AS nominal_tagihan,

                CASE
                    WHEN STR_TO_DATE(tanggal_jatuh_tempo, '%Y-%m-%d') IS NOT NULL
                        AND STR_TO_DATE(tanggal_jatuh_tempo, '%Y-%m-%d') >= '1900-01-01'
                    THEN STR_TO_DATE(tanggal_jatuh_tempo, '%Y-%m-%d')
                    ELSE NULL
                END AS tanggal_jatuh_tempo,

                CASE
                    WHEN UPPER(TRIM(status_tagihan))
                        IN ('LUNAS')
                    THEN 'LUNAS'

                    WHEN UPPER(TRIM(status_tagihan))
                        IN ('BELUM LUNAS', 'BELUM')
                    THEN 'BELUM LUNAS'

                    ELSE 'BELUM LUNAS'
                END AS status_tagihan,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dispenda_tagihan`

            WHERE
                id_tagihan IS NOT NULL
                AND TRIM(id_tagihan) <> ''
                AND id_objek IS NOT NULL
                AND TRIM(id_objek) <> ''
                AND tahun_pajak IS NOT NULL
                AND TRIM(tahun_pajak) <> ''
                AND nominal_tagihan IS NOT NULL
                AND CAST(nominal_tagihan AS UNSIGNED) >= 0
                AND tanggal_jatuh_tempo IS NOT NULL
                AND tanggal_jatuh_tempo <> '0000-00-00';
            """)
            conn.commit()

            logging.info("Transform: stg_dispenda_tagihan selesai.")

            # PEMBAYARAN
            logging.info("Transform: stg_dispenda_pembayaran ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_dispenda_pembayaran`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_dispenda_pembayaran`
            (
                id                      BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_pembayaran           VARCHAR(20),
                id_tagihan              VARCHAR(20),
                tanggal_bayar           DATE,
                jumlah_bayar            BIGINT UNSIGNED,
                denda_keterlambatan     BIGINT UNSIGNED,
                metode_bayar            VARCHAR(50),
                sumber_database         VARCHAR(100),
                waktu_ekstraksi         DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_dispenda_pembayaran`
            (
                id_pembayaran, id_tagihan, tanggal_bayar,
                jumlah_bayar, denda_keterlambatan, metode_bayar,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(id_pembayaran)
                    AS id_pembayaran,

                TRIM(id_tagihan)
                    AS id_tagihan,

                CASE
                    WHEN STR_TO_DATE(tanggal_bayar, '%Y-%m-%d') IS NOT NULL
                        AND STR_TO_DATE(tanggal_bayar, '%Y-%m-%d') <= CURDATE()
                        AND STR_TO_DATE(tanggal_bayar, '%Y-%m-%d') >= '1900-01-01'
                    THEN STR_TO_DATE(tanggal_bayar, '%Y-%m-%d')
                    ELSE NULL
                END AS tanggal_bayar,

                CAST(
                    jumlah_bayar
                    AS UNSIGNED
                ) AS jumlah_bayar,

                CAST(
                    COALESCE(denda_keterlambatan, 0)
                    AS UNSIGNED
                ) AS denda_keterlambatan,

                NULLIF(
                    TRIM(metode_bayar),
                    ''
                ) AS metode_bayar,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_dispenda_pembayaran`

            WHERE
                id_pembayaran IS NOT NULL
                AND TRIM(id_pembayaran) <> ''
                AND id_tagihan IS NOT NULL
                AND TRIM(id_tagihan) <> ''
                AND tanggal_bayar IS NOT NULL
                AND tanggal_bayar <> '0000-00-00'
                AND jumlah_bayar IS NOT NULL
                AND CAST(jumlah_bayar AS UNSIGNED) > 0;
            """)
            conn.commit()

            # =================================================
            # METODE BAYAR (Simplified - skip complex transform)
            # =================================================

            logging.info("Transform: stg_dispenda_metode_bayar ... (using raw data)")
            
            # Metode bayar staging table dibuat kosong
            # Data akan di-load langsung dari raw table di load task
            cursor.execute(f"""
            DROP TABLE IF EXISTS `{staging_db}`.`stg_dispenda_metode_bayar`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_dispenda_metode_bayar`
            (
                id                  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                metode_bayar        VARCHAR(255),
                sumber_database     VARCHAR(100),
                waktu_ekstraksi     DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)
            
            conn.commit()

            logging.info("Transform: stg_dispenda_metode_bayar selesai.")

            logging.info("Transform staging selesai.")

        except Exception as e:
            conn.rollback()
            logging.error(
                "ERROR transform_staging_dispenda: %s | Query: %s",
                str(e),
                cursor._last_executed if hasattr(cursor, "_last_executed") else "N/A",
            )
            raise

        finally:
            cursor.close()
            conn.close()

    # TASK: LOAD -> DATA WAREHOUSE
    @task(task_id="load_to_dwh_dispenda")
    def load_to_dwh():

        logging.info("Membuat dimension dan fact...")

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        dim_tables = [
            "dim_dispenda_waktu",
            "dim_dispenda_wajib_pajak",
            "dim_dispenda_kategori_pajak",
            "dim_dispenda_objek_pajak",
            "dim_dispenda_metode_bayar",
            "fact_dispenda_tagihan",
            "fact_dispenda_pembayaran",
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

        create_tables = [

            # DIM WAKTU
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dispenda_waktu`
            (
                waktu_key INT PRIMARY KEY,

                tanggal DATE NOT NULL,

                hari INT,
                bulan INT,
                nama_bulan VARCHAR(20),
                kuartal INT,
                tahun INT,

                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL
            );
            """,

            # DIM WAJIB PAJAK
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dispenda_wajib_pajak`
            (
                wajib_pajak_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                nik_wp VARCHAR(16)
                    NOT NULL,

                nama_lengkap VARCHAR(100),

                jenis_kelamin VARCHAR(10),

                alamat VARCHAR(255),

                id_kabupaten_kota VARCHAR(10),

                npwpd VARCHAR(25),

                tanggal_daftar DATE,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_dispenda_wajib_pajak
                    (nik_wp)
            );
            """,

            # DIM KATEGORI PAJAK
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dispenda_kategori_pajak`
            (
                kategori_pajak_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kategori VARCHAR(10)
                    NOT NULL,

                nama_pajak VARCHAR(100),

                tarif_persentase DECIMAL(5,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_dispenda_kategori_pajak
                    (id_kategori)
            );
            """,

            # DIM OBJEK PAJAK
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dispenda_objek_pajak`
            (
                objek_pajak_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                id_objek VARCHAR(20)
                    NOT NULL,

                nik_wp VARCHAR(16),

                id_kategori VARCHAR(10),

                nomor_identitas_aset VARCHAR(50),

                rincian_objek VARCHAR(100),

                nilai_aset BIGINT,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_dispenda_objek_pajak
                    (id_objek)
            );
            """,

            # DIM METODE BAYAR
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dispenda_metode_bayar`
            (
                metode_bayar_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                metode_bayar VARCHAR(50)
                    NOT NULL,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_dispenda_metode_bayar
                    (metode_bayar)
            );
            """,

            # FACT TAGIHAN
            # Grain: 1 tagihan per objek pajak per tahun
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dispenda_tagihan`
            (
                fact_tagihan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                wajib_pajak_key BIGINT,

                objek_pajak_key BIGINT,

                kategori_pajak_key INT,

                waktu_key INT,

                id_tagihan VARCHAR(20)
                    NOT NULL,

                tahun_pajak VARCHAR(4),

                nominal_tagihan BIGINT,

                tanggal_jatuh_tempo DATE,

                status_tagihan VARCHAR(20),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_dispenda_fact_tagihan
                    (id_tagihan),

                KEY idx_dispenda_fact_tagihan_wp
                    (wajib_pajak_key),

                KEY idx_dispenda_fact_tagihan_objek
                    (objek_pajak_key),

                KEY idx_dispenda_fact_tagihan_waktu
                    (waktu_key)
            );
            """,

            # FACT PEMBAYARAN
            # Grain: 1 pembayaran per transaksi
            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_dispenda_pembayaran`
            (
                fact_pembayaran_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                fact_tagihan_key BIGINT,

                metode_bayar_key INT,

                waktu_bayar_key INT,

                id_pembayaran VARCHAR(20)
                    NOT NULL,

                id_tagihan VARCHAR(20),

                tanggal_bayar DATE,

                jumlah_bayar BIGINT,

                denda_keterlambatan BIGINT,

                total_bayar BIGINT,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_dispenda_fact_pembayaran
                    (id_pembayaran),

                KEY idx_dispenda_fact_pembayaran_tagihan
                    (fact_tagihan_key),

                KEY idx_dispenda_fact_pembayaran_waktu
                    (waktu_bayar_key)
            );
            """,
        ]

        execute_sql(create_tables)

        # TRUNCATE DIMENSIONS
        truncate_dims = [
            f"TRUNCATE TABLE `{dwh_db}`.`dim_dispenda_waktu`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_dispenda_wajib_pajak`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_dispenda_kategori_pajak`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_dispenda_objek_pajak`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_dispenda_metode_bayar`;",
        ]

        execute_sql(truncate_dims)

        logging.info("Truncate dimensions selesai")

        # LOAD DIMENSION
        load_dimensions = [

            # DIM WAKTU
            f"""
            INSERT INTO `{dwh_db}`.`dim_dispenda_waktu`
            (
                waktu_key,
                tanggal,
                hari,
                bulan,
                nama_bulan,
                kuartal,
                tahun,
                sumber_database,
                waktu_load
            )

            SELECT
                CAST(
                    DATE_FORMAT(
                        CURDATE(),
                        '%Y%m%d'
                    ) AS UNSIGNED
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

                '{SOURCE_DB}',

                NOW()

            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # DIM WAJIB PAJAK
            f"""
            INSERT INTO `{dwh_db}`.`dim_dispenda_wajib_pajak`
            (
                nik_wp,
                nama_lengkap,
                jenis_kelamin,
                alamat,
                id_kabupaten_kota,
                npwpd,
                tanggal_daftar,
                sumber_database,
                waktu_load
            )

            SELECT
                nik_wp,
                nama_lengkap,
                jenis_kelamin,
                alamat,
                id_kabupaten_kota,
                npwpd,
                tanggal_daftar,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_dispenda_wajib_pajak`

            ON DUPLICATE KEY UPDATE

                nama_lengkap = VALUES(nama_lengkap),
                jenis_kelamin = VALUES(jenis_kelamin),
                alamat = VALUES(alamat),
                id_kabupaten_kota = VALUES(id_kabupaten_kota),
                npwpd = VALUES(npwpd),
                tanggal_daftar = VALUES(tanggal_daftar),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM KATEGORI PAJAK
            f"""
            INSERT INTO `{dwh_db}`.`dim_dispenda_kategori_pajak`
            (
                id_kategori,
                nama_pajak,
                tarif_persentase,
                sumber_database,
                waktu_load
            )

            SELECT
                id_kategori,
                nama_pajak,
                tarif_persentase,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_dispenda_kategori_pajak`

            ON DUPLICATE KEY UPDATE

                nama_pajak = VALUES(nama_pajak),
                tarif_persentase = VALUES(tarif_persentase),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM OBJEK PAJAK
            f"""
            INSERT INTO `{dwh_db}`.`dim_dispenda_objek_pajak`
            (
                id_objek,
                nik_wp,
                id_kategori,
                nomor_identitas_aset,
                rincian_objek,
                nilai_aset,
                sumber_database,
                waktu_load
            )

            SELECT
                id_objek,
                nik_wp,
                id_kategori,
                nomor_identitas_aset,
                rincian_objek,
                nilai_aset,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_dispenda_objek_pajak`

            ON DUPLICATE KEY UPDATE

                nik_wp = VALUES(nik_wp),
                id_kategori = VALUES(id_kategori),
                nomor_identitas_aset = VALUES(nomor_identitas_aset),
                rincian_objek = VALUES(rincian_objek),
                nilai_aset = VALUES(nilai_aset),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
            """,

            # DIM METODE BAYAR
            f"""
            INSERT INTO `{dwh_db}`.`dim_dispenda_metode_bayar`
            (
                metode_bayar,
                sumber_database,
                waktu_load
            )

            SELECT DISTINCT
                metode_bayar,
                '{SOURCE_DB}',
                NOW()

            FROM `{staging_db}`.`stg_dispenda_pembayaran`

            WHERE metode_bayar IS NOT NULL

            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # LOAD FACT
        load_facts = [

            # FACT TAGIHAN
            f"""
            INSERT INTO `{dwh_db}`.`fact_dispenda_tagihan`
            (
                wajib_pajak_key,
                objek_pajak_key,
                kategori_pajak_key,
                waktu_key,
                id_tagihan,
                tahun_pajak,
                nominal_tagihan,
                tanggal_jatuh_tempo,
                status_tagihan,
                sumber_database,
                waktu_load
            )

            SELECT

                dwp.wajib_pajak_key,

                dop.objek_pajak_key,

                dkp.kategori_pajak_key,

                CAST(
                    DATE_FORMAT(
                        CURDATE(),
                        '%Y%m%d'
                    ) AS UNSIGNED
                ) AS waktu_key,

                st.id_tagihan,

                st.tahun_pajak,

                st.nominal_tagihan,

                st.tanggal_jatuh_tempo,

                st.status_tagihan,

                st.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_dispenda_tagihan` st

            INNER JOIN
                `{staging_db}`.`stg_dispenda_objek_pajak` sop
                ON st.id_objek = sop.id_objek

            LEFT JOIN
                `{dwh_db}`.`dim_dispenda_wajib_pajak` dwp
                ON sop.nik_wp = dwp.nik_wp

            LEFT JOIN
                `{dwh_db}`.`dim_dispenda_objek_pajak` dop
                ON st.id_objek = dop.id_objek

            LEFT JOIN
                `{dwh_db}`.`dim_dispenda_kategori_pajak` dkp
                ON sop.id_kategori = dkp.id_kategori

            ON DUPLICATE KEY UPDATE

                wajib_pajak_key = VALUES(wajib_pajak_key),
                objek_pajak_key = VALUES(objek_pajak_key),
                kategori_pajak_key = VALUES(kategori_pajak_key),
                nominal_tagihan = VALUES(nominal_tagihan),
                tanggal_jatuh_tempo = VALUES(tanggal_jatuh_tempo),
                status_tagihan = VALUES(status_tagihan),
                waktu_load = VALUES(waktu_load);
            """,

            # FACT PEMBAYARAN
            f"""
            INSERT INTO `{dwh_db}`.`fact_dispenda_pembayaran`
            (
                fact_tagihan_key,
                metode_bayar_key,
                waktu_bayar_key,
                id_pembayaran,
                id_tagihan,
                tanggal_bayar,
                jumlah_bayar,
                denda_keterlambatan,
                total_bayar,
                sumber_database,
                waktu_load
            )

            SELECT

                ft.fact_tagihan_key,

                dmb.metode_bayar_key,

                CAST(
                    DATE_FORMAT(
                        sp.tanggal_bayar,
                        '%Y%m%d'
                    ) AS UNSIGNED
                ) AS waktu_bayar_key,

                sp.id_pembayaran,

                sp.id_tagihan,

                sp.tanggal_bayar,

                sp.jumlah_bayar,

                sp.denda_keterlambatan,

                (sp.jumlah_bayar + sp.denda_keterlambatan)
                    AS total_bayar,

                sp.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_dispenda_pembayaran` sp

            LEFT JOIN
                `{dwh_db}`.`fact_dispenda_tagihan` ft
                ON sp.id_tagihan = ft.id_tagihan

            LEFT JOIN
                `{dwh_db}`.`dim_dispenda_metode_bayar` dmb
                ON sp.metode_bayar = dmb.metode_bayar

            ON DUPLICATE KEY UPDATE

                fact_tagihan_key = VALUES(fact_tagihan_key),
                metode_bayar_key = VALUES(metode_bayar_key),
                waktu_bayar_key = VALUES(waktu_bayar_key),
                tanggal_bayar = VALUES(tanggal_bayar),
                jumlah_bayar = VALUES(jumlah_bayar),
                denda_keterlambatan = VALUES(denda_keterlambatan),
                total_bayar = VALUES(total_bayar),
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

        logging.info("Load ke Data Warehouse selesai.")

    # WIRING
    t_extract = extract_to_raw()
    t_transform = transform_staging()
    t_load = load_to_dwh()

    return {
        "extract_to_raw": t_extract,
        "transform_staging": t_transform,
        "load_to_dwh": t_load,
    }
