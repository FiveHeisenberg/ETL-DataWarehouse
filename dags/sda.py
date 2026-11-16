from __future__ import annotations

import logging
import math

import pendulum
import requests

from airflow.sdk import task


SOURCE_NAME = "sda"
SOURCE_DB = "db_sda_lingkungan"

SOURCE_ENDPOINTS = {
    "wilayah":              "/wilayah",
    "fasilitas_sampah":     "/fasilitas-sampah",
    "perusahaan":           "/perusahaan",
    "stasiun_pantau":       "/stasiun-pantau",
    "izin_lingkungan":      "/izin-lingkungan",
    "kualitas_air_sungai":  "/kualitas-air-sungai",
    "kualitas_udara":       "/kualitas-udara",
    "timbulan_sampah":      "/timbulan-sampah",
    "tutupan_lahan_rth":    "/tutupan-lahan-rth",
}

TABLE_NAME_MAP = {
    "wilayah":              "raw_sda_wilayah",
    "fasilitas_sampah":     "raw_sda_fasilitas_sampah",
    "perusahaan":           "raw_sda_perusahaan",
    "stasiun_pantau":       "raw_sda_stasiun_pantau",
    "izin_lingkungan":      "raw_sda_izin_lingkungan",
    "kualitas_air_sungai":  "raw_sda_kualitas_air_sungai",
    "kualitas_udara":       "raw_sda_kualitas_udara",
    "timbulan_sampah":      "raw_sda_timbulan_sampah",
    "tutupan_lahan_rth":    "raw_sda_tutupan_lahan_rth",
}


def create_sda_tasks(
    execute_sql,
    get_mysql_hook,
    raw_db,
    staging_db,
    dwh_db,
    api_base_url,
):

    @task(task_id="extract_to_raw_sda")
    def extract_to_raw():

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            logging.info("Truncate raw tables...")
            for table_name in SOURCE_ENDPOINTS.keys():
                raw_table = TABLE_NAME_MAP.get(
                    table_name,
                    f"raw_sda_{table_name}"
                )
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`{raw_table}`;")
                except:
                    pass
            conn.commit()

            for table_name, endpoint in SOURCE_ENDPOINTS.items():

                raw_table = TABLE_NAME_MAP.get(
                    table_name,
                    f"raw_sda_{table_name}"
                )

                url = f"{api_base_url}{endpoint}"

                logging.info(
                    "Extract API %s -> %s.%s",
                    url,
                    raw_db,
                    raw_table,
                )

                records = []
                page = 1
                max_pages = 100

                while page <= max_pages:
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

    @task(task_id="transform_staging_sda")
    def transform_staging():

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:

            logging.info(
                "Memulai proses transform..."
            )

            cursor.execute(f"""
            ALTER DATABASE `{staging_db}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_0900_ai_ci;
            """)
            conn.commit()

            logging.info("Transform: stg_sda_wilayah ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_wilayah`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_wilayah`
            (
                id                  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_desa             VARCHAR(10),
                nama_desa           VARCHAR(100),
                id_kecamatan        VARCHAR(10),
                nama_kecamatan      VARCHAR(100),
                id_kabupaten_kota   VARCHAR(10),
                nama_kabupaten_kota VARCHAR(100),
                nama_provinsi       VARCHAR(100),
                sumber_database     VARCHAR(100),
                waktu_ekstraksi     DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_wilayah`
            (
                id_desa, nama_desa, id_kecamatan, nama_kecamatan,
                id_kabupaten_kota, nama_kabupaten_kota, nama_provinsi,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(w.id_desa)
                    AS id_desa,

                TRIM(w.nama_desa)
                    AS nama_desa,

                NULLIF(
                    TRIM(w.id_kecamatan),
                    ''
                ) AS id_kecamatan,

                NULLIF(
                    TRIM(w.nama_kecamatan),
                    ''
                ) AS nama_kecamatan,

                NULLIF(
                    TRIM(w.id_kabupaten_kota),
                    ''
                ) AS id_kabupaten_kota,

                NULLIF(
                    TRIM(w.nama_kabupaten_kota),
                    ''
                ) AS nama_kabupaten_kota,

                NULLIF(
                    TRIM(w.nama_provinsi),
                    ''
                ) AS nama_provinsi,

                w.sumber_database,
                w.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_wilayah` w

            WHERE
                w.id_desa IS NOT NULL
                AND TRIM(w.id_desa) <> ''

                AND w.nama_desa IS NOT NULL
                AND TRIM(w.nama_desa) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_wilayah selesai."
            )

            logging.info("Transform: stg_sda_fasilitas_sampah ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_fasilitas_sampah`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_fasilitas_sampah`
            (
                id                      BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_fasilitas            VARCHAR(20),
                nama_fasilitas          VARCHAR(255),
                jenis_fasilitas         VARCHAR(50),
                id_desa                 VARCHAR(10),
                nama_desa               VARCHAR(100),
                kapasitas_maksimal_ton  DECIMAL(10,2),
                status_operasional      VARCHAR(20),
                sumber_database         VARCHAR(100),
                waktu_ekstraksi         DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_fasilitas_sampah`
            (
                id_fasilitas, nama_fasilitas, jenis_fasilitas,
                id_desa, nama_desa, kapasitas_maksimal_ton, status_operasional,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(fs.id_fasilitas)
                    AS id_fasilitas,

                TRIM(fs.nama_fasilitas)
                    AS nama_fasilitas,

                CASE
                    WHEN UPPER(TRIM(fs.jenis_fasilitas))
                        IN ('TPA')
                    THEN 'TPA'

                    WHEN UPPER(TRIM(fs.jenis_fasilitas))
                        IN ('TPS 3R', 'TPS3R', 'TPS-3R')
                    THEN 'TPS 3R'

                    WHEN UPPER(TRIM(fs.jenis_fasilitas))
                        IN ('BANK SAMPAH', 'BANKSAMPAH')
                    THEN 'Bank Sampah'

                    WHEN fs.jenis_fasilitas IS NULL
                        OR TRIM(fs.jenis_fasilitas) = ''
                    THEN 'TIDAK DIKETAHUI'

                    ELSE TRIM(fs.jenis_fasilitas)
                END AS jenis_fasilitas,

                NULLIF(
                    TRIM(fs.id_desa),
                    ''
                ) AS id_desa,

                NULLIF(
                    TRIM(fs.nama_desa),
                    ''
                ) AS nama_desa,

                CASE
                    WHEN CAST(fs.kapasitas_maksimal_ton AS DECIMAL(10,2)) < 0
                    THEN NULL
                    ELSE CAST(fs.kapasitas_maksimal_ton AS DECIMAL(10,2))
                END AS kapasitas_maksimal_ton,

                CASE
                    WHEN UPPER(TRIM(fs.status_operasional))
                        IN ('AKTIF', '1', 'YES')
                    THEN 'Aktif'

                    WHEN UPPER(TRIM(fs.status_operasional))
                        IN ('NON-AKTIF', 'NON AKTIF', 'NONAKTIF', '0', 'NO')
                    THEN 'Non-Aktif'

                    WHEN fs.status_operasional IS NULL
                        OR TRIM(fs.status_operasional) = ''
                    THEN 'TIDAK DIKETAHUI'

                    ELSE 'TIDAK DIKETAHUI'
                END AS status_operasional,

                fs.sumber_database,
                fs.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_fasilitas_sampah` fs

            WHERE
                fs.id_fasilitas IS NOT NULL
                AND TRIM(fs.id_fasilitas) <> ''

                AND fs.nama_fasilitas IS NOT NULL
                AND TRIM(fs.nama_fasilitas) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_fasilitas_sampah selesai."
            )

            logging.info("Transform: stg_sda_perusahaan ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_perusahaan`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_perusahaan`
            (
                id                  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_perusahaan       VARCHAR(20),
                nama_perusahaan     VARCHAR(255),
                bidang_usaha        VARCHAR(100),
                alamat_lengkap      VARCHAR(300),
                id_desa             VARCHAR(10),
                nama_desa           VARCHAR(100),
                kontak_perusahaan   VARCHAR(50),
                sumber_database     VARCHAR(100),
                waktu_ekstraksi     DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_perusahaan`
            (
                id_perusahaan, nama_perusahaan, bidang_usaha,
                alamat_lengkap, id_desa, nama_desa, kontak_perusahaan,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(p.id_perusahaan)
                    AS id_perusahaan,

                TRIM(p.nama_perusahaan)
                    AS nama_perusahaan,

                CASE
                    WHEN p.bidang_usaha IS NULL
                        OR TRIM(p.bidang_usaha) = ''
                    THEN 'TIDAK DIKETAHUI'
                    ELSE TRIM(p.bidang_usaha)
                END AS bidang_usaha,

                NULLIF(
                    TRIM(p.alamat_lengkap),
                    ''
                ) AS alamat_lengkap,

                NULLIF(
                    TRIM(p.id_desa),
                    ''
                ) AS id_desa,

                NULLIF(
                    TRIM(p.nama_desa),
                    ''
                ) AS nama_desa,

                NULLIF(
                    TRIM(p.kontak_perusahaan),
                    ''
                ) AS kontak_perusahaan,

                p.sumber_database,
                p.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_perusahaan` p

            WHERE
                p.id_perusahaan IS NOT NULL
                AND TRIM(p.id_perusahaan) <> ''

                AND p.nama_perusahaan IS NOT NULL
                AND TRIM(p.nama_perusahaan) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_perusahaan selesai."
            )

            logging.info("Transform: stg_sda_stasiun_pantau ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_stasiun_pantau`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_stasiun_pantau`
            (
                id                  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_stasiun          VARCHAR(20),
                nama_stasiun        VARCHAR(255),
                jenis_stasiun       VARCHAR(50),
                id_desa             VARCHAR(10),
                nama_desa           VARCHAR(100),
                koordinat_gps       VARCHAR(100),
                status_aktif        VARCHAR(20),
                sumber_database     VARCHAR(100),
                waktu_ekstraksi     DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_stasiun_pantau`
            (
                id_stasiun, nama_stasiun, jenis_stasiun,
                id_desa, nama_desa, koordinat_gps, status_aktif,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(sp.id_stasiun)
                    AS id_stasiun,

                TRIM(sp.nama_stasiun)
                    AS nama_stasiun,

                CASE
                    WHEN UPPER(TRIM(sp.jenis_stasiun))
                        IN ('AIR SUNGAI', 'AIRSUNGAI', 'AIR')
                    THEN 'Air Sungai'

                    WHEN UPPER(TRIM(sp.jenis_stasiun))
                        IN ('UDARA')
                    THEN 'Udara'

                    WHEN sp.jenis_stasiun IS NULL
                        OR TRIM(sp.jenis_stasiun) = ''
                    THEN 'TIDAK DIKETAHUI'

                    ELSE TRIM(sp.jenis_stasiun)
                END AS jenis_stasiun,

                NULLIF(
                    TRIM(sp.id_desa),
                    ''
                ) AS id_desa,

                NULLIF(
                    TRIM(sp.nama_desa),
                    ''
                ) AS nama_desa,

                CASE
                    WHEN sp.koordinat_gps IS NULL
                        OR TRIM(sp.koordinat_gps) = ''
                        OR TRIM(sp.koordinat_gps) = 'invalid'
                    THEN NULL
                    WHEN sp.koordinat_gps REGEXP '^-?[0-9]+\\.?[0-9]*,-?[0-9]+\\.?[0-9]*$'
                    THEN TRIM(sp.koordinat_gps)
                    ELSE NULL
                END AS koordinat_gps,

                CASE
                    WHEN UPPER(TRIM(sp.status_aktif))
                        IN ('AKTIF', '1', 'YES')
                    THEN 'Aktif'

                    WHEN UPPER(TRIM(sp.status_aktif))
                        IN ('NON-AKTIF', 'NON AKTIF', 'NONAKTIF', '0', 'NO')
                    THEN 'Non-Aktif'

                    WHEN sp.status_aktif IS NULL
                        OR TRIM(sp.status_aktif) = ''
                    THEN 'TIDAK DIKETAHUI'

                    ELSE 'TIDAK DIKETAHUI'
                END AS status_aktif,

                sp.sumber_database,
                sp.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_stasiun_pantau` sp

            WHERE
                sp.id_stasiun IS NOT NULL
                AND TRIM(sp.id_stasiun) <> ''

                AND sp.nama_stasiun IS NOT NULL
                AND TRIM(sp.nama_stasiun) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_stasiun_pantau selesai."
            )

            logging.info("Transform: stg_sda_izin_lingkungan ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_izin_lingkungan`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_izin_lingkungan`
            (
                id                          BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_izin                     VARCHAR(20),
                id_perusahaan               VARCHAR(20),
                nomor_izin                  VARCHAR(50),
                jenis_dokumen               VARCHAR(100),
                tanggal_terbit              DATE,
                masa_berlaku_tahun          INT,
                status_izin                 VARCHAR(20),
                sumber_database             VARCHAR(100),
                waktu_ekstraksi             DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_izin_lingkungan`
            (
                id_izin, id_perusahaan, nomor_izin, jenis_dokumen,
                tanggal_terbit, masa_berlaku_tahun, status_izin,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(il.id_izin)
                    AS id_izin,

                TRIM(il.id_perusahaan)
                    AS id_perusahaan,

                NULLIF(
                    TRIM(il.nomor_izin),
                    ''
                ) AS nomor_izin,

                CASE
                    WHEN UPPER(TRIM(il.jenis_dokumen))
                        IN ('AMDAL')
                    THEN 'AMDAL'

                    WHEN UPPER(TRIM(il.jenis_dokumen))
                        IN ('UKL-UPL', 'UKL UPL', 'UKLUPL')
                    THEN 'UKL-UPL'

                    WHEN UPPER(TRIM(il.jenis_dokumen))
                        IN ('SPPL')
                    THEN 'SPPL'

                    WHEN il.jenis_dokumen IS NULL
                        OR TRIM(il.jenis_dokumen) = ''
                    THEN 'TIDAK DIKETAHUI'

                    ELSE TRIM(il.jenis_dokumen)
                END AS jenis_dokumen,

                CASE
                    WHEN il.tanggal_terbit REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                        AND STR_TO_DATE(il.tanggal_terbit, '%Y-%m-%d') IS NOT NULL
                        AND STR_TO_DATE(il.tanggal_terbit, '%Y-%m-%d') <= CURDATE()
                    THEN STR_TO_DATE(il.tanggal_terbit, '%Y-%m-%d')
                    WHEN il.tanggal_terbit REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
                        AND STR_TO_DATE(il.tanggal_terbit, '%d/%m/%Y') IS NOT NULL
                        AND STR_TO_DATE(il.tanggal_terbit, '%d/%m/%Y') <= CURDATE()
                    THEN STR_TO_DATE(il.tanggal_terbit, '%d/%m/%Y')
                    WHEN il.tanggal_terbit REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
                        AND STR_TO_DATE(il.tanggal_terbit, '%d-%m-%Y') IS NOT NULL
                        AND STR_TO_DATE(il.tanggal_terbit, '%d-%m-%Y') <= CURDATE()
                    THEN STR_TO_DATE(il.tanggal_terbit, '%d-%m-%Y')
                    ELSE NULL
                END AS tanggal_terbit,

                CASE
                    WHEN CAST(il.masa_berlaku_tahun AS SIGNED) > 0
                        AND CAST(il.masa_berlaku_tahun AS SIGNED) <= 50
                    THEN CAST(il.masa_berlaku_tahun AS SIGNED)
                    ELSE NULL
                END AS masa_berlaku_tahun,

                CASE
                    WHEN UPPER(TRIM(il.status_izin))
                        IN ('AKTIF', 'BERLAKU')
                    THEN 'Aktif'

                    WHEN UPPER(TRIM(il.status_izin))
                        IN ('KADALUARSA', 'EXPIRED', 'NON-AKTIF')
                    THEN 'Kadaluarsa'

                    ELSE 'TIDAK DIKETAHUI'
                END AS status_izin,

                il.sumber_database,
                il.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_izin_lingkungan` il

            WHERE
                il.id_izin IS NOT NULL
                AND TRIM(il.id_izin) <> ''

                AND il.id_perusahaan IS NOT NULL
                AND TRIM(il.id_perusahaan) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_izin_lingkungan selesai."
            )

            logging.info("Transform: stg_sda_kualitas_air_sungai ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_kualitas_air_sungai`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_kualitas_air_sungai`
            (
                id                      BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_sampel               VARCHAR(20),
                id_stasiun              VARCHAR(20),
                nama_sungai             VARCHAR(255),
                waktu_pengambilan       DATETIME,
                ph_air                  DECIMAL(5,2),
                bod_mg_l                DECIMAL(8,2),
                cod_mg_l                DECIMAL(8,2),
                tss_mg_l                DECIMAL(8,2),
                status_mutu             VARCHAR(100),
                sumber_database         VARCHAR(100),
                waktu_ekstraksi         DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_kualitas_air_sungai`
            (
                id_sampel, id_stasiun, nama_sungai, waktu_pengambilan,
                ph_air, bod_mg_l, cod_mg_l, tss_mg_l, status_mutu,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(ka.id_sampel)
                    AS id_sampel,

                NULLIF(
                    TRIM(ka.id_stasiun),
                    ''
                ) AS id_stasiun,

                TRIM(ka.nama_sungai)
                    AS nama_sungai,

                CASE
                    WHEN ka.waktu_pengambilan REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%Y-%m-%d %H:%i:%s') IS NOT NULL
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%Y-%m-%d %H:%i:%s') <= NOW()
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%Y-%m-%d %H:%i:%s') >= '1900-01-01'
                    THEN STR_TO_DATE(ka.waktu_pengambilan, '%Y-%m-%d %H:%i:%s')
                    WHEN ka.waktu_pengambilan REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}$'
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y %H:%i') IS NOT NULL
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y %H:%i') <= NOW()
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y %H:%i') >= '1900-01-01'
                    THEN STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y %H:%i')
                    WHEN ka.waktu_pengambilan REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y') IS NOT NULL
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y') <= NOW()
                        AND STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y') >= '1900-01-01'
                    THEN STR_TO_DATE(ka.waktu_pengambilan, '%d-%m-%Y')
                    ELSE NULL
                END AS waktu_pengambilan,

                CASE
                    WHEN ka.ph_air REGEXP '^[0-9]+\\.?[0-9]*$'
                        AND CAST(ka.ph_air AS DECIMAL(5,2)) >= 0
                        AND CAST(ka.ph_air AS DECIMAL(5,2)) <= 14
                    THEN CAST(ka.ph_air AS DECIMAL(5,2))
                    ELSE NULL
                END AS ph_air,

                CASE
                    WHEN ka.bod_mg_l REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ka.bod_mg_l AS DECIMAL(8,2)) >= 0
                    THEN CAST(ka.bod_mg_l AS DECIMAL(8,2))
                    ELSE NULL
                END AS bod_mg_l,

                CASE
                    WHEN ka.cod_mg_l REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ka.cod_mg_l AS DECIMAL(8,2)) >= 0
                    THEN CAST(ka.cod_mg_l AS DECIMAL(8,2))
                    ELSE NULL
                END AS cod_mg_l,

                CASE
                    WHEN ka.tss_mg_l REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ka.tss_mg_l AS DECIMAL(8,2)) >= 0
                    THEN CAST(ka.tss_mg_l AS DECIMAL(8,2))
                    ELSE NULL
                END AS tss_mg_l,

                CASE
                    WHEN UPPER(TRIM(ka.status_mutu))
                        IN ('BAIK', 'GOOD')
                    THEN 'Baik'

                    WHEN UPPER(TRIM(ka.status_mutu))
                        IN ('SEDANG', 'MODERATE')
                    THEN 'Sedang'

                    WHEN UPPER(TRIM(ka.status_mutu))
                        IN ('BURUK', 'BAD', 'POOR')
                    THEN 'Buruk'

                    ELSE 'TIDAK DIKETAHUI'
                END AS status_mutu,

                ka.sumber_database,
                ka.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_kualitas_air_sungai` ka

            WHERE
                ka.id_sampel IS NOT NULL
                AND TRIM(ka.id_sampel) <> ''

                AND ka.nama_sungai IS NOT NULL
                AND TRIM(ka.nama_sungai) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_kualitas_air_sungai selesai."
            )

            logging.info("Transform: stg_sda_kualitas_udara ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_kualitas_udara`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_kualitas_udara`
            (
                id                      BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_record               VARCHAR(20),
                id_stasiun              VARCHAR(20),
                waktu_pengukuran        DATETIME,
                pm10                    DECIMAL(8,2),
                so2                     DECIMAL(8,2),
                co                      DECIMAL(8,2),
                o3                      DECIMAL(8,2),
                no2                     DECIMAL(8,2),
                kategori_ispu           VARCHAR(100),
                sumber_database         VARCHAR(100),
                waktu_ekstraksi         DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_kualitas_udara`
            (
                id_record, id_stasiun, waktu_pengukuran,
                pm10, so2, co, o3, no2, kategori_ispu,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(ku.id_record)
                    AS id_record,

                NULLIF(
                    TRIM(ku.id_stasiun),
                    ''
                ) AS id_stasiun,

                CASE
                    WHEN ku.waktu_pengukuran REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i:%s') IS NOT NULL
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i:%s') <= NOW()
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i:%s') >= '1900-01-01'
                    THEN STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i:%s')
                    WHEN ku.waktu_pengukuran REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}$'
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i') IS NOT NULL
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i') <= NOW()
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i') >= '1900-01-01'
                    THEN STR_TO_DATE(ku.waktu_pengukuran, '%Y-%m-%d %H:%i')
                    WHEN ku.waktu_pengukuran REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%d-%m-%Y') IS NOT NULL
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%d-%m-%Y') <= NOW()
                        AND STR_TO_DATE(ku.waktu_pengukuran, '%d-%m-%Y') >= '1900-01-01'
                    THEN STR_TO_DATE(ku.waktu_pengukuran, '%d-%m-%Y')
                    ELSE NULL
                END AS waktu_pengukuran,

                CASE
                    WHEN ku.pm10 REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ku.pm10 AS DECIMAL(8,2)) >= 0
                    THEN CAST(ku.pm10 AS DECIMAL(8,2))
                    ELSE NULL
                END AS pm10,

                CASE
                    WHEN ku.so2 REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ku.so2 AS DECIMAL(8,2)) >= 0
                    THEN CAST(ku.so2 AS DECIMAL(8,2))
                    ELSE NULL
                END AS so2,

                CASE
                    WHEN ku.co REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ku.co AS DECIMAL(8,2)) >= 0
                    THEN CAST(ku.co AS DECIMAL(8,2))
                    ELSE NULL
                END AS co,

                CASE
                    WHEN ku.o3 REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ku.o3 AS DECIMAL(8,2)) >= 0
                    THEN CAST(ku.o3 AS DECIMAL(8,2))
                    ELSE NULL
                END AS o3,

                CASE
                    WHEN ku.no2 REGEXP '^-?[0-9]+\\.?[0-9]*$'
                        AND CAST(ku.no2 AS DECIMAL(8,2)) >= 0
                    THEN CAST(ku.no2 AS DECIMAL(8,2))
                    ELSE NULL
                END AS no2,

                CASE
                    WHEN UPPER(TRIM(ku.kategori_ispu))
                        IN ('BAIK', 'GOOD')
                    THEN 'Baik'

                    WHEN UPPER(TRIM(ku.kategori_ispu))
                        IN ('SEDANG', 'MODERATE')
                    THEN 'Sedang'

                    WHEN UPPER(TRIM(ku.kategori_ispu))
                        IN ('TIDAK SEHAT', 'UNHEALTHY', 'BURUK')
                    THEN 'Tidak Sehat'

                    ELSE 'TIDAK DIKETAHUI'
                END AS kategori_ispu,

                ku.sumber_database,
                ku.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_kualitas_udara` ku

            WHERE
                ku.id_record IS NOT NULL
                AND TRIM(ku.id_record) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_kualitas_udara selesai."
            )

            logging.info("Transform: stg_sda_timbulan_sampah ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_timbulan_sampah`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_timbulan_sampah`
            (
                id                      BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_laporan              VARCHAR(20),
                id_fasilitas            VARCHAR(20),
                tanggal_lapor           DATE,
                volume_masuk_ton        DECIMAL(10,2),
                jenis_sampah_dominan    VARCHAR(100),
                sumber_sistem           VARCHAR(100),
                sumber_database         VARCHAR(100),
                waktu_ekstraksi         DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_timbulan_sampah`
            (
                id_laporan, id_fasilitas, tanggal_lapor, volume_masuk_ton,
                jenis_sampah_dominan, sumber_sistem,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(ts.id_laporan)
                    AS id_laporan,

                NULLIF(
                    TRIM(ts.id_fasilitas),
                    ''
                ) AS id_fasilitas,

                CASE
                    WHEN ts.tanggal_lapor REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                        AND STR_TO_DATE(ts.tanggal_lapor, '%Y-%m-%d') IS NOT NULL
                        AND STR_TO_DATE(ts.tanggal_lapor, '%Y-%m-%d') <= CURDATE()
                        AND STR_TO_DATE(ts.tanggal_lapor, '%Y-%m-%d') >= '1900-01-01'
                    THEN STR_TO_DATE(ts.tanggal_lapor, '%Y-%m-%d')
                    WHEN ts.tanggal_lapor REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
                        AND STR_TO_DATE(ts.tanggal_lapor, '%d-%m-%Y') IS NOT NULL
                        AND STR_TO_DATE(ts.tanggal_lapor, '%d-%m-%Y') <= CURDATE()
                        AND STR_TO_DATE(ts.tanggal_lapor, '%d-%m-%Y') >= '1900-01-01'
                    THEN STR_TO_DATE(ts.tanggal_lapor, '%d-%m-%Y')
                    ELSE NULL
                END AS tanggal_lapor,

                CASE
                    WHEN ts.volume_masuk_ton REGEXP '^[0-9]+\\.?[0-9]*$'
                        AND CAST(ts.volume_masuk_ton AS DECIMAL(10,2)) >= 0
                    THEN CAST(ts.volume_masuk_ton AS DECIMAL(10,2))
                    ELSE NULL
                END AS volume_masuk_ton,

                CASE
                    WHEN UPPER(TRIM(ts.jenis_sampah_dominan))
                        IN ('ORGANIK', 'ORGANIC')
                    THEN 'Organik'

                    WHEN UPPER(TRIM(ts.jenis_sampah_dominan))
                        IN ('ANORGANIK', 'ANORGANIC', 'NON-ORGANIK')
                    THEN 'Anorganik'

                    WHEN UPPER(TRIM(ts.jenis_sampah_dominan))
                        IN ('PLASTIK', 'PLASTIC')
                    THEN 'Plastik'

                    WHEN UPPER(TRIM(ts.jenis_sampah_dominan))
                        IN ('KERTAS', 'PAPER')
                    THEN 'Kertas'

                    WHEN UPPER(TRIM(ts.jenis_sampah_dominan))
                        IN ('CAMPURAN', 'MIXED')
                    THEN 'Campuran'

                    WHEN UPPER(TRIM(ts.jenis_sampah_dominan))
                        IN ('B3', 'BERBAHAYA')
                    THEN 'B3'

                    ELSE 'TIDAK DIKETAHUI'
                END AS jenis_sampah_dominan,

                NULLIF(
                    TRIM(ts.sumber_sistem),
                    ''
                ) AS sumber_sistem,

                ts.sumber_database,
                ts.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_timbulan_sampah` ts

            WHERE
                ts.id_laporan IS NOT NULL
                AND TRIM(ts.id_laporan) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_timbulan_sampah selesai."
            )

            logging.info("Transform: stg_sda_tutupan_lahan_rth ...")

            cursor.execute(f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_sda_tutupan_lahan_rth`;
            """)

            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_sda_tutupan_lahan_rth`
            (
                id                  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_polygon          VARCHAR(20),
                id_desa             VARCHAR(10),
                jenis_tutupan       VARCHAR(100),
                luas_hektar         DECIMAL(10,2),
                sumber_citra        VARCHAR(100),
                tanggal_citra       DATE,
                sumber_database     VARCHAR(100),
                waktu_ekstraksi     DATETIME
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_sda_tutupan_lahan_rth`
            (
                id_polygon, id_desa, jenis_tutupan, luas_hektar,
                sumber_citra, tanggal_citra,
                sumber_database, waktu_ekstraksi
            )
            SELECT DISTINCT

                TRIM(tl.id_polygon)
                    AS id_polygon,

                TRIM(tl.id_desa)
                    AS id_desa,

                CASE
                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('HUTAN KOTA', 'HUTANKOTA')
                    THEN 'Hutan Kota'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('TAMAN')
                    THEN 'Taman'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('JALUR HIJAU', 'JALURHIJAU')
                    THEN 'Jalur Hijau'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('KEBUN')
                    THEN 'Kebun'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('HUTAN LINDUNG', 'HUTANLINDUNG')
                    THEN 'Hutan Lindung'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('HUTAN ALAM', 'HUTANALAM')
                    THEN 'Hutan Alam'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('HUTAN PRODUKSI', 'HUTANPRODUKSI')
                    THEN 'Hutan Produksi'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('PERKEBUNAN')
                    THEN 'Perkebunan'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('SAWAH')
                    THEN 'Sawah'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('TAMAN NASIONAL', 'TAMANNASIONAL')
                    THEN 'Taman Nasional'

                    WHEN UPPER(TRIM(tl.jenis_tutupan))
                        IN ('RTH KOTA', 'RTHKOTA')
                    THEN 'RTH Kota'

                    ELSE 'TIDAK DIKETAHUI'
                END AS jenis_tutupan,

                CASE
                    WHEN tl.luas_hektar REGEXP '^[0-9]+\\.?[0-9]*$'
                        AND CAST(tl.luas_hektar AS DECIMAL(10,2)) >= 0
                    THEN CAST(tl.luas_hektar AS DECIMAL(10,2))
                    ELSE NULL
                END AS luas_hektar,

                NULLIF(
                    TRIM(tl.sumber_citra),
                    ''
                ) AS sumber_citra,

                CASE
                    WHEN tl.tanggal_citra REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
                        AND STR_TO_DATE(tl.tanggal_citra, '%Y-%m-%d') IS NOT NULL
                        AND STR_TO_DATE(tl.tanggal_citra, '%Y-%m-%d') <= CURDATE()
                        AND STR_TO_DATE(tl.tanggal_citra, '%Y-%m-%d') >= '1900-01-01'
                    THEN STR_TO_DATE(tl.tanggal_citra, '%Y-%m-%d')
                    WHEN tl.tanggal_citra REGEXP '^[0-9]{2}-[0-9]{2}-[0-9]{4}$'
                        AND STR_TO_DATE(tl.tanggal_citra, '%d-%m-%Y') IS NOT NULL
                        AND STR_TO_DATE(tl.tanggal_citra, '%d-%m-%Y') <= CURDATE()
                        AND STR_TO_DATE(tl.tanggal_citra, '%d-%m-%Y') >= '1900-01-01'
                    THEN STR_TO_DATE(tl.tanggal_citra, '%d-%m-%Y')
                    WHEN tl.tanggal_citra REGEXP '^[0-9]{2}/[0-9]{2}/[0-9]{4}$'
                        AND STR_TO_DATE(tl.tanggal_citra, '%d/%m/%Y') IS NOT NULL
                        AND STR_TO_DATE(tl.tanggal_citra, '%d/%m/%Y') <= CURDATE()
                        AND STR_TO_DATE(tl.tanggal_citra, '%d/%m/%Y') >= '1900-01-01'
                    THEN STR_TO_DATE(tl.tanggal_citra, '%d/%m/%Y')
                    ELSE NULL
                END AS tanggal_citra,

                tl.sumber_database,
                tl.waktu_ekstraksi

            FROM `{raw_db}`.`raw_sda_tutupan_lahan_rth` tl

            WHERE
                tl.id_polygon IS NOT NULL
                AND TRIM(tl.id_polygon) <> ''

                AND tl.id_desa IS NOT NULL
                AND TRIM(tl.id_desa) <> '';
            """)
            conn.commit()

            logging.info(
                "Transform: stg_sda_tutupan_lahan_rth selesai."
            )

            logging.info(
                "Transform staging selesai."
            )

        except Exception as e:
            conn.rollback()
            logging.error(
                "ERROR transform_staging_sda: %s | Query: %s",
                str(e),
                cursor._last_executed if hasattr(cursor, "_last_executed") else "N/A",
            )
            raise

        finally:
            cursor.close()
            conn.close()

    @task(task_id="load_to_dwh_sda")
    def load_to_dwh():

        logging.info(
            "Membuat dimension dan fact..."
        )

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        execute_sql([align_collation])

        drop_tables = [
            f"SET FOREIGN_KEY_CHECKS = 0;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_sda_tutupan_lahan`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_sda_timbulan_sampah`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_sda_kualitas_udara`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_sda_kualitas_air`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_sda_izin_lingkungan`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_sda_stasiun_pantau`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_sda_perusahaan`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_sda_fasilitas_sampah`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_sda_wilayah`;",
            f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_sda_waktu`;",
        ]

        execute_sql(drop_tables)

        logging.info("Drop tables selesai")

        create_tables = [

            f"SET FOREIGN_KEY_CHECKS = 0;",

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_sda_waktu`
            (
                waktu_key INT PRIMARY KEY,

                tanggal DATE NOT NULL,

                hari INT,
                bulan INT,
                nama_bulan VARCHAR(20),
                kuartal INT,
                tahun INT,

                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,

                INDEX idx_sda_waktu_tanggal (tanggal),
                INDEX idx_sda_waktu_tahun (tahun)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_sda_wilayah`
            (
                wilayah_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                id_desa VARCHAR(10)
                    NOT NULL,

                nama_desa VARCHAR(100),

                id_kecamatan VARCHAR(10),

                nama_kecamatan VARCHAR(100),

                id_kabupaten_kota VARCHAR(10),

                nama_kabupaten_kota VARCHAR(100),

                nama_provinsi VARCHAR(100),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_wilayah
                    (id_desa)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_sda_fasilitas_sampah`
            (
                fasilitas_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                id_fasilitas VARCHAR(20)
                    NOT NULL,

                nama_fasilitas VARCHAR(255),

                jenis_fasilitas VARCHAR(50),

                id_desa VARCHAR(10),

                kapasitas_maksimal_ton DECIMAL(10,2),

                status_operasional VARCHAR(20),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_fasilitas
                    (id_fasilitas)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_sda_perusahaan`
            (
                perusahaan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                id_perusahaan VARCHAR(20)
                    NOT NULL,

                nama_perusahaan VARCHAR(255),

                bidang_usaha VARCHAR(100),

                alamat_lengkap VARCHAR(300),

                id_desa VARCHAR(10),

                kontak_perusahaan VARCHAR(50),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_perusahaan
                    (id_perusahaan)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_sda_stasiun_pantau`
            (
                stasiun_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                id_stasiun VARCHAR(20)
                    NOT NULL,

                nama_stasiun VARCHAR(255),

                jenis_stasiun VARCHAR(50),

                id_desa VARCHAR(10),

                koordinat_gps VARCHAR(100),

                status_aktif VARCHAR(20),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_stasiun
                    (id_stasiun)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_sda_izin_lingkungan`
            (
                fact_izin_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                perusahaan_key BIGINT,

                wilayah_key BIGINT,

                waktu_terbit_key INT,

                id_izin VARCHAR(20)
                    NOT NULL,

                nomor_izin VARCHAR(50),

                jenis_dokumen VARCHAR(100),

                tanggal_terbit DATE,

                masa_berlaku_tahun INT,

                status_izin VARCHAR(20),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_fact_izin
                    (id_izin),

                INDEX idx_sda_fact_izin_perusahaan
                    (perusahaan_key),

                INDEX idx_sda_fact_izin_wilayah
                    (wilayah_key),

                INDEX idx_sda_fact_izin_waktu_terbit
                    (waktu_terbit_key),

                INDEX idx_sda_fact_izin_status
                    (status_izin)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_sda_kualitas_air`
            (
                fact_kualitas_air_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                stasiun_key BIGINT,

                wilayah_key BIGINT,

                waktu_key INT,

                id_sampel VARCHAR(20)
                    NOT NULL,

                nama_sungai VARCHAR(255),

                waktu_pengambilan DATETIME,

                ph_air DECIMAL(5,2),

                bod_mg_l DECIMAL(8,2),

                cod_mg_l DECIMAL(8,2),

                tss_mg_l DECIMAL(8,2),

                status_mutu VARCHAR(100),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_fact_kualitas_air
                    (id_sampel),

                INDEX idx_sda_fact_air_stasiun
                    (stasiun_key),

                INDEX idx_sda_fact_air_wilayah
                    (wilayah_key),

                INDEX idx_sda_fact_air_waktu
                    (waktu_key),

                INDEX idx_sda_fact_air_status
                    (status_mutu)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_sda_kualitas_udara`
            (
                fact_kualitas_udara_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                stasiun_key BIGINT,

                wilayah_key BIGINT,

                waktu_key INT,

                id_record VARCHAR(20)
                    NOT NULL,

                waktu_pengukuran DATETIME,

                pm10 DECIMAL(8,2),

                so2 DECIMAL(8,2),

                co DECIMAL(8,2),

                o3 DECIMAL(8,2),

                no2 DECIMAL(8,2),

                kategori_ispu VARCHAR(100),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_fact_kualitas_udara
                    (id_record),

                INDEX idx_sda_fact_udara_stasiun
                    (stasiun_key),

                INDEX idx_sda_fact_udara_wilayah
                    (wilayah_key),

                INDEX idx_sda_fact_udara_waktu
                    (waktu_key),

                INDEX idx_sda_fact_udara_kategori
                    (kategori_ispu)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_sda_timbulan_sampah`
            (
                fact_timbulan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                fasilitas_key BIGINT,

                waktu_key INT,

                id_laporan VARCHAR(20)
                    NOT NULL,

                tanggal_lapor DATE,

                volume_masuk_ton DECIMAL(10,2),

                jenis_sampah_dominan VARCHAR(100),

                sumber_sistem VARCHAR(100),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_fact_timbulan
                    (id_laporan),

                INDEX idx_sda_fact_timbulan_fasilitas
                    (fasilitas_key),

                INDEX idx_sda_fact_timbulan_waktu
                    (waktu_key),

                INDEX idx_sda_fact_timbulan_jenis
                    (jenis_sampah_dominan)
            );
            """,

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_sda_tutupan_lahan`
            (
                fact_tutupan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                wilayah_key BIGINT,

                waktu_key INT,

                id_polygon VARCHAR(20)
                    NOT NULL,

                jenis_tutupan VARCHAR(100),

                luas_hektar DECIMAL(10,2),

                sumber_citra VARCHAR(100),

                tanggal_citra DATE,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_sda_fact_tutupan
                    (id_polygon),

                INDEX idx_sda_fact_tutupan_wilayah
                    (wilayah_key),

                INDEX idx_sda_fact_tutupan_waktu
                    (waktu_key),

                INDEX idx_sda_fact_tutupan_jenis
                    (jenis_tutupan)
            );
            """,
        ]

        execute_sql(create_tables)

        execute_sql([f"SET FOREIGN_KEY_CHECKS = 1;"])

        logging.info("Create tables selesai")

        load_dimensions = [

            f"""
            INSERT INTO `{dwh_db}`.`dim_sda_waktu`
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

            f"""
            INSERT INTO `{dwh_db}`.`dim_sda_wilayah`
            (
                id_desa,
                nama_desa,
                id_kecamatan,
                nama_kecamatan,
                id_kabupaten_kota,
                nama_kabupaten_kota,
                nama_provinsi,
                sumber_database,
                waktu_load
            )

            SELECT
                id_desa,
                nama_desa,
                id_kecamatan,
                nama_kecamatan,
                id_kabupaten_kota,
                nama_kabupaten_kota,
                nama_provinsi,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_sda_wilayah`

            ON DUPLICATE KEY UPDATE

                nama_desa =
                    VALUES(nama_desa),

                id_kecamatan =
                    VALUES(id_kecamatan),

                nama_kecamatan =
                    VALUES(nama_kecamatan),

                id_kabupaten_kota =
                    VALUES(id_kabupaten_kota),

                nama_kabupaten_kota =
                    VALUES(nama_kabupaten_kota),

                nama_provinsi =
                    VALUES(nama_provinsi),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`dim_sda_fasilitas_sampah`
            (
                id_fasilitas,
                nama_fasilitas,
                jenis_fasilitas,
                id_desa,
                kapasitas_maksimal_ton,
                status_operasional,
                sumber_database,
                waktu_load
            )

            SELECT
                id_fasilitas,
                nama_fasilitas,
                jenis_fasilitas,
                id_desa,
                kapasitas_maksimal_ton,
                status_operasional,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_sda_fasilitas_sampah`

            ON DUPLICATE KEY UPDATE

                nama_fasilitas =
                    VALUES(nama_fasilitas),

                jenis_fasilitas =
                    VALUES(jenis_fasilitas),

                id_desa =
                    VALUES(id_desa),

                kapasitas_maksimal_ton =
                    VALUES(kapasitas_maksimal_ton),

                status_operasional =
                    VALUES(status_operasional),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`dim_sda_perusahaan`
            (
                id_perusahaan,
                nama_perusahaan,
                bidang_usaha,
                alamat_lengkap,
                id_desa,
                kontak_perusahaan,
                sumber_database,
                waktu_load
            )

            SELECT
                id_perusahaan,
                nama_perusahaan,
                bidang_usaha,
                alamat_lengkap,
                id_desa,
                kontak_perusahaan,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_sda_perusahaan`

            ON DUPLICATE KEY UPDATE

                nama_perusahaan =
                    VALUES(nama_perusahaan),

                bidang_usaha =
                    VALUES(bidang_usaha),

                alamat_lengkap =
                    VALUES(alamat_lengkap),

                id_desa =
                    VALUES(id_desa),

                kontak_perusahaan =
                    VALUES(kontak_perusahaan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`dim_sda_stasiun_pantau`
            (
                id_stasiun,
                nama_stasiun,
                jenis_stasiun,
                id_desa,
                koordinat_gps,
                status_aktif,
                sumber_database,
                waktu_load
            )

            SELECT
                id_stasiun,
                nama_stasiun,
                jenis_stasiun,
                id_desa,
                koordinat_gps,
                status_aktif,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_sda_stasiun_pantau`

            ON DUPLICATE KEY UPDATE

                nama_stasiun =
                    VALUES(nama_stasiun),

                jenis_stasiun =
                    VALUES(jenis_stasiun),

                id_desa =
                    VALUES(id_desa),

                koordinat_gps =
                    VALUES(koordinat_gps),

                status_aktif =
                    VALUES(status_aktif),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        logging.info("Load dimensions selesai")

        load_facts = [

            f"""
            INSERT INTO `{dwh_db}`.`fact_sda_izin_lingkungan`
            (
                perusahaan_key,
                wilayah_key,
                waktu_terbit_key,
                id_izin,
                nomor_izin,
                jenis_dokumen,
                tanggal_terbit,
                masa_berlaku_tahun,
                status_izin,
                sumber_database,
                waktu_load
            )

            SELECT

                dp.perusahaan_key,

                dw.wilayah_key,

                CASE
                    WHEN sil.tanggal_terbit IS NOT NULL
                    THEN CAST(
                        DATE_FORMAT(
                            sil.tanggal_terbit,
                            '%Y%m%d'
                        ) AS UNSIGNED
                    )
                    ELSE NULL
                END AS waktu_terbit_key,

                sil.id_izin,

                sil.nomor_izin,

                sil.jenis_dokumen,

                sil.tanggal_terbit,

                sil.masa_berlaku_tahun,

                sil.status_izin,

                sil.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_sda_izin_lingkungan` sil

            LEFT JOIN
                `{dwh_db}`.`dim_sda_perusahaan` dp
                ON sil.id_perusahaan = dp.id_perusahaan

            LEFT JOIN
                `{staging_db}`.`stg_sda_perusahaan` sp
                ON sil.id_perusahaan = sp.id_perusahaan

            LEFT JOIN
                `{dwh_db}`.`dim_sda_wilayah` dw
                ON sp.id_desa = dw.id_desa

            ON DUPLICATE KEY UPDATE

                perusahaan_key =
                    VALUES(perusahaan_key),

                wilayah_key =
                    VALUES(wilayah_key),

                waktu_terbit_key =
                    VALUES(waktu_terbit_key),

                nomor_izin =
                    VALUES(nomor_izin),

                jenis_dokumen =
                    VALUES(jenis_dokumen),

                tanggal_terbit =
                    VALUES(tanggal_terbit),

                masa_berlaku_tahun =
                    VALUES(masa_berlaku_tahun),

                status_izin =
                    VALUES(status_izin),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`fact_sda_kualitas_air`
            (
                stasiun_key,
                wilayah_key,
                waktu_key,
                id_sampel,
                nama_sungai,
                waktu_pengambilan,
                ph_air,
                bod_mg_l,
                cod_mg_l,
                tss_mg_l,
                status_mutu,
                sumber_database,
                waktu_load
            )

            SELECT

                dst.stasiun_key,

                dw.wilayah_key,

                CASE
                    WHEN DATE(ska.waktu_pengambilan) IS NOT NULL
                    THEN CAST(
                        DATE_FORMAT(
                            DATE(ska.waktu_pengambilan),
                            '%Y%m%d'
                        ) AS UNSIGNED
                    )
                    ELSE NULL
                END AS waktu_key,

                ska.id_sampel,

                ska.nama_sungai,

                ska.waktu_pengambilan,

                ska.ph_air,

                ska.bod_mg_l,

                ska.cod_mg_l,

                ska.tss_mg_l,

                ska.status_mutu,

                ska.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_sda_kualitas_air_sungai` ska

            LEFT JOIN
                `{dwh_db}`.`dim_sda_stasiun_pantau` dst
                ON ska.id_stasiun = dst.id_stasiun

            LEFT JOIN
                `{staging_db}`.`stg_sda_stasiun_pantau` ssp
                ON ska.id_stasiun = ssp.id_stasiun

            LEFT JOIN
                `{dwh_db}`.`dim_sda_wilayah` dw
                ON ssp.id_desa = dw.id_desa

            ON DUPLICATE KEY UPDATE

                stasiun_key =
                    VALUES(stasiun_key),

                wilayah_key =
                    VALUES(wilayah_key),

                waktu_key =
                    VALUES(waktu_key),

                nama_sungai =
                    VALUES(nama_sungai),

                waktu_pengambilan =
                    VALUES(waktu_pengambilan),

                ph_air =
                    VALUES(ph_air),

                bod_mg_l =
                    VALUES(bod_mg_l),

                cod_mg_l =
                    VALUES(cod_mg_l),

                tss_mg_l =
                    VALUES(tss_mg_l),

                status_mutu =
                    VALUES(status_mutu),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`fact_sda_kualitas_udara`
            (
                stasiun_key,
                wilayah_key,
                waktu_key,
                id_record,
                waktu_pengukuran,
                pm10,
                so2,
                co,
                o3,
                no2,
                kategori_ispu,
                sumber_database,
                waktu_load
            )

            SELECT

                dst.stasiun_key,

                dw.wilayah_key,

                CASE
                    WHEN DATE(sku.waktu_pengukuran) IS NOT NULL
                    THEN CAST(
                        DATE_FORMAT(
                            DATE(sku.waktu_pengukuran),
                            '%Y%m%d'
                        ) AS UNSIGNED
                    )
                    ELSE NULL
                END AS waktu_key,

                sku.id_record,

                sku.waktu_pengukuran,

                sku.pm10,

                sku.so2,

                sku.co,

                sku.o3,

                sku.no2,

                sku.kategori_ispu,

                sku.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_sda_kualitas_udara` sku

            LEFT JOIN
                `{dwh_db}`.`dim_sda_stasiun_pantau` dst
                ON sku.id_stasiun = dst.id_stasiun

            LEFT JOIN
                `{staging_db}`.`stg_sda_stasiun_pantau` ssp
                ON sku.id_stasiun = ssp.id_stasiun

            LEFT JOIN
                `{dwh_db}`.`dim_sda_wilayah` dw
                ON ssp.id_desa = dw.id_desa

            ON DUPLICATE KEY UPDATE

                stasiun_key =
                    VALUES(stasiun_key),

                wilayah_key =
                    VALUES(wilayah_key),

                waktu_key =
                    VALUES(waktu_key),

                waktu_pengukuran =
                    VALUES(waktu_pengukuran),

                pm10 =
                    VALUES(pm10),

                so2 =
                    VALUES(so2),

                co =
                    VALUES(co),

                o3 =
                    VALUES(o3),

                no2 =
                    VALUES(no2),

                kategori_ispu =
                    VALUES(kategori_ispu),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`fact_sda_timbulan_sampah`
            (
                fasilitas_key,
                waktu_key,
                id_laporan,
                tanggal_lapor,
                volume_masuk_ton,
                jenis_sampah_dominan,
                sumber_sistem,
                sumber_database,
                waktu_load
            )

            SELECT

                df.fasilitas_key,

                CASE
                    WHEN sts.tanggal_lapor IS NOT NULL
                    THEN CAST(
                        DATE_FORMAT(
                            sts.tanggal_lapor,
                            '%Y%m%d'
                        ) AS UNSIGNED
                    )
                    ELSE NULL
                END AS waktu_key,

                sts.id_laporan,

                sts.tanggal_lapor,

                sts.volume_masuk_ton,

                sts.jenis_sampah_dominan,

                sts.sumber_sistem,

                sts.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_sda_timbulan_sampah` sts

            LEFT JOIN
                `{dwh_db}`.`dim_sda_fasilitas_sampah` df
                ON sts.id_fasilitas = df.id_fasilitas

            ON DUPLICATE KEY UPDATE

                fasilitas_key =
                    VALUES(fasilitas_key),

                waktu_key =
                    VALUES(waktu_key),

                tanggal_lapor =
                    VALUES(tanggal_lapor),

                volume_masuk_ton =
                    VALUES(volume_masuk_ton),

                jenis_sampah_dominan =
                    VALUES(jenis_sampah_dominan),

                sumber_sistem =
                    VALUES(sumber_sistem),

                waktu_load =
                    VALUES(waktu_load);
            """,

            f"""
            INSERT INTO `{dwh_db}`.`fact_sda_tutupan_lahan`
            (
                wilayah_key,
                waktu_key,
                id_polygon,
                jenis_tutupan,
                luas_hektar,
                sumber_citra,
                tanggal_citra,
                sumber_database,
                waktu_load
            )

            SELECT

                dw.wilayah_key,

                CASE
                    WHEN stl.tanggal_citra IS NOT NULL
                    THEN CAST(
                        DATE_FORMAT(
                            stl.tanggal_citra,
                            '%Y%m%d'
                        ) AS UNSIGNED
                    )
                    ELSE NULL
                END AS waktu_key,

                stl.id_polygon,

                stl.jenis_tutupan,

                stl.luas_hektar,

                stl.sumber_citra,

                stl.tanggal_citra,

                stl.sumber_database,

                NOW() AS waktu_load

            FROM
                `{staging_db}`.`stg_sda_tutupan_lahan_rth` stl

            LEFT JOIN
                `{dwh_db}`.`dim_sda_wilayah` dw
                ON stl.id_desa = dw.id_desa

            ON DUPLICATE KEY UPDATE

                wilayah_key =
                    VALUES(wilayah_key),

                waktu_key =
                    VALUES(waktu_key),

                jenis_tutupan =
                    VALUES(jenis_tutupan),

                luas_hektar =
                    VALUES(luas_hektar),

                sumber_citra =
                    VALUES(sumber_citra),

                tanggal_citra =
                    VALUES(tanggal_citra),

                waktu_load =
                    VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

        logging.info(
            "Load ke Data Warehouse selesai."
        )

    t_extract = extract_to_raw()
    t_transform = transform_staging()
    t_load = load_to_dwh()

    t_extract >> t_transform >> t_load

    return t_load
