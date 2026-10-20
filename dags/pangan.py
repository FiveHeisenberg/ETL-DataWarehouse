from __future__ import annotations

import logging
from datetime import date, timedelta

import pendulum
import requests

from airflow.sdk import task


# ============================================================
# KONFIGURASI DOMAIN PANGAN
# ============================================================

# nama pendek -> endpoint API (tabel sumber: tb_<nama>)
# raw table      : raw_pangan_<nama>
# staging table  : stg_pangan_<nama>
SOURCE_ENDPOINTS = {
    "provinsi":               "/provinsi",
    "kabupaten_kota":         "/kabupaten-kota",
    "satuan":                 "/satuan",
    "kategori_komoditas":     "/kategori-komoditas",
    "komoditas":              "/komoditas",
    "jenis_lahan":            "/jenis-lahan",
    "luas_lahan":             "/luas-lahan",
    "produksi_pertanian":     "/produksi-pertanian",
    "kelompok_tani":          "/kelompok-tani",
    "petani":                 "/petani",
    "jenis_ternak":           "/jenis-ternak",
    "jenis_produk_ternak":    "/jenis-produk-ternak",
    "populasi_ternak":        "/populasi-ternak",
    "produksi_peternakan":    "/produksi-peternakan",
    "harga":                  "/harga-pangan",
    "ketersediaan":           "/ketersediaan-pangan",
    "jenis_perikanan":        "/jenis-perikanan",
    "jenis_ikan":             "/jenis-ikan",
    "produksi_perikanan":     "/produksi-perikanan",
}

NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

# staging table + ekspresi tahun, dipakai untuk menentukan rentang dim_waktu
WAKTU_SOURCES = [
    ("stg_pangan_luas_lahan",          "tahun"),
    ("stg_pangan_produksi_pertanian",  "tahun"),
    ("stg_pangan_petani",              "tahun_data"),
    ("stg_pangan_populasi_ternak",     "tahun"),
    ("stg_pangan_produksi_peternakan", "tahun"),
    ("stg_pangan_harga",               "YEAR(tanggal)"),
    ("stg_pangan_ketersediaan",        "tahun"),
    ("stg_pangan_produksi_perikanan",  "tahun"),
]


# ============================================================
# HELPER EKSPRESI SQL (cleansing + standardisasi)
#
# Semua konversi tipe dibungkus CASE + REGEXP agar nilai yang
# tidak valid menjadi NULL (lalu ditolak di tahap validasi),
# bukan menyebabkan error saat CAST.
# ============================================================

def _txt(col):
    """Teks: TRIM, string kosong -> NULL."""
    return "NULLIF(TRIM(%s), '')" % col


def _int(col):
    """Bilangan bulat non-negatif, selain itu NULL."""
    return (
        "CASE WHEN TRIM(%s) REGEXP '^[0-9]+$' "
        "THEN CAST(TRIM(%s) AS UNSIGNED) END" % (col, col)
    )


def _dec(col, precision):
    """Desimal non-negatif, selain itu NULL."""
    return (
        "CASE WHEN TRIM(%s) REGEXP '^[0-9]+([.][0-9]+)?$' "
        "THEN CAST(TRIM(%s) AS DECIMAL(%s)) END" % (col, col, precision)
    )


def _date(col):
    """Tanggal format YYYY-MM-DD yang benar-benar ada di kalender
    (30 Februari dsb. -> NULL), selain itu NULL.

    CASE dibuat bertingkat agar pemeriksaan hari-dalam-bulan hanya
    dievaluasi jika format sudah lolos; STR_TO_DATE pada tanggal yang
    tidak ada akan error di strict mode."""
    return (
        "CASE WHEN TRIM(%(c)s) REGEXP "
        "'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$' "
        "THEN CASE WHEN CAST(SUBSTR(TRIM(%(c)s), 9, 2) AS UNSIGNED) "
        "<= DAY(LAST_DAY(CONCAT(SUBSTR(TRIM(%(c)s), 1, 7), '-01'))) "
        "THEN STR_TO_DATE(TRIM(%(c)s), '%%Y-%%m-%%d') END END" % {"c": col}
    )


def _code2(col):
    """Kode wilayah numerik -> teks 2 digit ('1' -> '01'),
    disamakan dengan id_kabupaten_kota di dim_wilayah_penduduk."""
    return (
        "CASE WHEN TRIM(%s) REGEXP '^[0-9]+$' "
        "THEN IF(CHAR_LENGTH(TRIM(%s)) < 2, LPAD(TRIM(%s), 2, '0'), TRIM(%s)) "
        "END" % (col, col, col, col)
    )


def _nik(col):
    """NIK: buang karakter non-angka, wajib 16 digit."""
    return (
        "CASE WHEN CHAR_LENGTH(REGEXP_REPLACE(%s, '[^0-9]', '')) = 16 "
        "THEN REGEXP_REPLACE(%s, '[^0-9]', '') END" % (col, col)
    )


def _enum(col, values):
    """Standarisasi nilai kategori (tidak peka huruf besar/kecil);
    nilai di luar daftar -> NULL."""
    whens = " ".join(
        "WHEN '%s' THEN '%s'" % (v.upper(), v) for v in values
    )
    return "CASE UPPER(TRIM(%s)) %s END" % (col, whens)


def _nn(*cols):
    """Validasi: kolom wajib terisi."""
    return " AND ".join("x.`%s` IS NOT NULL" % c for c in cols)


def _yr(col):
    """Validasi: tahun wajar."""
    return "x.`%s` BETWEEN 2000 AND YEAR(CURDATE()) + 1" % col


# ============================================================
# PIPELINE PANGAN
# ============================================================

def create_pangan_tasks(
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

        # Kolom yang distandarisasi kapitalisasinya (Title Case)
        title_case_columns = {
            "nama_provinsi",
            "nama_kabupaten_kota",
            "nama_satuan",
            "nama_kategori",
            "nama_komoditas",
            "nama_jenis_lahan",
            "nama_kelompok",
            "nama_jenis_ternak",
            "nama_produk",
            "nama_jenis_perikanan",
            "nama_ikan",
        }

        try:

            for name, endpoint in SOURCE_ENDPOINTS.items():

                raw_table = f"raw_pangan_{name}"

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

                                # TERAPKAN TITLE CASE
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
                    name,
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
    #
    # Pola tiap tabel staging:
    #   subquery  : cleansing + standardisasi (ekspresi _txt/_int/...)
    #   WHERE     : validasi (kolom wajib, rentang tahun, nilai > 0, dst.)
    #   DISTINCT  : buang duplikat
    # ========================================================

    def _make_staging(name, cols, where):

        inner = ",\n                ".join(
            f"{expr} AS `{alias}`" for alias, expr in cols
        )
        outer = ", ".join(f"x.`{alias}`" for alias, _ in cols)

        return [
            f"""
            DROP TABLE IF EXISTS
            `{staging_db}`.`stg_pangan_{name}`;
            """,

            f"""
            CREATE TABLE `{staging_db}`.`stg_pangan_{name}`
            (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY
            ) AS

            SELECT DISTINCT
                {outer},
                x.sumber_database,
                x.waktu_ekstraksi

            FROM
            (
                SELECT
                {inner},
                sumber_database,
                waktu_ekstraksi

                FROM `{raw_db}`.`raw_pangan_{name}`
            ) x

            WHERE
                {where};
            """,
        ]

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

        specs = [

            # =================================================
            # MASTER WILAYAH
            # =================================================

            ("provinsi", [
                ("id_provinsi", _code2("id_provinsi")),
                ("nama_provinsi", _txt("nama_provinsi")),
            ], _nn("id_provinsi", "nama_provinsi")),

            ("kabupaten_kota", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_provinsi", _code2("id_provinsi")),
                ("nama_kabupaten_kota", _txt("nama_kabupaten_kota")),
            ], _nn("id_kabupaten_kota", "id_provinsi",
                   "nama_kabupaten_kota")),

            # =================================================
            # MASTER LAINNYA
            # =================================================

            ("satuan", [
                ("id_satuan", _int("id_satuan")),
                ("nama_satuan", _txt("nama_satuan")),
                ("simbol", _txt("simbol")),
            ], _nn("id_satuan", "nama_satuan", "simbol")),

            ("kategori_komoditas", [
                ("id_kategori_komoditas", _int("id_kategori_komoditas")),
                ("nama_kategori", _txt("nama_kategori")),
                ("subsektor", _enum("subsektor", [
                    "Pertanian", "Peternakan", "Pangan", "Perikanan"])),
            ], _nn("id_kategori_komoditas", "nama_kategori", "subsektor")),

            ("komoditas", [
                ("id_komoditas", _int("id_komoditas")),
                ("id_kategori_komoditas", _int("id_kategori_komoditas")),
                ("nama_komoditas", _txt("nama_komoditas")),
            ], _nn("id_komoditas", "id_kategori_komoditas",
                   "nama_komoditas")),

            ("jenis_lahan", [
                ("id_jenis_lahan", _int("id_jenis_lahan")),
                ("nama_jenis_lahan", _txt("nama_jenis_lahan")),
            ], _nn("id_jenis_lahan", "nama_jenis_lahan")),

            ("jenis_ternak", [
                ("id_jenis_ternak", _int("id_jenis_ternak")),
                ("nama_jenis_ternak", _txt("nama_jenis_ternak")),
                ("kelompok_ternak", _enum("kelompok_ternak", [
                    "Ternak Besar", "Ternak Kecil", "Unggas"])),
            ], _nn("id_jenis_ternak", "nama_jenis_ternak",
                   "kelompok_ternak")),

            ("jenis_produk_ternak", [
                ("id_jenis_produk", _int("id_jenis_produk")),
                ("nama_produk", _txt("nama_produk")),
                ("id_satuan", _int("id_satuan")),
            ], _nn("id_jenis_produk", "nama_produk", "id_satuan")),

            ("jenis_perikanan", [
                ("id_jenis_perikanan", _int("id_jenis_perikanan")),
                ("nama_jenis_perikanan", _txt("nama_jenis_perikanan")),
                ("kategori", _enum("kategori", ["Tangkap", "Budidaya"])),
            ], _nn("id_jenis_perikanan", "nama_jenis_perikanan",
                   "kategori")),

            ("jenis_ikan", [
                ("id_jenis_ikan", _int("id_jenis_ikan")),
                ("nama_ikan", _txt("nama_ikan")),
            ], _nn("id_jenis_ikan", "nama_ikan")),

            ("kelompok_tani", [
                ("id_kelompok_tani", _int("id_kelompok_tani")),
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("nama_kelompok", _txt("nama_kelompok")),
                ("tipe_kelompok", _enum("tipe_kelompok", [
                    "Poktan", "Gapoktan"])),
            ], _nn("id_kelompok_tani", "id_kabupaten_kota",
                   "nama_kelompok", "tipe_kelompok")),

            # =================================================
            # PETANI
            # Validasi NIK 16 digit, status, tahun
            # =================================================

            ("petani", [
                ("nik", _nik("nik")),
                ("id_kelompok_tani", _int("id_kelompok_tani")),
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_komoditas", _int("id_komoditas")),
                ("status_petani", _enum("status_petani", [
                    "Pemilik", "Penggarap", "Buruh Tani"])),
                ("tahun_data", _int("tahun_data")),
            ], _nn("nik", "id_kabupaten_kota", "status_petani",
                   "tahun_data") + " AND " + _yr("tahun_data")),

            # =================================================
            # PERTANIAN
            # =================================================

            ("luas_lahan", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_jenis_lahan", _int("id_jenis_lahan")),
                ("tahun", _int("tahun")),
                ("luas_ha", _dec("luas_ha", "12,2")),
            ], _nn("id_kabupaten_kota", "id_jenis_lahan", "tahun",
                   "luas_ha") + " AND " + _yr("tahun")),

            ("produksi_pertanian", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_komoditas", _int("id_komoditas")),
                ("tahun", _int("tahun")),
                ("luas_tanam_ha", _dec("luas_tanam_ha", "12,2")),
                ("luas_panen_ha", _dec("luas_panen_ha", "12,2")),
                ("produksi_ton", _dec("produksi_ton", "14,2")),
            ], _nn("id_kabupaten_kota", "id_komoditas", "tahun",
                   "luas_tanam_ha", "luas_panen_ha",
                   "produksi_ton") + " AND " + _yr("tahun")),

            # =================================================
            # PETERNAKAN
            # =================================================

            ("populasi_ternak", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_jenis_ternak", _int("id_jenis_ternak")),
                ("tahun", _int("tahun")),
                ("jumlah_ekor", _int("jumlah_ekor")),
            ], _nn("id_kabupaten_kota", "id_jenis_ternak", "tahun",
                   "jumlah_ekor") + " AND " + _yr("tahun")),

            ("produksi_peternakan", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_jenis_ternak", _int("id_jenis_ternak")),
                ("id_jenis_produk", _int("id_jenis_produk")),
                ("tahun", _int("tahun")),
                ("jumlah_produksi_ton",
                 _dec("jumlah_produksi_ton", "14,2")),
            ], _nn("id_kabupaten_kota", "id_jenis_ternak",
                   "id_jenis_produk", "tahun",
                   "jumlah_produksi_ton") + " AND " + _yr("tahun")),

            # =================================================
            # PANGAN
            # Harga: tanggal tidak boleh di masa depan, harga > 0
            # Ketersediaan: bulan 1-12
            # =================================================

            ("harga", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_komoditas", _int("id_komoditas")),
                ("id_satuan", _int("id_satuan")),
                ("tanggal", _date("tanggal")),
                ("harga", _dec("harga", "12,2")),
            ], _nn("id_kabupaten_kota", "id_komoditas", "id_satuan",
                   "tanggal", "harga")
               + " AND x.`tanggal` BETWEEN '2000-01-01' AND CURDATE()"
               + " AND x.`harga` > 0"),

            ("ketersediaan", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_komoditas", _int("id_komoditas")),
                ("tahun", _int("tahun")),
                ("bulan", _int("bulan")),
                ("produksi_ton", _dec("produksi_ton", "14,2")),
                ("stok_ton", _dec("stok_ton", "14,2")),
                ("kebutuhan_ton", _dec("kebutuhan_ton", "14,2")),
            ], _nn("id_kabupaten_kota", "id_komoditas", "tahun", "bulan",
                   "produksi_ton", "stok_ton", "kebutuhan_ton")
               + " AND " + _yr("tahun")
               + " AND x.`bulan` BETWEEN 1 AND 12"),

            # =================================================
            # PERIKANAN
            # nilai_produksi_rp boleh kosong
            # =================================================

            ("produksi_perikanan", [
                ("id_kabupaten_kota", _code2("id_kabupaten_kota")),
                ("id_jenis_perikanan", _int("id_jenis_perikanan")),
                ("id_jenis_ikan", _int("id_jenis_ikan")),
                ("tahun", _int("tahun")),
                ("volume_ton", _dec("volume_ton", "14,2")),
                ("nilai_produksi_rp", _dec("nilai_produksi_rp", "18,2")),
            ], _nn("id_kabupaten_kota", "id_jenis_perikanan",
                   "id_jenis_ikan", "tahun", "volume_ton")
               + " AND " + _yr("tahun")),
        ]

        transformations = []
        for name, cols, where in specs:
            transformations += _make_staging(name, cols, where)

        execute_sql(
            [align_collation] + transformations
        )

        # --------------------------------------------------------
        # Ringkasan validasi: raw vs staging
        # (selisih = baris ditolak validasi atau duplikat)
        # --------------------------------------------------------

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            for name in SOURCE_ENDPOINTS:
                cursor.execute(
                    f"SELECT COUNT(*) FROM "
                    f"`{raw_db}`.`raw_pangan_{name}`"
                )
                n_raw = cursor.fetchone()[0]

                cursor.execute(
                    f"SELECT COUNT(*) FROM "
                    f"`{staging_db}`.`stg_pangan_{name}`"
                )
                n_stg = cursor.fetchone()[0]

                if n_stg < n_raw:
                    logging.warning(
                        "Validasi %s: raw=%d, staging=%d, "
                        "ditolak/duplikat=%d",
                        name,
                        n_raw,
                        n_stg,
                        n_raw - n_stg,
                    )
                else:
                    logging.info(
                        "Validasi %s: raw=%d, staging=%d",
                        name,
                        n_raw,
                        n_stg,
                    )
        finally:
            cursor.close()
            conn.close()

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
            "dim_dukcapil_penduduk",
            "dim_pangan_wilayah",
            "dim_pangan_komoditas",
            "dim_pangan_jenis_lahan",
            "dim_pangan_jenis_ternak",
            "dim_pangan_jenis_produk_ternak",
            "dim_pangan_kelompok_tani",
            "dim_pangan_jenis_perikanan",
            "dim_pangan_jenis_ikan",
            "fact_pangan_luas_lahan",
            "fact_pangan_produksi_pertanian",
            "fact_pangan_petani",
            "fact_pangan_populasi_ternak",
            "fact_pangan_produksi_peternakan",
            "fact_pangan_harga",
            "fact_pangan_ketersediaan",
            "fact_pangan_produksi_perikanan",
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
        # CREATE TABLE
        # ====================================================

        create_tables = [

            # =================================================
            # DIM WAKTU (bersama, sudah ada dari ETL Dukcapil)
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
            # DIM PENDUDUK (bersama, dari ETL Dukcapil)
            # Dibuat jika belum ada agar fact petani tetap bisa
            # dimuat; penduduk_key terisi setelah DAG Dukcapil jalan.
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_dukcapil_penduduk`
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
            # DIM WILAYAH PANGAN
            # 1 baris = 1 kabupaten/kota
            # id_kabupaten_kota '01'-'23' sama dengan
            # dim_wilayah_penduduk (kunci join lintas domain)
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_wilayah`
            (
                wilayah_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kabupaten_kota VARCHAR(10)
                    NOT NULL,

                nama_kabupaten_kota VARCHAR(100),

                id_provinsi VARCHAR(10),

                nama_provinsi VARCHAR(100),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_wilayah
                    (id_kabupaten_kota)
            );
            """,

            # =================================================
            # DIM KOMODITAS
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_komoditas`
            (
                komoditas_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_komoditas INT NOT NULL,

                nama_komoditas VARCHAR(100),

                id_kategori_komoditas INT,

                nama_kategori VARCHAR(50),

                subsektor VARCHAR(20),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_komoditas
                    (id_komoditas)
            );
            """,

            # =================================================
            # DIM JENIS LAHAN
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_jenis_lahan`
            (
                jenis_lahan_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_lahan INT NOT NULL,

                nama_jenis_lahan VARCHAR(50),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_jenis_lahan
                    (id_jenis_lahan)
            );
            """,

            # =================================================
            # DIM JENIS TERNAK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_jenis_ternak`
            (
                jenis_ternak_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_ternak INT NOT NULL,

                nama_jenis_ternak VARCHAR(50),

                kelompok_ternak VARCHAR(20),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_jenis_ternak
                    (id_jenis_ternak)
            );
            """,

            # =================================================
            # DIM JENIS PRODUK TERNAK
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_jenis_produk_ternak`
            (
                jenis_produk_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_produk INT NOT NULL,

                nama_produk VARCHAR(50),

                satuan VARCHAR(10),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_jenis_produk
                    (id_jenis_produk)
            );
            """,

            # =================================================
            # DIM KELOMPOK TANI
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_kelompok_tani`
            (
                kelompok_tani_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_kelompok_tani INT NOT NULL,

                wilayah_key INT,

                nama_kelompok VARCHAR(150),

                tipe_kelompok VARCHAR(10),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_kelompok_tani
                    (id_kelompok_tani),

                KEY idx_kelompok_tani_wilayah
                    (wilayah_key)
            );
            """,

            # =================================================
            # DIM JENIS PERIKANAN
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_jenis_perikanan`
            (
                jenis_perikanan_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_perikanan INT NOT NULL,

                nama_jenis_perikanan VARCHAR(50),

                kategori VARCHAR(10),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_jenis_perikanan
                    (id_jenis_perikanan)
            );
            """,

            # =================================================
            # DIM JENIS IKAN
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`dim_pangan_jenis_ikan`
            (
                jenis_ikan_key
                    INT AUTO_INCREMENT PRIMARY KEY,

                id_jenis_ikan INT NOT NULL,

                nama_ikan VARCHAR(100),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_pangan_jenis_ikan
                    (id_jenis_ikan)
            );
            """,

            # =================================================
            # FACT LUAS LAHAN
            # Grain: kab/kota x jenis lahan x tahun
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_luas_lahan`
            (
                luas_lahan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                jenis_lahan_key INT NOT NULL,

                luas_ha DECIMAL(12,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_luas_lahan
                (
                    waktu_key,
                    wilayah_key,
                    jenis_lahan_key
                ),

                KEY idx_fact_luas_lahan_wilayah
                    (wilayah_key),

                KEY idx_fact_luas_lahan_jenis
                    (jenis_lahan_key)
            );
            """,

            # =================================================
            # FACT PRODUKSI PERTANIAN
            # Grain: kab/kota x komoditas x tahun
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_produksi_pertanian`
            (
                produksi_pertanian_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                komoditas_key INT NOT NULL,

                luas_tanam_ha DECIMAL(12,2),

                luas_panen_ha DECIMAL(12,2),

                produksi_ton DECIMAL(14,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_produksi_pertanian
                (
                    waktu_key,
                    wilayah_key,
                    komoditas_key
                ),

                KEY idx_fact_produksi_pertanian_wilayah
                    (wilayah_key),

                KEY idx_fact_produksi_pertanian_komoditas
                    (komoditas_key)
            );
            """,

            # =================================================
            # FACT PETANI
            # Grain: 1 petani (NIK) per tahun data
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_petani`
            (
                petani_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                penduduk_key BIGINT NULL,

                kelompok_tani_key INT NULL,

                komoditas_key INT NULL,

                nik VARCHAR(16) NOT NULL,

                status_petani VARCHAR(10),

                jumlah_petani INT
                    DEFAULT 1,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_petani
                (
                    nik,
                    waktu_key
                ),

                KEY idx_fact_petani_wilayah
                    (wilayah_key),

                KEY idx_fact_petani_penduduk
                    (penduduk_key),

                KEY idx_fact_petani_kelompok
                    (kelompok_tani_key)
            );
            """,

            # =================================================
            # FACT POPULASI TERNAK
            # Grain: kab/kota x jenis ternak x tahun
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_populasi_ternak`
            (
                populasi_ternak_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                jenis_ternak_key INT NOT NULL,

                jumlah_ekor INT,

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_populasi_ternak
                (
                    waktu_key,
                    wilayah_key,
                    jenis_ternak_key
                ),

                KEY idx_fact_populasi_ternak_wilayah
                    (wilayah_key),

                KEY idx_fact_populasi_ternak_jenis
                    (jenis_ternak_key)
            );
            """,

            # =================================================
            # FACT PRODUKSI PETERNAKAN
            # Grain: kab/kota x jenis ternak x jenis produk x tahun
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_produksi_peternakan`
            (
                produksi_peternakan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                jenis_ternak_key INT NOT NULL,

                jenis_produk_key INT NOT NULL,

                jumlah_produksi_ton DECIMAL(14,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_produksi_peternakan
                (
                    waktu_key,
                    wilayah_key,
                    jenis_ternak_key,
                    jenis_produk_key
                ),

                KEY idx_fact_produksi_peternakan_wilayah
                    (wilayah_key),

                KEY idx_fact_produksi_peternakan_ternak
                    (jenis_ternak_key),

                KEY idx_fact_produksi_peternakan_produk
                    (jenis_produk_key)
            );
            """,

            # =================================================
            # FACT HARGA
            # Grain: kab/kota x komoditas x tanggal
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_harga`
            (
                harga_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                komoditas_key INT NOT NULL,

                satuan VARCHAR(10),

                harga DECIMAL(12,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_harga
                (
                    waktu_key,
                    wilayah_key,
                    komoditas_key
                ),

                KEY idx_fact_harga_komoditas_waktu
                (
                    komoditas_key,
                    waktu_key
                ),

                KEY idx_fact_harga_wilayah
                    (wilayah_key)
            );
            """,

            # =================================================
            # FACT KETERSEDIAAN
            # Grain: kab/kota x komoditas x bulan
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_ketersediaan`
            (
                ketersediaan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                komoditas_key INT NOT NULL,

                produksi_ton DECIMAL(14,2),

                stok_ton DECIMAL(14,2),

                kebutuhan_ton DECIMAL(14,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_ketersediaan
                (
                    waktu_key,
                    wilayah_key,
                    komoditas_key
                ),

                KEY idx_fact_ketersediaan_wilayah
                    (wilayah_key),

                KEY idx_fact_ketersediaan_komoditas
                    (komoditas_key)
            );
            """,

            # =================================================
            # FACT PRODUKSI PERIKANAN
            # Grain: kab/kota x jenis perikanan x jenis ikan x tahun
            # =================================================

            f"""
            CREATE TABLE IF NOT EXISTS
            `{dwh_db}`.`fact_pangan_produksi_perikanan`
            (
                produksi_perikanan_key
                    BIGINT AUTO_INCREMENT PRIMARY KEY,

                waktu_key INT NOT NULL,

                wilayah_key INT NOT NULL,

                jenis_perikanan_key INT NOT NULL,

                jenis_ikan_key INT NOT NULL,

                volume_ton DECIMAL(14,2),

                nilai_produksi_rp DECIMAL(18,2),

                sumber_database VARCHAR(100),

                waktu_load DATETIME NOT NULL,

                UNIQUE KEY uk_fact_produksi_perikanan
                (
                    waktu_key,
                    wilayah_key,
                    jenis_perikanan_key,
                    jenis_ikan_key
                ),

                KEY idx_fact_produksi_perikanan_wilayah
                    (wilayah_key),

                KEY idx_fact_produksi_perikanan_jenis
                    (jenis_perikanan_key),

                KEY idx_fact_produksi_perikanan_ikan
                    (jenis_ikan_key)
            );
            """,
        ]

        execute_sql(create_tables)

        # ====================================================
        # DIM WAKTU
        #
        # Melengkapi kalender harian dari tahun terkecil sampai
        # tahun terbesar di data (minimal tahun berjalan + 1).
        # INSERT IGNORE: baris yang sudah ada (dari ETL
        # Dukcapil) tidak diubah.
        #
        # Kunci waktu di fact:
        #   tahunan : yyyy0101
        #   bulanan : yyyymm01
        #   harian  : yyyymmdd
        # ====================================================

        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            now = pendulum.now("Asia/Jakarta")
            years = [now.year]

            for stg_table, expr in WAKTU_SOURCES:
                cursor.execute(
                    f"SELECT MIN({expr}), MAX({expr}) "
                    f"FROM `{staging_db}`.`{stg_table}`"
                )
                lo, hi = cursor.fetchone()
                years += [int(v) for v in (lo, hi) if v is not None]

            start = date(min(years), 1, 1)
            end = date(max(years) + 1, 12, 31)

            now_str = now.to_datetime_string()

            rows = []
            d = start
            while d <= end:
                rows.append(
                    (
                        int(d.strftime("%Y%m%d")),
                        d,
                        d.day,
                        d.month,
                        NAMA_BULAN[d.month - 1],
                        (d.month - 1) // 3 + 1,
                        d.year,
                        now_str,
                    )
                )
                d += timedelta(days=1)

            sql_waktu = (
                f"INSERT IGNORE INTO `{dwh_db}`.`dim_waktu` "
                f"(waktu_key, tanggal, hari, bulan, nama_bulan, "
                f"kuartal, tahun, waktu_load) "
                f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )

            for i in range(0, len(rows), 1000):
                cursor.executemany(sql_waktu, rows[i : i + 1000])

            conn.commit()

            logging.info(
                "dim_waktu dilengkapi: %s s.d. %s",
                start,
                end,
            )

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

        # ====================================================
        # LOAD DIMENSION
        # ====================================================

        load_dimensions = [

            # -----------------------------------------------
            # DIM WILAYAH PANGAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_wilayah`
            (
                id_kabupaten_kota,
                nama_kabupaten_kota,
                id_provinsi,
                nama_provinsi,
                sumber_database,
                waktu_load
            )

            SELECT
                kab.id_kabupaten_kota,
                kab.nama_kabupaten_kota,
                kab.id_provinsi,
                prov.nama_provinsi,
                kab.sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_kabupaten_kota` kab

            LEFT JOIN
                `{staging_db}`.`stg_pangan_provinsi` prov
                ON kab.id_provinsi =
                   prov.id_provinsi

            ON DUPLICATE KEY UPDATE

                nama_kabupaten_kota =
                    VALUES(nama_kabupaten_kota),

                id_provinsi =
                    VALUES(id_provinsi),

                nama_provinsi =
                    VALUES(nama_provinsi),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM KOMODITAS
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_komoditas`
            (
                id_komoditas,
                nama_komoditas,
                id_kategori_komoditas,
                nama_kategori,
                subsektor,
                sumber_database,
                waktu_load
            )

            SELECT
                k.id_komoditas,
                k.nama_komoditas,
                k.id_kategori_komoditas,
                c.nama_kategori,
                c.subsektor,
                k.sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_komoditas` k

            LEFT JOIN
                `{staging_db}`.`stg_pangan_kategori_komoditas` c
                ON k.id_kategori_komoditas =
                   c.id_kategori_komoditas

            ON DUPLICATE KEY UPDATE

                nama_komoditas =
                    VALUES(nama_komoditas),

                id_kategori_komoditas =
                    VALUES(id_kategori_komoditas),

                nama_kategori =
                    VALUES(nama_kategori),

                subsektor =
                    VALUES(subsektor),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM JENIS LAHAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_jenis_lahan`
            (
                id_jenis_lahan,
                nama_jenis_lahan,
                sumber_database,
                waktu_load
            )

            SELECT
                id_jenis_lahan,
                nama_jenis_lahan,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_jenis_lahan`

            ON DUPLICATE KEY UPDATE

                nama_jenis_lahan =
                    VALUES(nama_jenis_lahan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM JENIS TERNAK
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_jenis_ternak`
            (
                id_jenis_ternak,
                nama_jenis_ternak,
                kelompok_ternak,
                sumber_database,
                waktu_load
            )

            SELECT
                id_jenis_ternak,
                nama_jenis_ternak,
                kelompok_ternak,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_jenis_ternak`

            ON DUPLICATE KEY UPDATE

                nama_jenis_ternak =
                    VALUES(nama_jenis_ternak),

                kelompok_ternak =
                    VALUES(kelompok_ternak),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM JENIS PRODUK TERNAK
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_jenis_produk_ternak`
            (
                id_jenis_produk,
                nama_produk,
                satuan,
                sumber_database,
                waktu_load
            )

            SELECT
                p.id_jenis_produk,
                p.nama_produk,
                s.simbol,
                p.sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_jenis_produk_ternak` p

            LEFT JOIN
                `{staging_db}`.`stg_pangan_satuan` s
                ON p.id_satuan =
                   s.id_satuan

            ON DUPLICATE KEY UPDATE

                nama_produk =
                    VALUES(nama_produk),

                satuan =
                    VALUES(satuan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM KELOMPOK TANI
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_kelompok_tani`
            (
                id_kelompok_tani,
                wilayah_key,
                nama_kelompok,
                tipe_kelompok,
                sumber_database,
                waktu_load
            )

            SELECT
                kt.id_kelompok_tani,
                w.wilayah_key,
                kt.nama_kelompok,
                kt.tipe_kelompok,
                kt.sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_kelompok_tani` kt

            INNER JOIN
                `{dwh_db}`.`dim_pangan_wilayah` w
                ON kt.id_kabupaten_kota =
                   w.id_kabupaten_kota

            ON DUPLICATE KEY UPDATE

                wilayah_key =
                    VALUES(wilayah_key),

                nama_kelompok =
                    VALUES(nama_kelompok),

                tipe_kelompok =
                    VALUES(tipe_kelompok),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM JENIS PERIKANAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_jenis_perikanan`
            (
                id_jenis_perikanan,
                nama_jenis_perikanan,
                kategori,
                sumber_database,
                waktu_load
            )

            SELECT
                id_jenis_perikanan,
                nama_jenis_perikanan,
                kategori,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_jenis_perikanan`

            ON DUPLICATE KEY UPDATE

                nama_jenis_perikanan =
                    VALUES(nama_jenis_perikanan),

                kategori =
                    VALUES(kategori),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,

            # -----------------------------------------------
            # DIM JENIS IKAN
            # -----------------------------------------------

            f"""
            INSERT INTO `{dwh_db}`.`dim_pangan_jenis_ikan`
            (
                id_jenis_ikan,
                nama_ikan,
                sumber_database,
                waktu_load
            )

            SELECT
                id_jenis_ikan,
                nama_ikan,
                sumber_database,
                NOW()

            FROM
                `{staging_db}`.`stg_pangan_jenis_ikan`

            ON DUPLICATE KEY UPDATE

                nama_ikan =
                    VALUES(nama_ikan),

                sumber_database =
                    VALUES(sumber_database),

                waktu_load =
                    VALUES(waktu_load);
            """,
        ]

        execute_sql(load_dimensions)

        # ====================================================
        # LOAD FACT
        #
        # INNER JOIN ke dimensi wajib (wilayah, komoditas, jenis,
        # dim_waktu): baris yang rujukannya tidak ada ditolak.
        # Pengecualian fact petani: LEFT JOIN ke penduduk,
        # kelompok tani, dan komoditas agar petani yang NIK-nya
        # belum ada di dim_dukcapil_penduduk tetap termuat
        # (penduduk_key = NULL).
        # ====================================================

        wilayah_join = f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_wilayah` w
                ON s.id_kabupaten_kota = w.id_kabupaten_kota
        """

        def waktu_join(expr):
            return f"""
            INNER JOIN `{dwh_db}`.`dim_waktu` t
                ON t.waktu_key = {expr}
            """

        def load_fact(table, stg, insert_cols, select_exprs,
                      joins, update_cols):

            ins = ", ".join(insert_cols + ["sumber_database", "waktu_load"])
            sel = ", ".join(select_exprs + ["s.sumber_database", "NOW()"])
            upd = ",\n                ".join(
                f"{c} = VALUES({c})"
                for c in update_cols + ["sumber_database", "waktu_load"]
            )

            return f"""
            INSERT INTO `{dwh_db}`.`{table}`
            (
                {ins}
            )

            SELECT
                {sel}

            FROM
                `{staging_db}`.`{stg}` s

            {joins}

            ON DUPLICATE KEY UPDATE
                {upd};
            """

        annual = "s.tahun * 10000 + 101"
        monthly = "s.tahun * 10000 + s.bulan * 100 + 1"
        daily = "CAST(DATE_FORMAT(s.tanggal, '%Y%m%d') AS UNSIGNED)"

        fact_specs = [

            ("fact_pangan_luas_lahan", "stg_pangan_luas_lahan",
             ["waktu_key", "wilayah_key", "jenis_lahan_key", "luas_ha"],
             [annual, "w.wilayah_key", "jl.jenis_lahan_key", "s.luas_ha"],
             wilayah_join + waktu_join(annual) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_jenis_lahan` jl
                ON s.id_jenis_lahan = jl.id_jenis_lahan
            """,
             ["luas_ha"]),

            ("fact_pangan_produksi_pertanian",
             "stg_pangan_produksi_pertanian",
             ["waktu_key", "wilayah_key", "komoditas_key",
              "luas_tanam_ha", "luas_panen_ha", "produksi_ton"],
             [annual, "w.wilayah_key", "k.komoditas_key",
              "s.luas_tanam_ha", "s.luas_panen_ha", "s.produksi_ton"],
             wilayah_join + waktu_join(annual) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_komoditas` k
                ON s.id_komoditas = k.id_komoditas
            """,
             ["luas_tanam_ha", "luas_panen_ha", "produksi_ton"]),

            ("fact_pangan_petani", "stg_pangan_petani",
             ["waktu_key", "wilayah_key", "penduduk_key",
              "kelompok_tani_key", "komoditas_key", "nik",
              "status_petani", "jumlah_petani"],
             ["s.tahun_data * 10000 + 101", "w.wilayah_key",
              "dp.penduduk_key", "kt.kelompok_tani_key",
              "k.komoditas_key", "s.nik", "s.status_petani", "1"],
             wilayah_join + waktu_join("s.tahun_data * 10000 + 101") + f"""
            LEFT JOIN `{dwh_db}`.`dim_dukcapil_penduduk` dp
                ON s.nik = dp.nik
            LEFT JOIN `{dwh_db}`.`dim_pangan_kelompok_tani` kt
                ON s.id_kelompok_tani = kt.id_kelompok_tani
            LEFT JOIN `{dwh_db}`.`dim_pangan_komoditas` k
                ON s.id_komoditas = k.id_komoditas
            """,
             ["wilayah_key", "penduduk_key", "kelompok_tani_key",
              "komoditas_key", "status_petani", "jumlah_petani"]),

            ("fact_pangan_populasi_ternak", "stg_pangan_populasi_ternak",
             ["waktu_key", "wilayah_key", "jenis_ternak_key",
              "jumlah_ekor"],
             [annual, "w.wilayah_key", "jt.jenis_ternak_key",
              "s.jumlah_ekor"],
             wilayah_join + waktu_join(annual) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_jenis_ternak` jt
                ON s.id_jenis_ternak = jt.id_jenis_ternak
            """,
             ["jumlah_ekor"]),

            ("fact_pangan_produksi_peternakan",
             "stg_pangan_produksi_peternakan",
             ["waktu_key", "wilayah_key", "jenis_ternak_key",
              "jenis_produk_key", "jumlah_produksi_ton"],
             [annual, "w.wilayah_key", "jt.jenis_ternak_key",
              "jp.jenis_produk_key", "s.jumlah_produksi_ton"],
             wilayah_join + waktu_join(annual) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_jenis_ternak` jt
                ON s.id_jenis_ternak = jt.id_jenis_ternak
            INNER JOIN `{dwh_db}`.`dim_pangan_jenis_produk_ternak` jp
                ON s.id_jenis_produk = jp.id_jenis_produk
            """,
             ["jumlah_produksi_ton"]),

            ("fact_pangan_harga", "stg_pangan_harga",
             ["waktu_key", "wilayah_key", "komoditas_key", "satuan",
              "harga"],
             [daily, "w.wilayah_key", "k.komoditas_key", "sat.simbol",
              "s.harga"],
             wilayah_join + waktu_join(daily) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_komoditas` k
                ON s.id_komoditas = k.id_komoditas
            LEFT JOIN `{staging_db}`.`stg_pangan_satuan` sat
                ON s.id_satuan = sat.id_satuan
            """,
             ["satuan", "harga"]),

            ("fact_pangan_ketersediaan", "stg_pangan_ketersediaan",
             ["waktu_key", "wilayah_key", "komoditas_key",
              "produksi_ton", "stok_ton", "kebutuhan_ton"],
             [monthly, "w.wilayah_key", "k.komoditas_key",
              "s.produksi_ton", "s.stok_ton", "s.kebutuhan_ton"],
             wilayah_join + waktu_join(monthly) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_komoditas` k
                ON s.id_komoditas = k.id_komoditas
            """,
             ["produksi_ton", "stok_ton", "kebutuhan_ton"]),

            ("fact_pangan_produksi_perikanan",
             "stg_pangan_produksi_perikanan",
             ["waktu_key", "wilayah_key", "jenis_perikanan_key",
              "jenis_ikan_key", "volume_ton", "nilai_produksi_rp"],
             [annual, "w.wilayah_key", "jp.jenis_perikanan_key",
              "ji.jenis_ikan_key", "s.volume_ton", "s.nilai_produksi_rp"],
             wilayah_join + waktu_join(annual) + f"""
            INNER JOIN `{dwh_db}`.`dim_pangan_jenis_perikanan` jp
                ON s.id_jenis_perikanan = jp.id_jenis_perikanan
            INNER JOIN `{dwh_db}`.`dim_pangan_jenis_ikan` ji
                ON s.id_jenis_ikan = ji.id_jenis_ikan
            """,
             ["volume_ton", "nilai_produksi_rp"]),
        ]

        load_facts = [
            load_fact(table, stg, ins, sel, joins, upd)
            for table, stg, ins, sel, joins, upd in fact_specs
        ]

        execute_sql(load_facts)

        # --------------------------------------------------------
        # Ringkasan load: staging vs fact
        # (fact < staging = ada baris yang rujukan dimensinya tidak
        #  ditemukan, atau duplikat pada kunci unik)
        # --------------------------------------------------------

        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            for table, stg, *_ in fact_specs:
                cursor.execute(
                    f"SELECT COUNT(*) FROM `{staging_db}`.`{stg}`"
                )
                n_stg = cursor.fetchone()[0]

                cursor.execute(
                    f"SELECT COUNT(*) FROM `{dwh_db}`.`{table}`"
                )
                n_fact = cursor.fetchone()[0]

                if n_fact < n_stg:
                    logging.warning(
                        "Load %s: staging=%d, fact=%d, selisih=%d",
                        table,
                        n_stg,
                        n_fact,
                        n_stg - n_fact,
                    )
                else:
                    logging.info(
                        "Load %s: staging=%d, fact=%d",
                        table,
                        n_stg,
                        n_fact,
                    )

            cursor.execute(
                f"SELECT COUNT(*) FROM `{dwh_db}`.`fact_pangan_petani` "
                f"WHERE penduduk_key IS NULL"
            )
            n_null = cursor.fetchone()[0]

            if n_null:
                logging.warning(
                    "fact_pangan_petani: %d petani belum ditemukan di "
                    "dim_dukcapil_penduduk (penduduk_key NULL). "
                    "Jalankan ETL Dukcapil lalu ulangi load.",
                    n_null,
                )
        finally:
            cursor.close()
            conn.close()

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