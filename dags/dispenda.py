from __future__ import annotations

import logging

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN PAJAK DAERAH
# ============================================================

SOURCE_ENDPOINTS = {
    "tb_wajib_pajak":       "/wajib-pajak",
    "tb_kategori_pajak":    "/kategori-pajak",
    "tb_objek_pajak":       "/objek-pajak",
    "tb_tagihan":           "/tagihan",
    "tb_pembayaran":        "/pembayaran",
}


# ============================================================
# PIPELINE PAJAK DAERAH (DISPENDA)
# ============================================================

def create_dispenda_tasks(
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

    @task(task_id="extract_to_raw_dispenda")
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

    @task(task_id="transform_staging_dispenda")
    def transform_staging():

        logging.info(
            "Memulai proses transform..."
        )

        align_collation = f"""
        ALTER DATABASE `{staging_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        transformations = [

            # =================================================
            # WAJIB PAJAK
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_wajib_pajak`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_wajib_pajak`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

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

                kab.id_kabupaten_kota
                    AS id_kabupaten_kota,

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

            FROM `{raw_db}`.`raw_tb_wajib_pajak` wp

            LEFT JOIN `{staging_db}`.`stg_kabupaten_kota` kab
                ON UPPER(TRIM(kab.nama_kabupaten_kota)) = 
                   UPPER(TRIM(
                       CASE
                           WHEN UPPER(TRIM(wp.kabupaten_kota)) = 'BANDA ACEH'
                           THEN 'Kota Banda Aceh'
                           
                           WHEN UPPER(TRIM(wp.kabupaten_kota)) = 'LHOKSEUMAWE'
                           THEN 'Kota Lhokseumawe'
                           
                           ELSE CONCAT('Kota ', wp.kabupaten_kota)
                       END
                   ))

            WHERE
                -- Validasi NIK 16 digit
                CHAR_LENGTH(
                    REGEXP_REPLACE(
                        wp.nik_wp,
                        '[^0-9]',
                        ''
                    )
                ) = 16

                -- Nama tidak boleh kosong
                AND wp.nama_lengkap IS NOT NULL
                AND TRIM(wp.nama_lengkap) <> ''

                -- Jenis kelamin valid
                AND UPPER(TRIM(wp.jenis_kelamin))
                    IN ('PRIA', 'L', 'LAKI-LAKI', 'WANITA', 'P', 'PEREMPUAN');
            """,

            # =================================================
            # KATEGORI PAJAK
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kategori_pajak`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_kategori_pajak`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

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

            FROM `{raw_db}`.`raw_tb_kategori_pajak`

            WHERE
                id_kategori IS NOT NULL
                AND TRIM(id_kategori) <> ''
                AND nama_pajak IS NOT NULL
                AND TRIM(nama_pajak) <> ''
                AND tarif_persentase IS NOT NULL
                AND CAST(tarif_persentase AS DECIMAL(5,2)) >= 0;
            """,

            # =================================================
            # OBJEK PAJAK
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_objek_pajak`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_objek_pajak`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

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

            FROM `{raw_db}`.`raw_tb_objek_pajak`

            WHERE
                id_objek IS NOT NULL
                AND TRIM(id_objek) <> ''
                AND id_kategori IS NOT NULL
                AND TRIM(id_kategori) <> ''

                -- Validasi NIK 16 digit
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
            """,

            # =================================================
            # TAGIHAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_tagihan`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_tagihan`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

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
                    WHEN tanggal_jatuh_tempo >= '1900-01-01'
                    THEN tanggal_jatuh_tempo
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

            FROM `{raw_db}`.`raw_tb_tagihan`

            WHERE
                id_tagihan IS NOT NULL
                AND TRIM(id_tagihan) <> ''
                AND id_objek IS NOT NULL
                AND TRIM(id_objek) <> ''
                AND tahun_pajak IS NOT NULL
                AND TRIM(tahun_pajak) <> ''
                AND nominal_tagihan IS NOT NULL
                AND CAST(nominal_tagihan AS UNSIGNED) >= 0;
            """,

            # =================================================
            # PEMBAYARAN
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pembayaran`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pembayaran`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT

                TRIM(id_pembayaran)
                    AS id_pembayaran,

                TRIM(id_tagihan)
                    AS id_tagihan,

                CASE
                    WHEN tanggal_bayar <= CURDATE()
                        AND tanggal_bayar >= '1900-01-01'
                    THEN tanggal_bayar
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

            FROM `{raw_db}`.`raw_tb_pembayaran`

            WHERE
                id_pembayaran IS NOT NULL
                AND TRIM(id_pembayaran) <> ''
                AND id_tagihan IS NOT NULL
                AND TRIM(id_tagihan) <> ''
                AND tanggal_bayar IS NOT NULL
                AND jumlah_bayar IS NOT NULL
                AND CAST(jumlah_bayar AS UNSIGNED) > 0;
            """,
        ]

        execute_sql(
            [align_collation] + transformations
        )

        logging.info(
            "Transform staging selesai."
        )

    # ========================================================
    # TASK: LOAD -> DATA WAREHOUSE
    # ========================================================

    @task(task_id="load_to_dwh_dispenda")
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
            "dim_wajib_pajak",
            "dim_kategori_pajak",
            "dim_objek_pajak",
            "dim_metode_bayar",
            "fact_tagihan",
            "fact_pembayaran",
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
        # MIGRASI KOLOM: kabupaten_kota -> id_kabupaten_kota
        # ====================================================

        migrate_columns = []

        hook_migrate = get_mysql_hook()
        conn_migrate = hook_migrate.get_conn()
        cursor_migrate = conn_migrate.cursor()

        try:
            # Cek apakah kolom lama 'kabupaten_kota' masih ada
            cursor_migrate.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = %s
                AND table_name = 'dim_wajib_pajak'
                AND column_name = 'kabupaten_kota'
                """,
                (dwh_db,),
            )

            if cursor_migrate.fetchone()[0] > 0:
                logging.info(
                    "Migrasi kolom kabupaten_kota -> id_kabupaten_kota..."
                )

                migrate_columns = [
                    # Tambah kolom baru
                    f"""
                    ALTER TABLE `{dwh_db}`.`dim_wajib_pajak`
                    ADD COLUMN id_kabupaten_kota VARCHAR(10)
                    AFTER alamat;
                    """,

                    # Drop kolom lama
                    f"""
                    ALTER TABLE `{dwh_db}`.`dim_wajib_pajak`
                    DROP COLUMN kabupaten_kota;
                    """,
                ]

        finally:
            cursor_migrate.close()
            conn_migrate.close()

        if migrate_columns:
            execute_sql(migrate_columns)

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
            # DIM WAJIB PAJAK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_wajib_pajak`
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

                UNIQUE KEY uk_wajib_pajak
                    (nik_wp)
            );
            """,

            # =================================================
            # DIM KATEGORI PAJAK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kategori_pajak`
            (
                kategori_pajak_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kategori VARCHAR(10)
                    NOT NULL,

                nama_pajak VARCHAR(100),

                tarif_persentase DECIMAL(5,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_kategori_pajak
                    (id_kategori)
            );
            """,

            # =================================================
            # DIM OBJEK PAJAK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_objek_pajak`
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

                UNIQUE KEY uk_objek_pajak
                    (id_objek)
            );
            """,

            # =================================================
            # DIM METODE BAYAR
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_metode_bayar`
            (
                metode_bayar_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                metode_bayar VARCHAR(50)
                    NOT NULL,

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_metode_bayar
                    (metode_bayar)
            );
            """,

            # =================================================
            # FACT TAGIHAN
            #
            # Grain:
            # 1 tagihan per objek pajak per tahun
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_tagihan`
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

                UNIQUE KEY uk_fact_tagihan
                    (id_tagihan),

                KEY idx_fact_tagihan_wp
                    (wajib_pajak_key),

                KEY idx_fact_tagihan_objek
                    (objek_pajak_key),

                KEY idx_fact_tagihan_waktu
                    (waktu_key)
            );
            """,

            # =================================================
            # FACT PEMBAYARAN
            #
            # Grain:
            # 1 pembayaran per transaksi
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pembayaran`
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

                UNIQUE KEY uk_fact_pembayaran
                    (id_pembayaran),

                KEY idx_fact_pembayaran_tagihan
                    (fact_tagihan_key),

                KEY idx_fact_pembayaran_waktu
                    (waktu_bayar_key)
            );
            """,
        ]

        execute_sql(create_tables)

        # ====================================================
        # LOAD DIMENSION
        # ====================================================

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

                NOW()

            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM WAJIB PAJAK
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_wajib_pajak`
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

            FROM `{staging_db}`.`stg_wajib_pajak`

            ON DUPLICATE KEY UPDATE

                nama_lengkap =
                    VALUES(nama_lengkap),

                jenis_kelamin =
                    VALUES(jenis_kelamin),

                alamat =
                    VALUES(alamat),

                id_kabupaten_kota =
                    VALUES(id_kabupaten_kota),

                npwpd =
                    VALUES(npwpd),

                tanggal_daftar =
                    VALUES(tanggal_daftar),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM KATEGORI PAJAK
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kategori_pajak`
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

            FROM `{staging_db}`.`stg_kategori_pajak`

            ON DUPLICATE KEY UPDATE

                nama_pajak =
                    VALUES(nama_pajak),

                tarif_persentase =
                    VALUES(tarif_persentase),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM OBJEK PAJAK
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_objek_pajak`
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

            FROM `{staging_db}`.`stg_objek_pajak`

            ON DUPLICATE KEY UPDATE

                nik_wp =
                    VALUES(nik_wp),

                id_kategori =
                    VALUES(id_kategori),

                nomor_identitas_aset =
                    VALUES(nomor_identitas_aset),

                rincian_objek =
                    VALUES(rincian_objek),

                nilai_aset =
                    VALUES(nilai_aset),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM METODE BAYAR
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_metode_bayar`
            (
                metode_bayar,
                waktu_load
            )

            SELECT DISTINCT
                metode_bayar,
                NOW()

            FROM `{staging_db}`.`stg_pembayaran`

            WHERE metode_bayar IS NOT NULL

            ON DUPLICATE KEY UPDATE
                waktu_load = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FACT
        # ====================================================

        load_facts = [

            # -----------------------------------------------
            # FACT TAGIHAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_tagihan`
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
                `{staging_db}`.`stg_tagihan` st

            INNER JOIN
                `{staging_db}`.`stg_objek_pajak` sop
                ON st.id_objek = sop.id_objek

            LEFT JOIN
                `{dwh_db}`.`dim_wajib_pajak` dwp
                ON sop.nik_wp = dwp.nik_wp

            LEFT JOIN
                `{dwh_db}`.`dim_objek_pajak` dop
                ON st.id_objek = dop.id_objek

            LEFT JOIN
                `{dwh_db}`.`dim_kategori_pajak` dkp
                ON sop.id_kategori = dkp.id_kategori

            ON DUPLICATE KEY UPDATE

                wajib_pajak_key =
                    VALUES(wajib_pajak_key),

                objek_pajak_key =
                    VALUES(objek_pajak_key),

                kategori_pajak_key =
                    VALUES(kategori_pajak_key),

                nominal_tagihan =
                    VALUES(nominal_tagihan),

                tanggal_jatuh_tempo =
                    VALUES(tanggal_jatuh_tempo),

                status_tagihan =
                    VALUES(status_tagihan),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # FACT PEMBAYARAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_pembayaran`
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
                `{staging_db}`.`stg_pembayaran` sp

            LEFT JOIN
                `{dwh_db}`.`fact_tagihan` ft
                ON sp.id_tagihan = ft.id_tagihan

            LEFT JOIN
                `{dwh_db}`.`dim_metode_bayar` dmb
                ON sp.metode_bayar = dmb.metode_bayar

            ON DUPLICATE KEY UPDATE

                fact_tagihan_key =
                    VALUES(fact_tagihan_key),

                metode_bayar_key =
                    VALUES(metode_bayar_key),

                waktu_bayar_key =
                    VALUES(waktu_bayar_key),

                tanggal_bayar =
                    VALUES(tanggal_bayar),

                jumlah_bayar =
                    VALUES(jumlah_bayar),

                denda_keterlambatan =
                    VALUES(denda_keterlambatan),

                total_bayar =
                    VALUES(total_bayar),

                waktu_load =
                    VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

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
