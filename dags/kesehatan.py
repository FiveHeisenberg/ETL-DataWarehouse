from __future__ import annotations

import logging
import time

import pendulum
import requests

from airflow.sdk import task


"""
DNS KESEHATAN (RUMAH SAKIT) — ETL API db_kemenkes -> raw_data -> staging_area -> dwh

Pipeline mengikuti pola dukcapil.py:
- extract_to_raw   : REST API -> schema raw_data (satu tabel per endpoint)
- transform_staging: raw_data -> schema staging_area (cleansing/standardisasi/validasi)
- load_to_dwh      : staging_area -> schema dwh (bintang/snowflake, SCD Type 2 untuk dim_kesehatan_rs)

Sumber: http://192.168.222.152:8011/api/kemenkes/{endpoint}
Bentuk respons: {"status": "success", "data": [...], "total": N}
(server tidak menerapkan paginasi; extract tetap defensif terhadap pembungkus/paginasi).
"""


# ============================================================
# MIGRASI STRUKTUR LAMA -> STRUKTUR BARU
# ============================================================
# True  : DROP tabel dim/fact tenaga medis & fasilitas yang dibuat
#         dengan struktur lama (grain kelompok / tanpa nama_fasilitas)
#         lalu dibuat ulang dengan struktur baru.
# False : setel menjadi False SETELAH struktur baru berhasil dibuat
#         pertama kali, agar DROP tidak dijalankan lagi pada run berikutnya.
MIGRASI_STRUKTUR_LAMA = True

# ============================================================
# MIGRASI WILAYAH -> STRUKTUR BARU
# ============================================================
# True  : DROP dim_kesehatan_rs dan semua fact yang memakai rs_key,
#         lalu dibuat ulang dengan kolom wilayah_key menggantikan
#         kolom wilayah yang sebelumnya inline di dim_kesehatan_rs.
# False : setel menjadi False SETELAH struktur baru berhasil dibuat
#         pertama kali, agar DROP tidak dijalankan lagi pada run berikutnya.
MIGRASI_WILAYAH = True


# ============================================================
# KONFIGURASI DOMAIN KESEHATAN
# ============================================================

SOURCE_ENDPOINTS = {
    "provinsi":              "/provinsi",
    "kabupaten_kota":        "/kabupaten-kota",
    "kelas_rs":              "/kelas-rs",
    "pemilik_rs":            "/pemilik-rs",
    "jenis_rs":              "/jenis-rs",
    "rs":                    "/rs",
    "jenis_layanan_rs":      "/jenis-layanan-rs",
    "layanan_rs":            "/layanan-rs",
    "jenis_fasilitas_rs":    "/jenis-fasilitas-rs",
    "fasilitas_rs":          "/fasilitas-rs",
    "kelompok_tenaga_medis": "/kelompok-tenaga-medis",
    "jenis_tenaga_medis":    "/jenis-tenaga-medis",
    "tenaga_medis":          "/tenaga-medis",
    "kategori_penyakit":     "/kategori-penyakit",
    "penyakit":              "/penyakit",
    "pasien":                "/pasien",
    "kasus_penyakit_rs":     "/kasus-penyakit-rs",
    "puskesmas":             "/puskesmas",
}


# ============================================================
# HELPER: HTTP + PARSING RESPONS DEFENSIF
# ============================================================

def _get_with_retry(url, timeout=120, retries=3, backoff=5):
    """GET dengan retry + backoff eksponensial sederhana."""

    last_err = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as err:  # noqa: BLE001
            last_err = err
            logging.warning(
                "Request gagal (percobaan %d/%d) %s: %s",
                attempt,
                retries,
                url,
                err,
            )
            if attempt < retries:
                time.sleep(backoff * attempt)

    raise RuntimeError(f"Gagal mengambil data dari {url}") from last_err


def _extract_records(payload):
    """Normalisasi beragam bentuk pembungkus respons menjadi list[dict]."""

    if isinstance(payload, list):
        return [rec for rec in payload if isinstance(rec, dict)]

    if isinstance(payload, dict):
        # pembungkus umum: data / results / records / items / rows
        for key in ("data", "results", "records", "items", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return [rec for rec in value if isinstance(rec, dict)]
            if isinstance(value, dict):
                nested = _extract_records(value)
                if nested:
                    return nested

        # dict tunggal tanpa pembungkus list (satu record)
        if not any(
            key in payload
            for key in ("data", "results", "records", "items", "rows")
        ):
            return [payload]

    return []


def _has_next_page(payload, page, page_size):
    """Baca metadata paginasi bila tersedia."""

    if not isinstance(payload, dict):
        return False

    pagination = payload.get("pagination")

    if isinstance(pagination, dict):
        if "has_next" in pagination:
            return bool(pagination["has_next"])
        total_pages = pagination.get("total_pages")
        if total_pages is not None:
            return page < int(total_pages)
        total = pagination.get("total")
        if total is not None:
            return page * page_size < int(total)

    if "has_next" in payload:
        return bool(payload["has_next"])
    if "next" in payload:
        return bool(payload["next"])

    total = payload.get("total")
    if total is not None:
        return page * page_size < int(total)

    return False


def _fetch_endpoint(api_base_url, endpoint, page_size=100, max_pages=1000):
    """
    Ambil seluruh record dari sebuah endpoint secara defensif.

    Mendukung server yang:
    - membungkus data dengan `data` / `results` / list langsung
    - melakukan paginasi nyata (metadata pagination/has_next/total)
    - mengabaikan paginasi (mengembalikan semua data sekaligus)
    """

    collected = []
    page = 1
    first_records = None

    while page <= max_pages:

        separator = "&" if "?" in endpoint else "?"
        url = (
            f"{api_base_url}{endpoint}"
            f"{separator}page={page}&limit={page_size}"
        )

        response = _get_with_retry(url)
        payload = response.json()
        records = _extract_records(payload)

        if not records:
            break

        if page == 1:
            first_records = records
        elif records == first_records:
            # server mengabaikan paginasi -> data identik -> hentikan
            break

        collected.extend(records)

        total = None
        if isinstance(payload, dict):
            total = payload.get("total")
            pagination = payload.get("pagination")
            if isinstance(pagination, dict) and pagination.get("total") is not None:
                total = pagination.get("total")

        if total is not None and len(collected) >= int(total):
            break
        if len(records) < page_size:
            break
        if not _has_next_page(payload, page, page_size):
            break

        page += 1

    return collected


# ============================================================
# PIPELINE KESEHATAN
# ============================================================

def create_kesehatan_tasks(
    execute_sql,
    get_mysql_hook,
    raw_db,
    staging_db,
    dwh_db,
    api_base_url,
):
    """
    execute_sql    : helper untuk menjalankan list query SQL (didefinisikan di main.py)
    get_mysql_hook : helper koneksi ke server raw_data & staging_area
    raw_db         : nama database raw_data
    staging_db     : nama database staging_area
    dwh_db         : nama database dwh
    api_base_url   : base URL API sumber kesehatan (mis. http://host:8011/api/kemenkes)
    """

    # ========================================================
    # TASK 1: EXTRACT API -> RAW_DATA
    # ========================================================
    # Menyalin data API apa adanya (mirror) ke `raw_<endpoint>` beserta
    # kolom sumber_database (URL API) dan waktu_ekstraksi (WIB).

    @task
    def extract_to_raw():

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:

            for table_name, endpoint in SOURCE_ENDPOINTS.items():

                raw_table = f"raw_{table_name}"

                logging.info(
                    "Extract API %s -> %s.%s",
                    f"{api_base_url}{endpoint}",
                    raw_db,
                    raw_table,
                )

                # --------------------------------------------
                # Fetch data dari API (retry + paginasi defensif)
                # --------------------------------------------

                records = _fetch_endpoint(api_base_url, endpoint)

                if not records:
                    raise RuntimeError(
                        f"Extract gagal: endpoint {endpoint} "
                        f"mengembalikan 0 records. Periksa API "
                        f"{api_base_url}{endpoint}."
                    )

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
                        `sumber_database` VARCHAR(255),
                        `waktu_ekstraksi` DATETIME
                    )
                    CHARACTER SET utf8mb4
                    COLLATE utf8mb4_0900_ai_ci;
                    """
                )

                # --------------------------------------------
                # Insert data per batch
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
                                str(rec.get(c)).strip()
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
    # TASK 2A: TRANSFORM - DIMENSION BASIC (tabel master kecil)
    # ========================================================
    # Cleansing provinsi, kabupaten, kelas, pemilik, jenis RS,
    # jenis layanan, jenis fasilitas, kelompok tenaga medis, kategori penyakit.
    # Tabel-tabel ini kecil dan menjadi dependency untuk tabel lainnya.

    @task
    def transform_dimension_basic():

        logging.info("Memulai transform dimension basic...")

        align_collation = f"""
        ALTER DATABASE `{staging_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        transformations = [

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
                TRIM(id_provinsi) AS id_provinsi,
                NULLIF(TRIM(nama_provinsi), '') AS nama_provinsi,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_provinsi`

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
            CREATE TABLE `{staging_db}`.`stg_kabupaten_kota`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_kabupaten_kota) AS id_kabupaten_kota,
                TRIM(id_provinsi) AS id_provinsi,
                NULLIF(TRIM(nama_kabupaten_kota), '') AS nama_kabupaten_kota,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_kabupaten_kota`

            WHERE
                id_kabupaten_kota IS NOT NULL
                AND id_provinsi IS NOT NULL;
            """,

            # =================================================
            # KELAS RS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kelas_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_kelas_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_kelas_rs) AS id_kelas_rs,
                NULLIF(TRIM(nama_kelas), '') AS nama_kelas,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_kelas_rs`

            WHERE id_kelas_rs IS NOT NULL;
            """,

            # =================================================
            # PEMILIK RS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pemilik_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pemilik_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_pemilik_rs) AS id_pemilik_rs,
                NULLIF(TRIM(nama_pemilik), '') AS nama_pemilik,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_pemilik_rs`

            WHERE id_pemilik_rs IS NOT NULL;
            """,

            # =================================================
            # JENIS RS
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_jenis_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_jenis_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_jenis_rs) AS id_jenis_rs,
                NULLIF(TRIM(nama_jenis_rs), '') AS nama_jenis_rs,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_jenis_rs`

            WHERE id_jenis_rs IS NOT NULL;
            """,

            # =================================================
            # JENIS LAYANAN RS (master kecil)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_jenis_layanan_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_jenis_layanan_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_jenis_layanan_rs) AS id_jenis_layanan_rs,
                NULLIF(TRIM(nama_layanan), '') AS nama_layanan,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_jenis_layanan_rs`

            WHERE id_jenis_layanan_rs IS NOT NULL;
            """,

            # =================================================
            # JENIS FASILITAS RS (master kecil)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_jenis_fasilitas_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_jenis_fasilitas_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_jenis_fasilitas) AS id_jenis_fasilitas,
                NULLIF(TRIM(nama_jenis_fasilitas), '') AS nama_jenis_fasilitas,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_jenis_fasilitas_rs`

            WHERE id_jenis_fasilitas IS NOT NULL;
            """,

            # =================================================
            # KATEGORI PENYAKIT (master kecil)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kategori_penyakit`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_kategori_penyakit`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_kategori_penyakit) AS id_kategori_penyakit,
                NULLIF(TRIM(nama_kategori), '') AS nama_kategori,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_kategori_penyakit`

            WHERE id_kategori_penyakit IS NOT NULL;
            """,
        ]

        execute_sql([align_collation] + transformations)
        logging.info("Transform dimension basic kesehatan selesai.")

    # ========================================================
    # TASK 2B: TRANSFORM - RS FAMILY (RS + relasi + tenaga medis + penyakit)
    # ========================================================
    # Tabel-tabel yang berkaitan dengan RS: RS, layanan, fasilitas,
    # tenaga medis, penyakit, dan puskesmas. Depends on task 2A.

    @task
    def transform_rs_family():

        logging.info("Memulai transform RS family...")

        transformations = [

            # =================================================
            # RS (cleansing + koordinat)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_rs) AS id_rs,
                NULLIF(TRIM(nama_rs), '') AS nama_rs,
                TRIM(id_kabupaten_kota) AS id_kabupaten_kota,
                NULLIF(TRIM(alamat), '') AS alamat,
                NULLIF(TRIM(telepon), '') AS telepon,
                TRIM(id_pemilik_rs) AS id_pemilik_rs,
                TRIM(id_kelas_rs) AS id_kelas_rs,
                TRIM(id_jenis_rs) AS id_jenis_rs,

                CASE
                    WHEN TRIM(latitude)
                        REGEXP '^-?[0-9]+([.][0-9]+)?$'
                    THEN CAST(latitude AS DECIMAL(10,7))
                    ELSE NULL
                END AS latitude,

                CASE
                    WHEN TRIM(longitude)
                        REGEXP '^-?[0-9]+([.][0-9]+)?$'
                    THEN CAST(longitude AS DECIMAL(10,7))
                    ELSE NULL
                END AS longitude,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_rs`

            WHERE
                id_rs IS NOT NULL
                AND TRIM(nama_rs) <> '';
            """,

            # =================================================
            # RS LENGKAP (denormalisasi untuk DWH)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_rs_lengkap`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_rs_lengkap`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT
                r.id_rs,
                r.nama_rs,
                r.alamat,
                r.telepon,
                r.latitude,
                r.longitude,

                r.id_kelas_rs,
                k.nama_kelas,

                r.id_jenis_rs,
                j.nama_jenis_rs,

                r.id_pemilik_rs,
                p.nama_pemilik,

                r.id_kabupaten_kota,
                kab.nama_kabupaten_kota,

                kab.id_provinsi,
                prov.nama_provinsi,

                r.sumber_database,
                r.waktu_ekstraksi

            FROM `{staging_db}`.`stg_rs` r

            LEFT JOIN `{staging_db}`.`stg_kelas_rs` k
                ON r.id_kelas_rs = k.id_kelas_rs

            LEFT JOIN `{staging_db}`.`stg_jenis_rs` j
                ON r.id_jenis_rs = j.id_jenis_rs

            LEFT JOIN `{staging_db}`.`stg_pemilik_rs` p
                ON r.id_pemilik_rs = p.id_pemilik_rs

            LEFT JOIN `{staging_db}`.`stg_kabupaten_kota` kab
                ON r.id_kabupaten_kota = kab.id_kabupaten_kota

            LEFT JOIN `{staging_db}`.`stg_provinsi` prov
                ON kab.id_provinsi = prov.id_provinsi;
            """,

            # =================================================
            # LAYANAN RS (relasi rs x jenis layanan)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_layanan_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_layanan_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_layanan_rs) AS id_layanan_rs,
                TRIM(id_jenis_layanan_rs) AS id_jenis_layanan_rs,
                TRIM(id_rs) AS id_rs,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_layanan_rs`

            WHERE
                id_layanan_rs IS NOT NULL
                AND id_rs IS NOT NULL
                AND id_jenis_layanan_rs IS NOT NULL;
            """,

            # =================================================
            # FASILITAS RS (snapshot per RS)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_fasilitas_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_fasilitas_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_fasilitas) AS id_fasilitas,
                TRIM(id_rs) AS id_rs,
                TRIM(id_jenis_fasilitas) AS id_jenis_fasilitas,
                COALESCE(
                    NULLIF(TRIM(nama_fasilitas), ''),
                    '-'
                ) AS nama_fasilitas,

                COALESCE(
                    CAST(NULLIF(TRIM(jumlah), '') AS UNSIGNED),
                    0
                ) AS jumlah,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_fasilitas_rs`

            WHERE
                id_fasilitas IS NOT NULL
                AND id_rs IS NOT NULL
                AND id_jenis_fasilitas IS NOT NULL;
            """,

            # =================================================
            # JENIS TENAGA MEDIS (perlu kelompok untuk kategori)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_jenis_tenaga_medis`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_jenis_tenaga_medis`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_jenis_tenaga_medis) AS id_jenis_tenaga_medis,
                TRIM(id_kelompok_tenaga_medis) AS id_kelompok_tenaga_medis,
                NULLIF(TRIM(nama_jenis_tenaga), '') AS nama_jenis_tenaga,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_jenis_tenaga_medis`

            WHERE
                id_jenis_tenaga_medis IS NOT NULL
                AND id_kelompok_tenaga_medis IS NOT NULL;
            """,

            # =================================================
            # TENAGA MEDIS (per RS x jenis)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_tenaga_medis`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_tenaga_medis`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_tenaga_medis) AS id_tenaga_medis,
                TRIM(id_rs) AS id_rs,
                TRIM(id_jenis_tenaga_medis) AS id_jenis_tenaga_medis,

                COALESCE(
                    CAST(NULLIF(TRIM(jumlah), '') AS UNSIGNED),
                    0
                ) AS jumlah,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_tenaga_medis`

            WHERE
                id_tenaga_medis IS NOT NULL
                AND id_rs IS NOT NULL
                AND id_jenis_tenaga_medis IS NOT NULL;
            """,

            # =================================================
            # PENYAKIT
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_penyakit`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_penyakit`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_penyakit) AS id_penyakit,
                TRIM(id_kategori_penyakit) AS id_kategori_penyakit,
                NULLIF(TRIM(nama_penyakit), '') AS nama_penyakit,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_penyakit`

            WHERE
                id_penyakit IS NOT NULL
                AND TRIM(nama_penyakit) <> '';
            """,

            # =================================================
            # PUSKESMAS
            # Asumsi kolom API: id_puskesmas, nama_puskesmas,
            # alamat, telepon, id_kabupaten_kota
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_puskesmas`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_puskesmas`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_puskesmas) AS id_puskesmas,
                TRIM(id_kabupaten_kota) AS id_kabupaten_kota,
                NULLIF(TRIM(nama_puskesmas), '') AS nama_puskesmas,
                NULLIF(TRIM(alamat), '') AS alamat,
                NULLIF(TRIM(telepon), '') AS telepon,
                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_puskesmas`

            WHERE
                id_puskesmas IS NOT NULL
                AND TRIM(nama_puskesmas) <> '';
            """,
        ]

        execute_sql(transformations)
        logging.info("Transform RS family kesehatan selesai.")

    # ========================================================
    # TASK 2C: TRANSFORM - PASIEN (validasi NIK & tanggal)
    # ========================================================
    # Hanya pasien, kecil. Depends on task 2B.

    @task
    def transform_pasien():

        logging.info("Memulai transform pasien...")

        etl_date = pendulum.now("Asia/Jakarta").to_date_string()

        transformations = [

            # =================================================
            # PASIEN (validasi NIK & tanggal lahir)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pasien`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pasien`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(id_pasien) AS id_pasien,

                CASE
                    WHEN LENGTH(
                        REGEXP_REPLACE(nik, '[^0-9]', '')
                    ) = 16
                        THEN REGEXP_REPLACE(nik, '[^0-9]', '')

                    WHEN LENGTH(
                        REGEXP_REPLACE(nik, '[^0-9]', '')
                    ) = 15
                        THEN CONCAT(
                            '0',
                            REGEXP_REPLACE(nik, '[^0-9]', '')
                        )

                    ELSE NULL
                END AS nik,

                CASE
                    WHEN UPPER(TRIM(jenis_kelamin)) IN
                        ('L', 'LAKI LAKI', 'LAKI-LAKI', 'PRIA')
                        THEN 'L'

                    WHEN UPPER(TRIM(jenis_kelamin)) IN
                        ('P', 'PEREMPUAN', 'WANITA')
                        THEN 'P'

                    ELSE NULL
                END AS jenis_kelamin,

                CASE
                    WHEN tanggal_lahir
                        REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                        AND tanggal_lahir <= '{etl_date}'
                        THEN tanggal_lahir
                    ELSE NULL
                END AS tanggal_lahir,

                sumber_database,
                waktu_ekstraksi

            FROM `{raw_db}`.`raw_pasien`

            WHERE id_pasien IS NOT NULL;
            """,
        ]

        execute_sql(transformations)
        logging.info("Transform pasien kesehatan selesai.")

    # ========================================================
    # TASK 2D: TRANSFORM - KASUS & REJECT (validasi + tracking)
    # ========================================================
    # Kasus penyakit dan reject table. Depends on task 2C (stg_pasien).

    @task
    def transform_kasus_reject():

        logging.info("Memulai transform kasus & reject...")

        etl_date = pendulum.now("Asia/Jakarta").to_date_string()

        transformations = [

            # =================================================
            # KASUS PENYAKIT RS (dengan validasi referensial)
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_kasus_penyakit_rs`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_kasus_penyakit_rs`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                TRIM(k.id_kasus) AS id_kasus,
                TRIM(k.id_rs) AS id_rs,
                TRIM(k.id_penyakit) AS id_penyakit,
                TRIM(k.id_pasien) AS id_pasien,
                k.tanggal_kasus,
                k.sumber_database,
                k.waktu_ekstraksi

            FROM `{raw_db}`.`raw_kasus_penyakit_rs` k

            INNER JOIN `{staging_db}`.`stg_rs` r
                ON TRIM(k.id_rs) = r.id_rs

            INNER JOIN `{staging_db}`.`stg_penyakit` p
                ON TRIM(k.id_penyakit) = p.id_penyakit

            INNER JOIN `{staging_db}`.`stg_pasien` s
                ON TRIM(k.id_pasien) = s.id_pasien

            WHERE
                k.id_kasus IS NOT NULL
                AND k.tanggal_kasus
                    REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                AND k.tanggal_kasus <= '{etl_date}';
            """,

            # =================================================
            # BARIS DITOLAK (STG_REJECT) - per endpoint
            # =================================================

            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_reject`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_reject`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                tabel_sumber VARCHAR(255) NOT NULL,
                id_baris BIGINT,
                alasan VARCHAR(255) NOT NULL,
                waktu_ekstraksi DATETIME
            )
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_0900_ai_ci;
            """,

            # Pasien: id kosong
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_pasien',
                r.id,
                'id_pasien kosong',
                r.waktu_ekstraksi
            FROM `{raw_db}`.`raw_pasien` r
            WHERE r.id_pasien IS NULL;
            """,

            # Pasien: NIK invalid
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_pasien',
                r.id,
                'NIK tidak valid (bukan 15/16 digit)',
                r.waktu_ekstraksi
            FROM `{raw_db}`.`raw_pasien` r
            WHERE r.id_pasien IS NOT NULL
              AND LENGTH(
                  REGEXP_REPLACE(COALESCE(r.nik, ''), '[^0-9]', '')
              ) NOT IN (15, 16);
            """,

            # Pasien: jenis kelamin tidak dikenal
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_pasien',
                r.id,
                'jenis kelamin tidak dikenal',
                r.waktu_ekstraksi
            FROM `{raw_db}`.`raw_pasien` r
            WHERE r.id_pasien IS NOT NULL
              AND UPPER(TRIM(r.jenis_kelamin)) NOT IN
                  ('L', 'LAKI LAKI', 'LAKI-LAKI', 'PRIA',
                   'P', 'PEREMPUAN', 'WANITA');
            """,

            # Pasien: tanggal lahir tidak valid
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_pasien',
                r.id,
                'tanggal_lahir tidak valid (format atau masa depan)',
                r.waktu_ekstraksi
            FROM `{raw_db}`.`raw_pasien` r
            WHERE r.id_pasien IS NOT NULL
              AND (
                  TRIM(r.tanggal_lahir)
                      NOT REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                  OR TRIM(r.tanggal_lahir) > '{etl_date}'
              );
            """,

            # Kasus: id kasus kosong
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_kasus_penyakit_rs',
                k.id,
                'id_kasus kosong',
                k.waktu_ekstraksi
            FROM `{raw_db}`.`raw_kasus_penyakit_rs` k
            WHERE k.id_kasus IS NULL;
            """,

            # Kasus: tanggal kasus tidak valid
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_kasus_penyakit_rs',
                k.id,
                'tanggal_kasus tidak valid (format atau masa depan)',
                k.waktu_ekstraksi
            FROM `{raw_db}`.`raw_kasus_penyakit_rs` k
            WHERE k.id_kasus IS NOT NULL
              AND (
                  TRIM(k.tanggal_kasus)
                      NOT REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
                  OR TRIM(k.tanggal_kasus) > '{etl_date}'
              );
            """,

            # Kasus: referensi tidak ditemukan
            f"""
            INSERT INTO `{staging_db}`.`stg_reject`
            (tabel_sumber, id_baris, alasan, waktu_ekstraksi)
            SELECT
                'raw_kasus_penyakit_rs',
                k.id,
                'referensi tidak ditemukan (rs / penyakit / pasien)',
                k.waktu_ekstraksi
            FROM `{raw_db}`.`raw_kasus_penyakit_rs` k
            WHERE k.id_kasus IS NOT NULL
              AND TRIM(k.tanggal_kasus)
                  REGEXP '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$'
              AND TRIM(k.tanggal_kasus) <= '{etl_date}'
              AND (
                  NOT EXISTS (
                      SELECT 1
                      FROM `{staging_db}`.`stg_rs` r
                      WHERE TRIM(k.id_rs) = r.id_rs
                  )
                  OR NOT EXISTS (
                      SELECT 1
                      FROM `{staging_db}`.`stg_penyakit` p
                      WHERE TRIM(k.id_penyakit) = p.id_penyakit
                  )
                  OR NOT EXISTS (
                      SELECT 1
                      FROM `{staging_db}`.`stg_pasien` s
                      WHERE TRIM(k.id_pasien) = s.id_pasien
                  )
              );
            """,
        ]

        execute_sql(transformations)

        # ------------------------------------------------
        # Log jumlah baris ditolak per alasan
        # ------------------------------------------------

        hook = get_mysql_hook()
        reject_conn = hook.get_conn()
        reject_cursor = reject_conn.cursor()

        try:
            reject_cursor.execute(
                f"""
                SELECT alasan, COUNT(*) AS jumlah
                FROM `{staging_db}`.`stg_reject`
                GROUP BY alasan
                ORDER BY jumlah DESC;
                """
            )
            for alasan, jumlah in reject_cursor.fetchall():
                logging.warning("Baris ditolak: %s (%s)", alasan, jumlah)
        finally:
            reject_cursor.close()
            reject_conn.close()

        logging.info("Transform kasus & reject kesehatan selesai.")

    # ========================================================
    # TASK 3: LOAD -> DATA WAREHOUSE
    # ========================================================
    # Membuat dimensi & fakta baru (tanpa membuat ulang dim_waktu /
    # dim_dukcapil_penduduk), memuat dimensi, lalu memuat fakta secara
    # idempoten (ON DUPLICATE KEY UPDATE).

    @task
    def load_to_dwh():

        logging.info("Membuat dimension dan fact kesehatan...")

        etl_date = pendulum.now("Asia/Jakarta").to_date_string()

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        # ------------------------------------------------
        # Sinkronisasi collation tabel lama yang sudah ada
        # (dim_waktu & dim_dukcapil_penduduk tidak dibuat ulang)
        # ------------------------------------------------

        existing_tables = ["dim_waktu", "dim_dukcapil_penduduk"]

        convert_statements = [align_collation]

        hook = get_mysql_hook()
        check_conn = hook.get_conn()
        check_cursor = check_conn.cursor()

        try:
            for table_name in existing_tables:
                check_cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_name = %s
                    """,
                    (dwh_db, table_name),
                )

                if check_cursor.fetchone()[0]:
                    convert_statements.append(
                        f"""
                        ALTER TABLE `{dwh_db}`.`{table_name}`
                        CONVERT TO CHARACTER SET utf8mb4
                        COLLATE utf8mb4_0900_ai_ci;
                        """
                    )
        finally:
            check_cursor.close()
            check_conn.close()

        execute_sql(convert_statements)

        # ====================================================
        # MIGRASI STRUKTUR LAMA -> STRUKTUR BARU
        # ====================================================
        # Struktur dim_kesehatan_tenaga_medis/fact_kesehatan_tenaga_medis berubah
        # (grain kelompok -> jenis) dan dim_kesehatan_fasilitas menambah
        # kolom nama_fasilitas. Tabel lama perlu di-drop dulu
        # sebelum dibuat ulang. Set MIGRASI_STRUKTUR_LAMA = False
        # setelah struktur baru berhasil dibuat pertama kali.

        if MIGRASI_STRUKTUR_LAMA:
            migration = [
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_tenaga_medis`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_kesehatan_tenaga_medis`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_fasilitas_rs`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_kesehatan_fasilitas`;",
            ]
            execute_sql(migration)
            logging.info(
                "Migrasi struktur: tabel tenaga medis & fasilitas "
                "versi lama telah di-drop."
            )

        # ====================================================
        # MIGRASI WILAYAH -> STRUKTUR BARU
        # ====================================================
        # dim_kesehatan_rs sekarang memakai wilayah_key, bukan kolom
        # wilayah inline. Semua fact yang memakai rs_key juga harus
        # di-drop terlebih dahulu agar tidak ada constraint yang menghambat.
        # Set MIGRASI_WILAYAH = False setelah berhasil berjalan pertama kali.

        if MIGRASI_WILAYAH:
            migration_wilayah = [
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_kasus_penyakit`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_layanan_rs`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_fasilitas_rs`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_tenaga_medis`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`fact_kesehatan_ketersediaan_fasilitas`;",
                f"DROP TABLE IF EXISTS `{dwh_db}`.`dim_kesehatan_rs`;",
            ]
            execute_sql(migration_wilayah)
            logging.info(
                "Migrasi wilayah: dim_kesehatan_rs dan fact terkait "
                "versi lama telah di-drop."
            )

        # ====================================================
        # DDL: DIMENSI & FAKTA
        # ====================================================

        create_tables = [

            # ---------------------------------------------
            # DIM WILAYAH (kab/kota + provinsi)
            # Sumber: stg_kabupaten_kota + stg_provinsi
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_wilayah`
            (
                wilayah_kesehatan_key INT AUTO_INCREMENT PRIMARY KEY,

                id_kabupaten_kota VARCHAR(10) NOT NULL,
                nama_kabupaten_kota VARCHAR(100),
                id_provinsi VARCHAR(10),
                nama_provinsi VARCHAR(100),

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_wilayah
                    (id_kabupaten_kota)
            );
            """,

            # ---------------------------------------------
            # DIM RS (Type 1)
            # Kolom wilayah diganti dengan wilayah_key (FK ke dim_kesehatan_wilayah)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_rs`
            (
                rs_key INT AUTO_INCREMENT PRIMARY KEY,

                id_rs VARCHAR(20) NOT NULL,
                nama_rs VARCHAR(150),
                alamat TEXT,
                telepon VARCHAR(50),
                latitude DECIMAL(10,7),
                longitude DECIMAL(10,7),

                id_kelas_rs VARCHAR(10),
                nama_kelas VARCHAR(30),
                id_jenis_rs VARCHAR(10),
                nama_jenis_rs VARCHAR(60),
                id_pemilik_rs VARCHAR(10),
                nama_pemilik VARCHAR(60),

                wilayah_key INT,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_rs
                    (id_rs),

                KEY idx_rs_wilayah (wilayah_key)
            );
            """,

            # ---------------------------------------------
            # DIM PUSKESMAS (Type 1)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_puskesmas`
            (
                puskesmas_key INT AUTO_INCREMENT PRIMARY KEY,

                id_puskesmas VARCHAR(20) NOT NULL,
                nama_puskesmas VARCHAR(150),
                alamat TEXT,
                telepon VARCHAR(50),

                wilayah_key INT,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_puskesmas
                    (id_puskesmas),

                KEY idx_pkm_wilayah (wilayah_key)
            );
            """,

            # ---------------------------------------------
            # DIM PENYAKIT (Type 1)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_penyakit`
            (
                penyakit_key INT AUTO_INCREMENT PRIMARY KEY,

                id_penyakit VARCHAR(20) NOT NULL,
                nama_penyakit VARCHAR(150),

                id_kategori_penyakit VARCHAR(20),
                nama_kategori VARCHAR(150),

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_penyakit
                    (id_penyakit)
            );
            """,

            # ---------------------------------------------
            # DIM KELOMPOK UMUR (statis)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_kelompok_umur`
            (
                kelompok_umur_key INT PRIMARY KEY,

                kelompok VARCHAR(20) NOT NULL,
                umur_min INT,
                umur_max INT,

                waktu_load DATETIME NOT NULL
            );
            """,

            # ---------------------------------------------
            # DIM LAYANAN (dari jenis-layanan-rs)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_layanan`
            (
                layanan_key INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_layanan_rs VARCHAR(20) NOT NULL,
                nama_layanan VARCHAR(150),

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_layanan
                    (id_jenis_layanan_rs)
            );
            """,

            # ---------------------------------------------
            # DIM FASILITAS (jenis + nama fasilitas)
            # UNIQUE: (id_jenis_fasilitas, nama_fasilitas)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_fasilitas`
            (
                fasilitas_key INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_fasilitas VARCHAR(20) NOT NULL,
                nama_jenis_fasilitas VARCHAR(150),
                nama_fasilitas VARCHAR(150),

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fasilitas
                    (id_jenis_fasilitas, nama_fasilitas)
            );
            """,

            # ---------------------------------------------
            # DIM TENAGA MEDIS (grain = jenis)
            # UNIQUE: id_jenis_tenaga_medis
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_tenaga_medis`
            (
                tenaga_key INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_tenaga_medis VARCHAR(20) NOT NULL,
                nama_jenis_tenaga VARCHAR(150),
                id_kelompok_tenaga_medis VARCHAR(20),
                nama_kelompok VARCHAR(100),
                kategori_profesi VARCHAR(30),

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_jenis_tenaga
                    (id_jenis_tenaga_medis)
            );
            """,

            # ---------------------------------------------
            # DIM KETERSEDIAAN FASILITAS (target rasio penduduk, statis)
            # RS       = 10.000 penduduk per 1 RS
            # Puskesmas = 30.000 penduduk per 1 Puskesmas
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_kesehatan_ketersediaan_fasilitas`
            (
                target_fasilitas_key INT AUTO_INCREMENT PRIMARY KEY,

                jenis_fasilitas VARCHAR(50) NOT NULL,
                rasio_penduduk INT NOT NULL,

                UNIQUE KEY uk_jenis_ketersediaan
                    (jenis_fasilitas)
            );
            """,

            # ---------------------------------------------
            # FACT KASUS PENYAKIT (grain: 1 kasus)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kesehatan_kasus_penyakit`
            (
                fact_kasus_key BIGINT AUTO_INCREMENT PRIMARY KEY,

                id_kasus VARCHAR(20) NOT NULL,
                waktu_key INT NOT NULL,

                rs_key INT,
                penyakit_key INT,
                penduduk_key BIGINT,
                kelompok_umur_key INT,

                umur INT,
                jumlah_kasus INT DEFAULT 1,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_kasus
                    (id_kasus),

                KEY idx_fk_waktu (waktu_key),
                KEY idx_fk_rs (rs_key),
                KEY idx_fk_penyakit (penyakit_key),
                KEY idx_fk_penduduk (penduduk_key)
            );
            """,

            # ---------------------------------------------
            # FACT LAYANAN RS (factless snapshot)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kesehatan_layanan_rs`
            (
                fact_layanan_key BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,
                rs_key INT,
                layanan_key INT,

                jumlah_layanan INT DEFAULT 1,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_layanan
                    (rs_key, layanan_key, waktu_key),

                KEY idx_fl_waktu (waktu_key)
            );
            """,

            # ---------------------------------------------
            # FACT FASILITAS RS (snapshot)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kesehatan_fasilitas_rs`
            (
                fact_fasilitas_key BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,
                rs_key INT,
                fasilitas_key INT,

                jumlah INT,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_fasilitas
                    (rs_key, fasilitas_key, waktu_key),

                KEY idx_ff_waktu (waktu_key)
            );
            """,

            # ---------------------------------------------
            # FACT TENAGA MEDIS (snapshot, grain = jenis per RS)
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kesehatan_tenaga_medis`
            (
                fact_tenaga_key BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,
                rs_key INT,
                tenaga_key INT,

                jumlah_tenaga INT,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_tenaga
                    (rs_key, tenaga_key, waktu_key),

                KEY idx_ft_waktu (waktu_key)
            );
            """,

            # ---------------------------------------------
            # FACT KETERSEDIAAN FASILITAS
            # grain: wilayah x waktu (snapshot per ETL date)
            # Menyimpan jumlah penduduk, RS aktual, dan
            # puskesmas aktual per kabupaten/kota.
            # ---------------------------------------------

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_kesehatan_ketersediaan_fasilitas`
            (
                fact_ketersediaan_key BIGINT AUTO_INCREMENT PRIMARY KEY,

                wilayah_kesehatan_key INT NOT NULL,
                waktu_key INT NOT NULL,

                jumlah_penduduk INT,
                jumlah_rs_aktual INT,
                jumlah_puskesmas_aktual INT,

                sumber_database VARCHAR(255),
                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_ketersediaan
                    (wilayah_kesehatan_key, waktu_key),

                KEY idx_fkt_waktu (waktu_key)
            );
            """,
        ]

        execute_sql(create_tables)

        metadata_columns = {
            "dim_waktu": ("waktu_load DATETIME",),
            "dim_kesehatan_wilayah": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "dim_kesehatan_rs": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "dim_kesehatan_puskesmas": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "dim_kesehatan_penyakit": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "dim_kesehatan_layanan": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "dim_kesehatan_fasilitas": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "dim_kesehatan_tenaga_medis": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "fact_kesehatan_kasus_penyakit": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "fact_kesehatan_layanan_rs": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "fact_kesehatan_fasilitas_rs": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "fact_kesehatan_tenaga_medis": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
            "fact_kesehatan_ketersediaan_fasilitas": (
                "sumber_database VARCHAR(255)",
                "waktu_load DATETIME",
            ),
        }

        metadata_migrations = []
        metadata_conn = hook.get_conn()
        metadata_cursor = metadata_conn.cursor()

        try:
            for table_name, columns in metadata_columns.items():
                metadata_cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                      AND table_name = %s
                    """,
                    (dwh_db, table_name),
                )

                if not metadata_cursor.fetchone()[0]:
                    continue

                metadata_cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = %s
                      AND table_name = %s
                    """,
                    (dwh_db, table_name),
                )
                existing_columns = {
                    row[0] for row in metadata_cursor.fetchall()
                }

                missing_columns = [
                    definition
                    for definition in columns
                    if definition.split()[0] not in existing_columns
                ]

                if missing_columns:
                    metadata_migrations.append(
                        f"""
                        ALTER TABLE `{dwh_db}`.`{table_name}`
                        ADD COLUMN {', ADD COLUMN '.join(missing_columns)};
                        """
                    )
        finally:
            metadata_cursor.close()
            metadata_conn.close()

        if metadata_migrations:
            execute_sql(metadata_migrations)
            logging.info(
                "Migrasi kolom sumber_database selesai untuk %d tabel.",
                len(metadata_migrations),
            )

        # ====================================================
        # POPULASI DIM_WAKTU (hanya baris yang belum ada)
        # ====================================================

        fill_dim_waktu = f"""
        INSERT IGNORE INTO `{dwh_db}`.`dim_waktu`
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
            ELT(
                MONTH(t.tanggal),
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ),
            QUARTER(t.tanggal),
            YEAR(t.tanggal),
            NOW()

        FROM
        (
            SELECT '{etl_date}' AS tanggal

            UNION

            SELECT DISTINCT tanggal_kasus
            FROM `{staging_db}`.`stg_kasus_penyakit_rs`
            WHERE tanggal_kasus IS NOT NULL
        ) t

        WHERE t.tanggal IS NOT NULL;
        """

        execute_sql([fill_dim_waktu])

        # ====================================================
        # LOAD DIMENSI
        # Urutan penting: dim_kesehatan_wilayah harus diisi
        # sebelum dim_kesehatan_rs dan dim_kesehatan_puskesmas
        # karena keduanya membutuhkan wilayah_kesehatan_key.
        # ====================================================

        load_dimensions = [

            # ---------------------------------------------
            # DIM WILAYAH (Type 1)
            # Harus diload pertama kali sebelum RS & puskesmas
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_wilayah`
            (
                id_kabupaten_kota, nama_kabupaten_kota,
                id_provinsi, nama_provinsi,
                sumber_database, waktu_load
            )

            SELECT
                kab.id_kabupaten_kota,
                kab.nama_kabupaten_kota,
                kab.id_provinsi,
                prov.nama_provinsi,
                kab.sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_kabupaten_kota` kab

            LEFT JOIN `{staging_db}`.`stg_provinsi` prov
                ON kab.id_provinsi = prov.id_provinsi

            ON DUPLICATE KEY UPDATE
                nama_kabupaten_kota = VALUES(nama_kabupaten_kota),
                id_provinsi         = VALUES(id_provinsi),
                nama_provinsi       = VALUES(nama_provinsi),
                sumber_database     = VALUES(sumber_database),
                waktu_load          = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM RS (Type 1, wilayah_key dari dim_kesehatan_wilayah)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_rs`
            (
                id_rs, nama_rs, alamat, telepon, latitude, longitude,
                id_kelas_rs, nama_kelas,
                id_jenis_rs, nama_jenis_rs,
                id_pemilik_rs, nama_pemilik,
                wilayah_key,
                sumber_database, waktu_load
            )

            SELECT
                s.id_rs,
                s.nama_rs,
                s.alamat,
                s.telepon,
                s.latitude,
                s.longitude,
                s.id_kelas_rs,
                s.nama_kelas,
                s.id_jenis_rs,
                s.nama_jenis_rs,
                s.id_pemilik_rs,
                s.nama_pemilik,
                w.wilayah_kesehatan_key,
                s.sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_rs_lengkap` s

            LEFT JOIN `{dwh_db}`.`dim_kesehatan_wilayah` w
                ON s.id_kabupaten_kota = w.id_kabupaten_kota

            ON DUPLICATE KEY UPDATE
                nama_rs       = VALUES(nama_rs),
                alamat        = VALUES(alamat),
                telepon       = VALUES(telepon),
                latitude      = VALUES(latitude),
                longitude     = VALUES(longitude),
                id_kelas_rs   = VALUES(id_kelas_rs),
                nama_kelas    = VALUES(nama_kelas),
                id_jenis_rs   = VALUES(id_jenis_rs),
                nama_jenis_rs = VALUES(nama_jenis_rs),
                id_pemilik_rs = VALUES(id_pemilik_rs),
                nama_pemilik  = VALUES(nama_pemilik),
                wilayah_key   = VALUES(wilayah_key),
                sumber_database = VALUES(sumber_database),
                waktu_load    = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM PUSKESMAS (Type 1)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_puskesmas`
            (
                id_puskesmas, nama_puskesmas, alamat, telepon,
                wilayah_key,
                sumber_database, waktu_load
            )

            SELECT
                p.id_puskesmas,
                p.nama_puskesmas,
                p.alamat,
                p.telepon,
                w.wilayah_kesehatan_key,
                p.sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_puskesmas` p

            LEFT JOIN `{dwh_db}`.`dim_kesehatan_wilayah` w
                ON p.id_kabupaten_kota = w.id_kabupaten_kota

            ON DUPLICATE KEY UPDATE
                nama_puskesmas  = VALUES(nama_puskesmas),
                alamat          = VALUES(alamat),
                telepon         = VALUES(telepon),
                wilayah_key     = VALUES(wilayah_key),
                sumber_database = VALUES(sumber_database),
                waktu_load      = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM PENYAKIT (Type 1)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_penyakit`
            (
                id_penyakit, nama_penyakit,
                id_kategori_penyakit, nama_kategori,
                sumber_database, waktu_load
            )

            SELECT
                p.id_penyakit,
                p.nama_penyakit,
                p.id_kategori_penyakit,
                k.nama_kategori,
                p.sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_penyakit` p

            LEFT JOIN `{staging_db}`.`stg_kategori_penyakit` k
                ON p.id_kategori_penyakit = k.id_kategori_penyakit

            ON DUPLICATE KEY UPDATE
                nama_penyakit        = VALUES(nama_penyakit),
                id_kategori_penyakit = VALUES(id_kategori_penyakit),
                nama_kategori        = VALUES(nama_kategori),
                sumber_database      = VALUES(sumber_database),
                waktu_load           = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM LAYANAN (Type 1)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_layanan`
            (
                id_jenis_layanan_rs, nama_layanan,
                sumber_database, waktu_load
            )

            SELECT
                id_jenis_layanan_rs,
                nama_layanan,
                sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_jenis_layanan_rs`

            ON DUPLICATE KEY UPDATE
                nama_layanan    = VALUES(nama_layanan),
                sumber_database = VALUES(sumber_database),
                waktu_load      = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM FASILITAS (Type 1)
            # Sumber: stg_fasilitas_rs (nama fasilitas) +
            #         stg_jenis_fasilitas_rs (nama jenis)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_fasilitas`
            (
                id_jenis_fasilitas, nama_jenis_fasilitas,
                nama_fasilitas,
                sumber_database, waktu_load
            )

            SELECT DISTINCT
                f.id_jenis_fasilitas,
                COALESCE(j.nama_jenis_fasilitas, 'TIDAK DIKETAHUI'),
                f.nama_fasilitas,
                f.sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_fasilitas_rs` f

            LEFT JOIN `{staging_db}`.`stg_jenis_fasilitas_rs` j
                ON f.id_jenis_fasilitas = j.id_jenis_fasilitas

            ON DUPLICATE KEY UPDATE
                nama_jenis_fasilitas = VALUES(nama_jenis_fasilitas),
                nama_fasilitas       = VALUES(nama_fasilitas),
                sumber_database      = VALUES(sumber_database),
                waktu_load           = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM TENAGA MEDIS (Type 1, grain = jenis)
            # KTM001-KTM006 = Dokter, KTM007 = Perawat
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_tenaga_medis`
            (
                id_jenis_tenaga_medis, nama_jenis_tenaga,
                id_kelompok_tenaga_medis, nama_kelompok,
                kategori_profesi,
                sumber_database, waktu_load
            )

            SELECT
                j.id_jenis_tenaga_medis,
                j.nama_jenis_tenaga,
                j.id_kelompok_tenaga_medis,
                k.nama_kelompok,

                CASE
                    WHEN j.id_kelompok_tenaga_medis IN
                        ('KTM001', 'KTM002', 'KTM003',
                         'KTM004', 'KTM005', 'KTM006')
                        THEN 'Dokter'

                    WHEN j.id_kelompok_tenaga_medis = 'KTM007'
                        THEN 'Perawat'

                    ELSE 'Lainnya'
                END AS kategori_profesi,

                j.sumber_database,
                NOW()

            FROM `{staging_db}`.`stg_jenis_tenaga_medis` j

            LEFT JOIN `{staging_db}`.`stg_kelompok_tenaga_medis` k
                ON j.id_kelompok_tenaga_medis =
                   k.id_kelompok_tenaga_medis

            ON DUPLICATE KEY UPDATE
                nama_jenis_tenaga        = VALUES(nama_jenis_tenaga),
                id_kelompok_tenaga_medis = VALUES(id_kelompok_tenaga_medis),
                nama_kelompok            = VALUES(nama_kelompok),
                kategori_profesi         = VALUES(kategori_profesi),
                sumber_database          = VALUES(sumber_database),
                waktu_load               = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # DIM KELOMPOK UMUR (statis, INSERT IGNORE)
            # ---------------------------------------------

            f"""
            INSERT IGNORE INTO `{dwh_db}`.`dim_kesehatan_kelompok_umur`
            (
                kelompok_umur_key, kelompok, umur_min, umur_max,
                waktu_load
            )
            VALUES
                (1, '0-4',     0,   4,   NOW()),
                (2, '5-14',    5,  14,   NOW()),
                (3, '15-24',  15,  24,   NOW()),
                (4, '25-44',  25,  44,   NOW()),
                (5, '45-59',  45,  59,   NOW()),
                (6, '60+',    60, 999,   NOW());
            """,

            # ---------------------------------------------
            # DIM KETERSEDIAAN FASILITAS (target rasio, statis)
            # Rumah Sakit  : 1 RS per 10.000 penduduk
            # Puskesmas    : 1 puskesmas per 30.000 penduduk
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_kesehatan_ketersediaan_fasilitas`
            (
                jenis_fasilitas, rasio_penduduk
            )
            VALUES
                ('Rumah Sakit', 10),
                ('Puskesmas',   30)
            ON DUPLICATE KEY UPDATE
                rasio_penduduk = VALUES(rasio_penduduk);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FAKTA
        # ====================================================

        load_facts = [

            # ---------------------------------------------
            # FACT KASUS PENYAKIT
            # grain: 1 kasus (id_kasus). Lookup gagal -> NULL.
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kesehatan_kasus_penyakit`
            (
                id_kasus, waktu_key,
                rs_key, penyakit_key, penduduk_key, kelompok_umur_key,
                umur, jumlah_kasus,
                sumber_database, waktu_load
            )

            SELECT
                c.id_kasus,

                CAST(DATE_FORMAT(c.tanggal_kasus, '%Y%m%d') AS UNSIGNED)
                    AS waktu_key,

                drs.rs_key        AS rs_key,
                dpy.penyakit_key  AS penyakit_key,
                dpd.penduduk_key  AS penduduk_key,

                CASE
                    WHEN c.umur IS NULL          THEN -1
                    WHEN c.umur BETWEEN 0 AND 4  THEN 1
                    WHEN c.umur BETWEEN 5 AND 14 THEN 2
                    WHEN c.umur BETWEEN 15 AND 24 THEN 3
                    WHEN c.umur BETWEEN 25 AND 44 THEN 4
                    WHEN c.umur BETWEEN 45 AND 59 THEN 5
                    WHEN c.umur >= 60             THEN 6
                    ELSE -1
                END AS kelompok_umur_key,

                c.umur,
                1 AS jumlah_kasus,
                c.sumber_database,
                NOW()

            FROM
            (
                SELECT
                    k.id_kasus,
                    k.id_rs,
                    k.id_penyakit,
                    k.tanggal_kasus,
                    k.sumber_database,
                    s.nik,

                    CASE
                        WHEN s.tanggal_lahir IS NULL THEN NULL
                        WHEN k.tanggal_kasus < s.tanggal_lahir THEN NULL
                        ELSE TIMESTAMPDIFF(
                            YEAR,
                            s.tanggal_lahir,
                            k.tanggal_kasus
                        )
                    END AS umur

                FROM `{staging_db}`.`stg_kasus_penyakit_rs` k

                JOIN `{staging_db}`.`stg_pasien` s
                    ON k.id_pasien = s.id_pasien
            ) c

            LEFT JOIN `{dwh_db}`.`dim_kesehatan_rs` drs
                ON c.id_rs = drs.id_rs

            LEFT JOIN `{dwh_db}`.`dim_kesehatan_penyakit` dpy
                ON c.id_penyakit = dpy.id_penyakit

            LEFT JOIN `{dwh_db}`.`dim_dukcapil_penduduk` dpd
                ON c.nik = dpd.nik

            ON DUPLICATE KEY UPDATE
                waktu_key         = VALUES(waktu_key),
                penyakit_key      = VALUES(penyakit_key),
                penduduk_key      = VALUES(penduduk_key),
                kelompok_umur_key = VALUES(kelompok_umur_key),
                umur              = VALUES(umur),
                jumlah_kasus      = VALUES(jumlah_kasus),
                sumber_database   = VALUES(sumber_database),
                waktu_load        = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # FACT LAYANAN RS (factless snapshot, jumlah = 1)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kesehatan_layanan_rs`
            (
                waktu_key, rs_key, layanan_key,
                jumlah_layanan,
                sumber_database, waktu_load
            )

            SELECT
                CAST(DATE_FORMAT('{etl_date}', '%Y%m%d') AS UNSIGNED),
                drs.rs_key,
                dl.layanan_key,
                1,
                l.sumber_database,
                NOW()

            FROM
            (
                SELECT DISTINCT
                    id_rs,
                    id_jenis_layanan_rs,
                    sumber_database
                FROM `{staging_db}`.`stg_layanan_rs`
            ) l

            LEFT JOIN `{dwh_db}`.`dim_kesehatan_rs` drs
                ON l.id_rs = drs.id_rs

            LEFT JOIN `{dwh_db}`.`dim_kesehatan_layanan` dl
                ON l.id_jenis_layanan_rs = dl.id_jenis_layanan_rs

            ON DUPLICATE KEY UPDATE
                jumlah_layanan  = VALUES(jumlah_layanan),
                rs_key          = VALUES(rs_key),
                layanan_key     = VALUES(layanan_key),
                sumber_database = VALUES(sumber_database),
                waktu_load      = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # FACT FASILITAS RS (snapshot, agregasi jumlah)
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kesehatan_fasilitas_rs`
            (
                waktu_key, rs_key, fasilitas_key,
                jumlah,
                sumber_database, waktu_load
            )

            SELECT
                a.waktu_key,
                a.rs_key,
                a.fasilitas_key,
                a.jumlah,
                a.sumber_database,
                NOW()

            FROM
            (
                SELECT
                    CAST(DATE_FORMAT('{etl_date}', '%Y%m%d') AS UNSIGNED)
                        AS waktu_key,
                    drs.rs_key      AS rs_key,
                    df.fasilitas_key AS fasilitas_key,
                    SUM(f.jumlah)   AS jumlah,
                    MAX(f.sumber_database) AS sumber_database

                FROM `{staging_db}`.`stg_fasilitas_rs` f

                LEFT JOIN `{dwh_db}`.`dim_kesehatan_rs` drs
                    ON f.id_rs = drs.id_rs

                LEFT JOIN `{dwh_db}`.`dim_kesehatan_fasilitas` df
                    ON f.id_jenis_fasilitas = df.id_jenis_fasilitas
                    AND f.nama_fasilitas    = df.nama_fasilitas

                GROUP BY waktu_key, rs_key, fasilitas_key
            ) a

            ON DUPLICATE KEY UPDATE
                jumlah          = VALUES(jumlah),
                rs_key          = VALUES(rs_key),
                fasilitas_key   = VALUES(fasilitas_key),
                sumber_database = VALUES(sumber_database),
                waktu_load      = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # FACT TENAGA MEDIS (snapshot, grain = jenis per RS)
            # Agregasi SUM(jumlah) per (rs, jenis tenaga).
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kesehatan_tenaga_medis`
            (
                waktu_key, rs_key, tenaga_key,
                jumlah_tenaga,
                sumber_database, waktu_load
            )

            SELECT
                a.waktu_key,
                a.rs_key,
                a.tenaga_key,
                a.jumlah_tenaga,
                a.sumber_database,
                NOW()

            FROM
            (
                SELECT
                    CAST(DATE_FORMAT('{etl_date}', '%Y%m%d') AS UNSIGNED)
                        AS waktu_key,
                    drs.rs_key    AS rs_key,
                    dt.tenaga_key AS tenaga_key,
                    SUM(t.jumlah) AS jumlah_tenaga,
                    MAX(t.sumber_database) AS sumber_database

                FROM `{staging_db}`.`stg_tenaga_medis` t

                LEFT JOIN `{dwh_db}`.`dim_kesehatan_rs` drs
                    ON t.id_rs = drs.id_rs

                LEFT JOIN `{dwh_db}`.`dim_kesehatan_tenaga_medis` dt
                    ON t.id_jenis_tenaga_medis =
                       dt.id_jenis_tenaga_medis

                GROUP BY waktu_key, rs_key, tenaga_key
            ) a

            ON DUPLICATE KEY UPDATE
                jumlah_tenaga   = VALUES(jumlah_tenaga),
                rs_key          = VALUES(rs_key),
                tenaga_key      = VALUES(tenaga_key),
                sumber_database = VALUES(sumber_database),
                waktu_load      = VALUES(waktu_load);
            """,

            # ---------------------------------------------
            # FACT KETERSEDIAAN FASILITAS
            # grain: wilayah x waktu (snapshot per ETL date)
            #
            # jumlah_penduduk   -> COUNT(DISTINCT nik) per kab/kota
            #                      dari data kependudukan (dukcapil)
            # jumlah_rs_aktual  -> COUNT(DISTINCT id_rs) per kab/kota
            #                      dari stg_rs
            # jumlah_puskesmas  -> COUNT(DISTINCT id_puskesmas) per kab/kota
            #                      dari stg_puskesmas
            # ---------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`fact_kesehatan_ketersediaan_fasilitas`
            (
                wilayah_kesehatan_key, waktu_key,
                jumlah_penduduk, jumlah_rs_aktual, jumlah_puskesmas_aktual,
                sumber_database, waktu_load
            )

            SELECT
                w.wilayah_kesehatan_key,
                CAST(DATE_FORMAT('{etl_date}', '%Y%m%d') AS UNSIGNED)
                    AS waktu_key,
                COALESCE(pd.jumlah_penduduk,    0) AS jumlah_penduduk,
                COALESCE(rs.jumlah_rs,          0) AS jumlah_rs_aktual,
                COALESCE(pk.jumlah_puskesmas,   0) AS jumlah_puskesmas_aktual,
                w.sumber_database,
                NOW()

            FROM `{dwh_db}`.`dim_kesehatan_wilayah` w

            -- Jumlah penduduk per kab/kota dari pipeline dukcapil
            LEFT JOIN
            (
                SELECT
                    sk.id_kabupaten_kota,
                    COUNT(DISTINCT sp.nik) AS jumlah_penduduk
                FROM `{staging_db}`.`stg_penduduk` AS sp
                JOIN `{staging_db}`.`stg_alamat` AS sa
                    ON sp.id_alamat = sa.id_alamat
                JOIN `{staging_db}`.`stg_desa` AS sd
                    ON sa.id_desa = sd.id_desa
                JOIN `{staging_db}`.`stg_kecamatan` AS sk
                    ON sd.id_kecamatan = sk.id_kecamatan
                GROUP BY sk.id_kabupaten_kota
            ) pd
                ON pd.id_kabupaten_kota = w.id_kabupaten_kota

            -- Jumlah RS aktual per kab/kota
            LEFT JOIN
            (
                SELECT
                    id_kabupaten_kota,
                    COUNT(DISTINCT id_rs) AS jumlah_rs
                FROM `{staging_db}`.`stg_rs`
                GROUP BY id_kabupaten_kota
            ) rs
                ON rs.id_kabupaten_kota = w.id_kabupaten_kota

            -- Jumlah puskesmas aktual per kab/kota
            LEFT JOIN
            (
                SELECT
                    id_kabupaten_kota,
                    COUNT(DISTINCT id_puskesmas) AS jumlah_puskesmas
                FROM `{staging_db}`.`stg_puskesmas`
                GROUP BY id_kabupaten_kota
            ) pk
                ON pk.id_kabupaten_kota = w.id_kabupaten_kota

            ON DUPLICATE KEY UPDATE
                jumlah_penduduk         = VALUES(jumlah_penduduk),
                jumlah_rs_aktual        = VALUES(jumlah_rs_aktual),
                jumlah_puskesmas_aktual = VALUES(jumlah_puskesmas_aktual),
                sumber_database         = VALUES(sumber_database),
                waktu_load              = VALUES(waktu_load);
            """,
        ]

        execute_sql(load_facts)

        logging.info("Load ke Data Warehouse kesehatan selesai.")

    # ========================================================
    # WIRING (urutan: extract >> basic >> rs >> pasien >> kasus >> load)
    # ========================================================

    t1  = extract_to_raw()
    t2a = transform_dimension_basic()
    t2b = transform_rs_family()
    t2c = transform_pasien()
    t2d = transform_kasus_reject()
    t3  = load_to_dwh()

    # Sequential: extract -> basic -> rs -> pasien -> kasus -> load
    t1 >> t2a >> t2b >> t2c >> t2d >> t3

    return t3