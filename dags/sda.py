from __future__ import annotations

import logging
import math
import re
from datetime import datetime, date

import pendulum
import requests

from airflow.sdk import task

SOURCE_NAME = "sda"
SOURCE_DB = "db_sda_lingkungan"

SOURCE_ENDPOINTS = {
    "wilayah": "/wilayah",
    "fasilitas_sampah": "/fasilitas-sampah",
    "perusahaan": "/perusahaan",
    "stasiun_pantau": "/stasiun-pantau",
    "izin_lingkungan": "/izin-lingkungan",
    "kualitas_air_sungai": "/kualitas-air-sungai",
    "kualitas_udara": "/kualitas-udara",
    "timbulan_sampah": "/timbulan-sampah",
    "tutupan_lahan_rth": "/tutupan-lahan-rth",
}

TABLE_NAME_MAP = {
    "wilayah": "raw_sda_wilayah",
    "fasilitas_sampah": "raw_sda_fasilitas_sampah",
    "perusahaan": "raw_sda_perusahaan",
    "stasiun_pantau": "raw_sda_stasiun_pantau",
    "izin_lingkungan": "raw_sda_izin_lingkungan",
    "kualitas_air_sungai": "raw_sda_kualitas_air_sungai",
    "kualitas_udara": "raw_sda_kualitas_udara",
    "timbulan_sampah": "raw_sda_timbulan_sampah",
    "tutupan_lahan_rth": "raw_sda_tutupan_lahan_rth",
}

# HELPER: TITLE CASE / PROPER CASE DENGAN AKRONIM RESMI
OFFICIAL_ACRONYMS = {
    "tpa", "tps", "3r", "pt", "cv", "ud", "rth", "das", "pdam",
    "b3", "amdal", "ukl", "upl", "ukl-upl", "ukl upl", "spp", "spp-l"
}

def proper_case(text: str) -> str:
    if not text or not isinstance(text, str):
        return text
    text = text.strip()
    if not text:
        return text
    words = text.split()
    result = []
    for word in words:
        word_lower = word.lower()
        word_clean = word_lower.strip(".,;:()-")
        if word_clean in OFFICIAL_ACRONYMS:
            if word_clean == "3r":
                result.append("3R")
            elif word_clean == "upl":
                result.append("UPL")
            elif word_clean == "ukl-upl" or word_clean == "ukl upl":
                result.append("UKL-UPL")
            elif word_clean == "ukl":
                result.append("UKL")
            elif word_clean == "spp":
                result.append("SPP")
            elif word_clean == "spp-l":
                result.append("SPP-L")
            else:
                result.append(word_clean.upper())
        else:
            if word:
                result.append(word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper())
            else:
                result.append(word)
    return " ".join(result)

def clean_and_title(text: str) -> str:
    if not text or not isinstance(text, str):
        return None
    text = text.strip()
    if not text:
        return None
    return proper_case(text)

def log_cleansing_metrics(table_name: str, metrics: dict):
    msg_parts = [f"Cleansing {table_name}:"]
    for key, value in metrics.items():
        msg_parts.append(f"{key}={value}")
    logging.info(" | ".join(msg_parts))

def create_proper_case_expr(column: str, alias: str = None, metrics_var: str = None) -> str:
    return f"proper_case({column})"

def create_mysql_proper_case(column: str) -> str:
    return f"CONCAT(UPPER(SUBSTRING(TRIM({column}), 1, 1)), LOWER(SUBSTRING(TRIM({column}), 2)))"

def create_mysql_proper_case_multiword(column: str) -> str:
    return f"""
        TRIM(
            REPLACE(
                REPLACE(
                    REPLACE(
                        CONCAT(
                            UPPER(SUBSTRING(TRIM({column}), 1, 1)),
                            LOWER(SUBSTRING(TRIM({column}), 2))
                        ),
                        ' tpa ', ' TPA '
                    ),
                    ' tps 3r ', ' TPS 3R '
                ),
                ' 3r ', ' 3R '
            )
        """

def apply_title_case_in_python(records: list, name_fields: list, metrics: dict) -> list:
    if not records:
        return records
    cleaned = []
    case_fixed = 0
    null_count = 0
    for rec in records:
        new_rec = rec.copy()
        for field in name_fields:
            if field in new_rec and new_rec[field] is not None:
                original = str(new_rec[field]).strip()
                if original:
                    cleaned_val = proper_case(original)
                    if cleaned_val != original:
                        case_fixed += 1
                    new_rec[field] = cleaned_val
                else:
                    new_rec[field] = None
                    null_count += 1
        cleaned.append(new_rec)
    metrics["case_fixed"] = metrics.get("case_fixed", 0) + case_fixed
    metrics["null_count"] = metrics.get("null_count", 0) + null_count
    return cleaned

def create_mysql_trim_expr(column: str) -> str:
    return f"TRIM({column})"

def create_mysql_nullif_expr(column: str) -> str:
    return f"NULLIF(TRIM({column}), '')"

def create_mysql_proper_case_with_acronyms(column: str) -> str:
    expr = f"""
    TRIM(
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        REPLACE(
                                            CONCAT(
                                                UPPER(SUBSTRING(TRIM({column}), 1, 1)),
                                                LOWER(SUBSTRING(TRIM({column}), 2))
                                            ),
                                            ' Tpa ', ' TPA '
                                        ),
                                        ' Tps 3r ', ' TPS 3R '
                                    ),
                                    ' 3r ', ' 3R '
                                ),
                                ' Pt ', ' PT '
                            ),
                            ' Cv ', ' CV '
                        ),
                        ' Ud ', ' UD '
                    ),
                    ' Rth ', ' RTH '
                ),
                ' Das ', ' DAS '
            ),
            ' Pdam ', ' PDAM '
        ),
        ' B3 ', ' B3 '
    )
    """
    return expr.strip()

def create_mysql_case_when_nullif(column: str, empty_to_null: bool = True) -> str:
    if empty_to_null:
        return f"NULLIF(TRIM({column}), '')"
    return f"TRIM({column})"

def log_cleansing_summary(table_name: str, stage: str, total_records: int, metrics: dict):
    parts = [f"[{stage}] {table_name}: total={total_records}"]
    for k, v in metrics.items():
        parts.append(f"{k}={v}")
    logging.info(" | ".join(parts))

def create_mysql_numeric_safe_cast(column: str, target_type: str, min_val: float = None, max_val: float = None) -> str:
    conditions = [f"{column} REGEXP '^-?[0-9]+\\.?[0-9]*$'"]
    if min_val is not None:
        conditions.append(f"CAST({column} AS {target_type}) >= {min_val}")
    if max_val is not None:
        conditions.append(f"CAST({column} AS {target_type}) <= {max_val}")
    where_clause = " AND ".join(conditions)
    return f"""
    CASE
        WHEN {where_clause}
        THEN CAST({column} AS {target_type})
        ELSE NULL
    END
    """.strip()

# PROCESSING FUNCTIONS UNTUK STAGING
def process_staging_table(cursor, conn, raw_db, staging_db, table_cfg, raw_db_name, source_db):
    table_name = table_cfg["name"]
    raw_table = table_cfg["raw_table"]
    insert_cols = table_cfg["insert_cols"]
    raw_cols = table_cfg["raw_cols"]
    name_fields = table_cfg.get("name_fields", [])
    where_clause = table_cfg.get("where_clause", "")
    distinct = table_cfg.get("distinct", True)
    processors = table_cfg.get("processors", {})
    stg_id = table_cfg["stg_id"]

    logging.info(f"Transform: {table_name} ...")

    cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`{table_name}`;")
    cursor.execute(table_cfg["create_sql"])
    conn.commit()

    select_cols = ", ".join([f"`{c}`" for c in raw_cols])
    distinct_kw = "DISTINCT " if distinct else ""
    sql = f"""
    SELECT {distinct_kw}{select_cols}
    FROM `{raw_db_name}`.`{raw_table}`
    {where_clause}
    """

    cursor.execute(sql)
    raw_rows = cursor.fetchall()

    if not raw_rows:
        logging.warning(f"Tidak ada data dari {raw_table}, skip.")
        return

    col_names = [desc[0] for desc in cursor.description]
    metrics = {"total_raw": len(raw_rows), "null_count": 0, "case_fixed": 0, "invalid_numeric": 0, "invalid_gps": 0, "invalid_date": 0}
    cleaned_rows = []

    for row in raw_rows:
        rec = dict(zip(col_names, row))
        for field, processor in processors.items():
            if field in rec:
                original = rec[field]
                try:
                    rec[field] = processor(original)
                    if original is not None and rec[field] is None:
                        metrics["invalid_numeric"] = metrics.get("invalid_numeric", 0) + 1
                    elif field in ["koordinat_gps"] and original is not None and rec[field] is None:
                        metrics["invalid_gps"] = metrics.get("invalid_gps", 0) + 1
                    elif field in ["tanggal_terbit", "waktu_pengambilan", "waktu_pengukuran", "tanggal_lapor", "tanggal_citra", "tanggal_terbit"] and original is not None and rec[field] is None:
                        metrics["invalid_date"] = metrics.get("invalid_date", 0) + 1
                except Exception as e:
                    logging.warning(f"Processor error for {field}: {e}")
                    rec[field] = None

        for field in name_fields:
            if field in rec and rec[field] is not None:
                original = str(rec[field]).strip()
                if original:
                    cleaned = proper_case(original)
                    if cleaned != original:
                        metrics["case_fixed"] = metrics.get("case_fixed", 0) + 1
                    rec[field] = cleaned
                else:
                    rec[field] = None
                    metrics["null_count"] = metrics.get("null_count", 0) + 1

        for col in raw_cols:
            if col in rec and isinstance(rec[col], str):
                val = rec[col].strip()
                if not val:
                    rec[col] = None
                    metrics["null_count"] = metrics.get("null_count", 0) + 1
                else:
                    rec[col] = val

        insert_row = []
        for col in insert_cols:
            insert_row.append(rec.get(col))
        cleaned_rows.append(insert_row)

    if cleaned_rows:
        placeholders = ", ".join(["%s"] * len(insert_cols))
        insert_cols_str = ", ".join([f"`{c}`" for c in insert_cols])
        insert_sql = f"INSERT INTO `{staging_db}`.`{table_name}` ({', '.join([f'`{c}`' for c in insert_cols])}) VALUES ({placeholders})"

        batch_size = 1000
        total_inserted = 0
        for i in range(0, len(cleaned_rows), batch_size):
            batch = cleaned_rows[i:i + batch_size]
            cursor.executemany(
                f"INSERT INTO `{staging_db}`.`{table_name}` ({', '.join([f'`{c}`' for c in insert_cols])}) VALUES ({placeholders})",
                batch
            )
            total_inserted += len(batch)

        conn.commit()

        log_cleansing_summary(
            table_name,
            "STAGING",
            metrics["total_raw"],
            {
                "inserted": total_inserted,
                "case_fixed": metrics.get("case_fixed", 0),
                "null_fields": metrics.get("null_count", 0),
                "invalid_numeric": metrics.get("invalid_numeric", 0),
                "invalid_gps": metrics.get("invalid_gps", 0),
                "invalid_date": metrics.get("invalid_date", 0),
            }
        )

    logging.info(f"Transform: {table_name} selesai.")

# STANDARDISASI & VALIDASI FIELD
def standardize_jenis_fasilitas(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v == "TPA":
        return "TPA"
    if v in ("TPS 3R", "TPS3R", "TPS-3R"):
        return "TPS 3R"
    if v in ("BANK SAMPAH", "BANKSAMPAH"):
        return "Bank Sampah"
    if not v:
        return "TIDAK DIKETAHUI"
    return proper_case(val)

def standardize_status_operasional(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("AKTIF", "1", "YES"):
        return "Aktif"
    if v in ("NON-AKTIF", "NON AKTIF", "NONAKTIF", "0", "NO"):
        return "Non-Aktif"
    if not v:
        return "TIDAK DIKETAHUI"
    return "TIDAK DIKETAHUI"

def standardize_jenis_stasiun(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("AIR SUNGAI", "AIRSUNGAI", "AIR"):
        return "Air Sungai"
    if v == "UDARA":
        return "Udara"
    if not v:
        return "TIDAK DIKETAHUI"
    return proper_case(val)

def standardize_status_aktif(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("AKTIF", "1", "YES"):
        return "Aktif"
    if v in ("NON-AKTIF", "NON AKTIF", "NONAKTIF", "0", "NO"):
        return "Non-Aktif"
    if not v:
        return "TIDAK DIKETAHUI"
    return "TIDAK DIKETAHUI"

def standardize_jenis_dokumen(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v == "AMDAL":
        return "AMDAL"
    if v in ("UKL-UPL", "UKL UPL", "UKLUPL"):
        return "UKL-UPL"
    if v == "SPPL":
        return "SPPL"
    if not v:
        return "TIDAK DIKETAHUI"
    return proper_case(val)

def standardize_status_izin(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("AKTIF", "BERLAKU"):
        return "Aktif"
    if v in ("KADALUARSA", "EXPIRED", "NON-AKTIF"):
        return "Kadaluarsa"
    return "TIDAK DIKETAHUI"

def standardize_status_mutu(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("BAIK", "GOOD"):
        return "Baik"
    if v in ("SEDANG", "MODERATE"):
        return "Sedang"
    if v in ("BURUK", "BAD", "POOR"):
        return "Buruk"
    return "TIDAK DIKETAHUI"

def standardize_jenis_sampah(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("ORGANIK", "ORGANIC"):
        return "Organik"
    if v in ("ANORGANIK", "ANORGANIC", "NON-ORGANIK"):
        return "Anorganik"
    if v in ("PLASTIK", "PLASTIC"):
        return "Plastik"
    if v in ("KERTAS", "PAPER"):
        return "Kertas"
    if v in ("CAMPURAN", "MIXED"):
        return "Campuran"
    if v in ("B3", "BERBAHAYA"):
        return "B3"
    return "TIDAK DIKETAHUI"

def standardize_jenis_tutupan(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("HUTAN KOTA", "HUTANKOTA"):
        return "Hutan Kota"
    if v == "TAMAN":
        return "Taman"
    if v in ("JALUR HIJAU", "JALURHIJAU"):
        return "Jalur Hijau"
    if v == "KEBUN":
        return "Kebun"
    if v in ("HUTAN LINDUNG", "HUTANLINDUNG"):
        return "Hutan Lindung"
    if v in ("HUTAN ALAM", "HUTANALAM"):
        return "Hutan Alam"
    if v in ("HUTAN PRODUKSI", "HUTANPRODUKSI"):
        return "Hutan Produksi"
    if v == "PERKEBUNAN":
        return "Perkebunan"
    if v == "SAWAH":
        return "Sawah"
    if v in ("TAMAN NASIONAL", "TAMANNASIONAL"):
        return "Taman Nasional"
    if v in ("RTH KOTA", "RTHKOTA"):
        return "RTH Kota"
    if v in ("HUTAN LINDUNG", "HUTANLINDUNG"):
        return "Hutan Lindung"
    if v in ("HUTAN ALAM", "HUTANALAM"):
        return "Hutan Alam"
    if v in ("HUTAN PRODUKSI", "HUTANPRODUKSI"):
        return "Hutan Produksi"
    return "TIDAK DIKETAHUI"

def standardize_kategori_ispu(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("BAIK", "GOOD"):
        return "Baik"
    if v in ("SEDANG", "MODERATE"):
        return "Sedang"
    if v in ("TIDAK SEHAT", "UNHEALTHY", "BURUK"):
        return "Tidak Sehat"
    return "TIDAK DIKETAHUI"

def standardize_status_mutu(val):
    if not val:
        return "TIDAK DIKETAHUI"
    v = str(val).strip().upper()
    if v in ("BAIK", "GOOD"):
        return "Baik"
    if v in ("SEDANG", "MODERATE"):
        return "Sedang"
    if v in ("BURUK", "BAD", "POOR"):
        return "Buruk"
    return "TIDAK DIKETAHUI"

# VALIDASI & PARSING UTILITIES
def safe_numeric(val, target_type="DECIMAL(10,2)", min_val=None, max_val=None):
    if val is None:
        return None
    try:
        val_str = str(val).strip()
        if not val_str:
            return None
        if not re.match(r'^-?[0-9]+\.?[0-9]*$', val_str):
            return None
        num = float(val_str)
        if min_val is not None and num < min_val:
            return None
        if max_val is not None and num > max_val:
            return None
        if "INT" in target_type.upper():
            return int(num)
        return round(num, 2) if "." in target_type else int(num)
    except (ValueError, TypeError):
        return None

def safe_int(val, min_val=None, max_val=None):
    if val is None:
        return None
    try:
        val_str = str(val).strip()
        if not val_str:
            return None
        if not re.match(r'^-?[0-9]+$', val_str):
            return None
        num = int(val_str)
        if min_val is not None and num < min_val:
            return None
        if max_val is not None and num > max_val:
            return None
        return num
    except (ValueError, TypeError):
        return None

def validate_gps(val):
    if not val:
        return None
    val = str(val).strip()
    if not val or val.lower() == "invalid":
        return None
    if not re.match(r'^-?[0-9]+\.?[0-9]*,-?[0-9]+\.?[0-9]*$', val):
        return None
    try:
        lat_str, lon_str = val.split(',')
        lat = float(lat_str)
        lon = float(lon_str)
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return None
        return val
    except (ValueError, TypeError):
        return None

def parse_date_multi_format(val):
    if not val:
        return None
    val = str(val).strip()
    if not val:
        return None
    formats = [
        ("%Y-%m-%d", r'^\d{4}-\d{2}-\d{2}$'),
        ("%d-%m-%Y", r'^\d{2}-\d{2}-\d{4}$'),
        ("%d/%m/%Y", r'^\d{2}/\d{2}/\d{4}$'),
    ]
    for fmt, pattern in formats:
        if re.match(pattern, val):
            try:
                dt = datetime.strptime(val, fmt).date()
                if dt > datetime.now().date() or dt < date(1900, 1, 1):
                    return None
                return dt
            except ValueError:
                continue
    return None

def parse_datetime_multi_format(val):
    if not val:
        return None
    val = str(val).strip()
    if not val:
        return None
    formats = [
        ("%Y-%m-%d %H:%M:%S", r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'),
        ("%Y-%m-%d %H:%M", r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'),
        ("%d-%m-%Y %H:%M", r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$'),
        ("%d-%m-%Y", r'^\d{2}-\d{2}-\d{4}$'),
        ("%d/%m/%Y", r'^\d{2}/\d{2}/\d{4}$'),
        ("%Y-%m-%d", r'^\d{4}-\d{2}-\d{2}$'),
    ]
    for fmt, pattern in formats:
        if re.match(pattern, val):
            try:
                dt = datetime.strptime(val, fmt)
                if dt > datetime.now() or dt < datetime(1900, 1, 1):
                    return None
                return dt
            except ValueError:
                continue
    return None

# AKHIR HELPER FUNCTIONS

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
                        raw_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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

            # KONFIGURASI TABEL STAGING
            staging_tables = [
                {
                    "name": "stg_sda_wilayah",
                    "raw_table": "raw_sda_wilayah",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_wilayah`
                    (
                        stg_id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_desa", "nama_desa", "id_kecamatan", "nama_kecamatan",
                                    "id_kabupaten_kota", "nama_kabupaten_kota", "nama_provinsi",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_desa", "nama_desa", "id_kecamatan", "nama_kecamatan",
                                 "id_kabupaten_kota", "nama_kabupaten_kota", "nama_provinsi",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["nama_desa", "nama_kecamatan", "nama_kabupaten_kota", "nama_provinsi"],
                    "where_clause": "WHERE id_desa IS NOT NULL AND TRIM(id_desa) <> '' AND nama_desa IS NOT NULL AND TRIM(nama_desa) <> ''",
                    "distinct": True,
                },
                {
                    "name": "stg_sda_fasilitas_sampah",
                    "raw_table": "raw_sda_fasilitas_sampah",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_fasilitas_sampah`
                    (
                        stg_id                      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_fasilitas", "nama_fasilitas", "jenis_fasilitas",
                                    "id_desa", "nama_desa", "kapasitas_maksimal_ton", "status_operasional",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_fasilitas", "nama_fasilitas", "jenis_fasilitas",
                                 "id_desa", "nama_desa", "kapasitas_maksimal_ton", "status_operasional",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["nama_fasilitas", "nama_desa"],
                    "where_clause": "WHERE id_fasilitas IS NOT NULL AND TRIM(id_fasilitas) <> '' AND nama_fasilitas IS NOT NULL AND TRIM(nama_fasilitas) <> ''",
                    "distinct": True,
                    "processors": {
                        "jenis_fasilitas": lambda v: standardize_jenis_fasilitas(v),
                        "kapasitas_maksimal_ton": lambda v: safe_numeric(v, "DECIMAL(10,2)", min_val=0),
                        "status_operasional": lambda v: standardize_status_operasional(v),
                    },
                },
                {
                    "name": "stg_sda_perusahaan",
                    "raw_table": "raw_sda_perusahaan",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_perusahaan`
                    (
                        stg_id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_perusahaan", "nama_perusahaan", "bidang_usaha",
                                    "alamat_lengkap", "id_desa", "nama_desa", "kontak_perusahaan",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_perusahaan", "nama_perusahaan", "bidang_usaha",
                                 "alamat_lengkap", "id_desa", "nama_desa", "kontak_perusahaan",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["nama_perusahaan", "nama_desa", "alamat_lengkap", "bidang_usaha"],
                    "where_clause": "WHERE id_perusahaan IS NOT NULL AND TRIM(id_perusahaan) <> '' AND nama_perusahaan IS NOT NULL AND TRIM(nama_perusahaan) <> ''",
                    "distinct": True,
                    "processors": {
                        "bidang_usaha": lambda v: v.strip() if v and v.strip() else "TIDAK DIKETAHUI",
                    },
                },
                {
                    "name": "stg_sda_stasiun_pantau",
                    "raw_table": "raw_sda_stasiun_pantau",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_stasiun_pantau`
                    (
                        stg_id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_stasiun", "nama_stasiun", "jenis_stasiun",
                                    "id_desa", "nama_desa", "koordinat_gps", "status_aktif",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_stasiun", "nama_stasiun", "jenis_stasiun",
                                 "id_desa", "nama_desa", "koordinat_gps", "status_aktif",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["nama_stasiun", "nama_desa"],
                    "where_clause": "WHERE id_stasiun IS NOT NULL AND TRIM(id_stasiun) <> '' AND nama_stasiun IS NOT NULL AND TRIM(nama_stasiun) <> ''",
                    "distinct": True,
                    "processors": {
                        "jenis_stasiun": lambda v: standardize_jenis_stasiun(v),
                        "koordinat_gps": lambda v: validate_gps(v),
                        "status_aktif": lambda v: standardize_status_aktif(v),
                    },
                },
                {
                    "name": "stg_sda_izin_lingkungan",
                    "raw_table": "raw_sda_izin_lingkungan",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_izin_lingkungan`
                    (
                        stg_id                          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_izin", "id_perusahaan", "nomor_izin", "jenis_dokumen",
                                    "tanggal_terbit", "masa_berlaku_tahun", "status_izin",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_izin", "id_perusahaan", "nomor_izin", "jenis_dokumen",
                                 "tanggal_terbit", "masa_berlaku_tahun", "status_izin",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["nomor_izin"],
                    "where_clause": "WHERE id_izin IS NOT NULL AND TRIM(id_izin) <> '' AND id_perusahaan IS NOT NULL AND TRIM(id_perusahaan) <> ''",
                    "distinct": True,
                    "processors": {
                        "jenis_dokumen": lambda v: standardize_jenis_dokumen(v),
                        "tanggal_terbit": lambda v: parse_date_multi_format(v),
                        "masa_berlaku_tahun": lambda v: safe_int(v, min_val=1, max_val=50),
                        "status_izin": lambda v: standardize_status_izin(v),
                    },
                },
                {
                    "name": "stg_sda_kualitas_air_sungai",
                    "raw_table": "raw_sda_kualitas_air_sungai",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_kualitas_air_sungai`
                    (
                        stg_id                      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_sampel", "id_stasiun", "nama_sungai", "waktu_pengambilan",
                                    "ph_air", "bod_mg_l", "cod_mg_l", "tss_mg_l", "status_mutu",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_sampel", "id_stasiun", "nama_sungai", "waktu_pengambilan",
                                 "ph_air", "bod_mg_l", "cod_mg_l", "tss_mg_l", "status_mutu",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["nama_sungai"],
                    "where_clause": "WHERE id_sampel IS NOT NULL AND TRIM(id_sampel) <> '' AND nama_sungai IS NOT NULL AND TRIM(nama_sungai) <> ''",
                    "distinct": True,
                    "processors": {
                        "waktu_pengambilan": lambda v: parse_datetime_multi_format(v),
                        "ph_air": lambda v: safe_numeric(v, "DECIMAL(5,2)", min_val=0, max_val=14),
                        "bod_mg_l": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "cod_mg_l": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "tss_mg_l": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "status_mutu": lambda v: standardize_status_mutu(v),
                    },
                },
                {
                    "name": "stg_sda_kualitas_udara",
                    "raw_table": "raw_sda_kualitas_udara",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_kualitas_udara`
                    (
                        stg_id                      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_record", "id_stasiun", "waktu_pengukuran",
                                    "pm10", "so2", "co", "o3", "no2", "kategori_ispu",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_record", "id_stasiun", "waktu_pengukuran",
                                 "pm10", "so2", "co", "o3", "no2", "kategori_ispu",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": [],
                    "where_clause": "WHERE id_record IS NOT NULL AND TRIM(id_record) <> ''",
                    "distinct": True,
                    "processors": {
                        "waktu_pengukuran": lambda v: parse_datetime_multi_format(v),
                        "pm10": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "so2": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "co": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "o3": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "no2": lambda v: safe_numeric(v, "DECIMAL(8,2)", min_val=0),
                        "kategori_ispu": lambda v: standardize_kategori_ispu(v),
                    },
                },
                {
                    "name": "stg_sda_timbulan_sampah",
                    "raw_table": "raw_sda_timbulan_sampah",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_timbulan_sampah`
                    (
                        stg_id                      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_laporan", "id_fasilitas", "tanggal_lapor", "volume_masuk_ton",
                                    "jenis_sampah_dominan", "sumber_sistem",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_laporan", "id_fasilitas", "tanggal_lapor", "volume_masuk_ton",
                                 "jenis_sampah_dominan", "sumber_sistem",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["sumber_sistem"],
                    "where_clause": "WHERE id_laporan IS NOT NULL AND TRIM(id_laporan) <> ''",
                    "distinct": True,
                    "processors": {
                        "tanggal_lapor": lambda v: parse_date_multi_format(v),
                        "volume_masuk_ton": lambda v: safe_numeric(v, "DECIMAL(10,2)", min_val=0),
                        "jenis_sampah_dominan": lambda v: standardize_jenis_sampah(v),
                    },
                },
                {
                    "name": "stg_sda_tutupan_lahan_rth",
                    "raw_table": "raw_sda_tutupan_lahan_rth",
                    "stg_id": "stg_id",
                    "create_sql": f"""
                    CREATE TABLE `{staging_db}`.`stg_sda_tutupan_lahan_rth`
                    (
                        stg_id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
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
                    """,
                    "insert_cols": ["id_polygon", "id_desa", "jenis_tutupan", "luas_hektar",
                                    "sumber_citra", "tanggal_citra",
                                    "sumber_database", "waktu_ekstraksi"],
                    "raw_cols": ["id_polygon", "id_desa", "jenis_tutupan", "luas_hektar",
                                 "sumber_citra", "tanggal_citra",
                                 "sumber_database", "waktu_ekstraksi"],
                    "name_fields": ["sumber_citra"],
                    "where_clause": "WHERE id_polygon IS NOT NULL AND TRIM(id_polygon) <> '' AND id_desa IS NOT NULL AND TRIM(id_desa) <> ''",
                    "distinct": True,
                    "processors": {
                        "jenis_tutupan": lambda v: standardize_jenis_tutupan(v),
                        "luas_hektar": lambda v: safe_numeric(v, "DECIMAL(10,2)", min_val=0),
                        "tanggal_citra": lambda v: parse_date_multi_format(v),
                    },
                },
            ]

            # ============================================================
            # PROSES SETIAP TABEL
            # ============================================================
            for table_cfg in staging_tables:
                process_staging_table(cursor, conn, raw_db, staging_db, table_cfg, raw_db, SOURCE_DB)

            logging.info("Transform staging selesai.")

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

        logging.info("Membuat dimension dan fact...")

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
                waktu_key INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

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

                nama_desa = VALUES(nama_desa),
                id_kecamatan = VALUES(id_kecamatan),
                nama_kecamatan = VALUES(nama_kecamatan),
                id_kabupaten_kota = VALUES(id_kabupaten_kota),
                nama_kabupaten_kota = VALUES(nama_kabupaten_kota),
                nama_provinsi = VALUES(nama_provinsi),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
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

                nama_fasilitas = VALUES(nama_fasilitas),
                jenis_fasilitas = VALUES(jenis_fasilitas),
                id_desa = VALUES(id_desa),
                kapasitas_maksimal_ton = VALUES(kapasitas_maksimal_ton),
                status_operasional = VALUES(status_operasional),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
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

                nama_perusahaan = VALUES(nama_perusahaan),
                bidang_usaha = VALUES(bidang_usaha),
                alamat_lengkap = VALUES(alamat_lengkap),
                id_desa = VALUES(id_desa),
                kontak_perusahaan = VALUES(kontak_perusahaan),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
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

                nama_stasiun = VALUES(nama_stasiun),
                jenis_stasiun = VALUES(jenis_stasiun),
                id_desa = VALUES(id_desa),
                koordinat_gps = VALUES(koordinat_gps),
                status_aktif = VALUES(status_aktif),
                sumber_database = VALUES(sumber_database),
                waktu_load = VALUES(waktu_load);
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

        logging.info("Load ke Data Warehouse selesai.")

    t_extract = extract_to_raw()
    t_transform = transform_staging()
    t_load = load_to_dwh()

    t_extract >> t_transform >> t_load

    return t_load
