from __future__ import annotations

import logging
import re

import pendulum
import requests

from airflow.sdk import task


SOURCE_DB = "db_perencanaan"

SOURCE_TABLES = {
    "skpa": "master_skpa",
    "program": "tb_program",
    "kegiatan": "tb_kegiatan",
    "target": "tb_target",
    "realisasi": "tb_realisasi",
    "evaluasi": "tb_evaluasi_pembangunan",
}

RAW_TABLE_MAP = {
    "skpa": "raw_perencanaan_skpa",
    "program": "raw_perencanaan_program",
    "kegiatan": "raw_perencanaan_kegiatan",
    "target": "raw_perencanaan_target",
    "realisasi": "raw_perencanaan_realisasi",
    "evaluasi": "raw_perencanaan_evaluasi",
}

STG_TABLE_MAP = {
    "skpa": "stg_perencanaan_skpa",
    "program": "stg_perencanaan_program",
    "kegiatan": "stg_perencanaan_kegiatan",
    "target": "stg_perencanaan_target",
    "realisasi": "stg_perencanaan_realisasi",
    "evaluasi": "stg_perencanaan_evaluasi",
}

KAB_KOTA_MAPPING = {
    "01": "Kota Banda Aceh",
    "02": "Kota Sabang",
    "03": "Kota Lhokseumawe",
    "04": "Kota Langsa",
    "05": "Kabupaten Aceh Barat",
    "06": "Kabupaten Aceh Barat Daya",
    "07": "Kabupaten Aceh Besar",
    "08": "Kabupaten Aceh Jaya",
    "09": "Kabupaten Aceh Selatan",
    "10": "Kabupaten Aceh Singkil",
    "11": "Kabupaten Aceh Tamiang",
    "12": "Kabupaten Aceh Tengah",
    "13": "Kabupaten Aceh Tenggara",
    "14": "Kabupaten Aceh Timur",
    "15": "Kabupaten Gayo Lues",
    "16": "Kabupaten Pidie",
    "17": "Kabupaten Pidie Jaya",
    "18": "Kabupaten Simeulue",
    "19": "Kabupaten Bireuen",
    "20": "Kabupaten Nagan Raya",
    "21": "Kota Subulussalam",
    "22": "Kabupaten Bener Meriah",
    "23": "Kabupaten Aceh Utara",
}

KOTA_CODES = {"01", "02", "03", "04", "21"}

ACRONYMS_UPPER = {
    "SKPA", "RTH", "TPA", "TPS", "APBA", "APBN", "UKL", "UPL", "UKL-UPL",
    "AMDAL", "PM10", "PM2.5", "KWP", "KWH", "MW", "KW", "HA", "KM",
    "M", "CM", "MM", "KG", "TON", "LITER", "ML", "UNIT", "BUAH",
    "PAKET", "ORANG", "JIWA", "KEPALA", "EKOR", "BUAH", "BUTIR",
    "SET", "ROLL", "METER", "M2", "M3", "KM2", "HA", "RB", "JT",
    "MT", "YTD", "Q1", "Q2", "Q3", "Q4", "TW1", "TW2", "TW3", "TW4",
    "KAB", "KOTA", "KEC", "DESA", "DS", "KEL", "RT", "RW", "DUSUN",
    "BANJAR", "NAGARI", "GAMPONG", "MEUNASAH", "KAMPUNG", "LINGKUNGAN",
    "BPS", "BAPPEDA", "DINAS", "BPBD", "KLHK", "ESDM", "PUPR", "DISNAKER",
    "DISDIKBUD", "DINKES", "DISPERINDAG", "DISKOMINFO", "DISHUB", "DISPERTA",
    "DPMD", "DPMPTSP", "INSPEKTORAT", "KEJAKSAAN", "POLRES", "POLDA",
    "TNI", "POLRI", "BNN", "KPK", "OJK", "BI", "KPU", "BAWASLU",
}

def proper_case_preserve_acronyms(text: str) -> str:
    if not text or not text.strip():
        return text
    words = text.strip().split()
    result = []
    for word in words:
        upper_word = word.upper()
        if upper_word in ACRONYMS_UPPER:
            result.append(upper_word)
        elif "-" in word:
            parts = word.split("-")
            new_parts = []
            for part in parts:
                if part.upper() in ACRONYMS_UPPER:
                    new_parts.append(part.upper())
                else:
                    new_parts.append(part.capitalize())
            result.append("-".join(new_parts))
        elif "/" in word:
            parts = word.split("/")
            new_parts = [p.capitalize() if p.upper() not in ACRONYMS_UPPER else p.upper() for p in parts]
            result.append("/".join(new_parts))
        else:
            result.append(word.capitalize())
    return " ".join(result)


def clean_text(text: str) -> str:
    if not text:
        return text
    text = re.sub(r"\s+", " ", text.strip())
    return text


def standardize_kab_kota(code: str, name: str) -> tuple[str, str]:
    code_clean = code.zfill(2) if code and code.isdigit() else (code or "").zfill(2)
    # Always use the canonical name from mapping based on code
    if code_clean in KAB_KOTA_MAPPING:
        name_proper = KAB_KOTA_MAPPING[code_clean]
    else:
        name_clean = clean_text(name)
        name_proper = proper_case_preserve_acronyms(name_clean)
        if code_clean in KOTA_CODES:
            if not name_proper.startswith("Kota "):
                name_proper = f"Kota {name_proper}"
        else:
            if not name_proper.startswith("Kabupaten "):
                name_proper = f"Kabupaten {name_proper}"
    
    return code_clean, name_proper


def standardize_kecamatan(code: str, name: str) -> tuple[str, str]:
    code_clean = code.zfill(4) if code and code.isdigit() else (code or "").zfill(4)
    name_clean = clean_text(name)
    name_proper = proper_case_preserve_acronyms(name_clean)
    name_proper = name_proper.replace("Kec. ", "Kecamatan ").replace("Kec ", "Kecamatan ")
    return code_clean, name_proper


def standardize_desa(code: str, name: str) -> tuple[str, str]:
    code_clean = code.zfill(5) if code and code.isdigit() else (code or "").zfill(5)
    name_clean = clean_text(name)
    name_proper = proper_case_preserve_acronyms(name_clean)
    name_proper = name_proper.replace("Ds. ", "Desa ").replace("Ds ", "Desa ").replace("Gampong ", "Gampong ").replace("Meunasah ", "Meunasah ")
    return code_clean, name_proper


def standardize_satuan(satuan: str) -> str:
    if not satuan:
        return satuan
    s = satuan.strip().lower()
    mapping = {
        "ton": "Ton",
        "ha": "Hektar",
        "hektar": "Hektar",
        "km": "Kilometer",
        "kilometer": "Kilometer",
        "m": "Meter",
        "meter": "Meter",
        "unit": "Unit",
        "buah": "Buah",
        "paket": "Paket",
        "orang": "Orang",
        "jiwa": "Jiwa",
        "kepala": "Kepala",
        "ekor": "Ekor",
        "set": "Set",
        "roll": "Roll",
        "m2": "Meter2",
        "m3": "Meter3",
        "km2": "Km2",
        "kw": "KW",
        "kwp": "KWp",
        "kwh": "KWh",
        "mw": "MW",
        "liter": "Liter",
        "ml": "ML",
        "rb": "Ribu",
        "jt": "Juta",
        "mt": "Meter",
    }
    return mapping.get(s, proper_case_preserve_acronyms(satuan))


def parse_date(date_val):
    if not date_val:
        return None
    if isinstance(date_val, str):
        try:
            return pendulum.parse(date_val).date()
        except Exception:
            return None
    if hasattr(date_val, 'year'):
        return date_val
    return None


def fix_tanggal_selesai(tanggal_mulai, tanggal_selesai):
    tgl_mulai = parse_date(tanggal_mulai)
    tgl_selesai = parse_date(tanggal_selesai)
    if tgl_mulai and tgl_selesai and tgl_selesai < tgl_mulai:
        return pendulum.date(tgl_mulai.year, 12, 31)
    return tgl_selesai


def fix_tanggal_lapor(tanggal_lapor, triwulan, tahun):
    tgl_lapor = parse_date(tanggal_lapor)
    if tgl_lapor and (tgl_lapor.year == 1970 or str(tgl_lapor) == "1970-01-01"):
        tw_end = {
            "TW1": (3, 31),
            "TW2": (6, 30),
            "TW3": (9, 30),
            "TW4": (12, 31),
        }
        month, day = tw_end.get(triwulan, (12, 31))
        try:
            return pendulum.date(int(tahun), month, day)
        except Exception:
            return pendulum.date(int(tahun), 12, 31)
    return tgl_lapor


def standardize_kendala(kendala: str) -> str:
    if not kendala:
        return "Tidak Ada Kendala"
    k = kendala.strip()
    if k.upper() in ("", "-", "N/A", "NULL", "NONE", "TIDAK ADA KENDALA", "TIDAK ADA"):
        return "Tidak Ada Kendala"
    return proper_case_preserve_acronyms(k)


SOURCE_ENDPOINTS = {
    "skpa": "/skpa",
    "program": "/program",
    "kegiatan": "/kegiatan",
    "target": "/target",
    "realisasi": "/realisasi",
    "evaluasi": "/evaluasi",
}

SOURCE_TABLES = {
    "skpa": "master_skpa",
    "program": "tb_program",
    "kegiatan": "tb_kegiatan",
    "target": "tb_target",
    "realisasi": "tb_realisasi",
    "evaluasi": "tb_evaluasi_pembangunan",
}

RAW_TABLE_MAP = {
    "skpa": "raw_perencanaan_skpa",
    "program": "raw_perencanaan_program",
    "kegiatan": "raw_perencanaan_kegiatan",
    "target": "raw_perencanaan_target",
    "realisasi": "raw_perencanaan_realisasi",
    "evaluasi": "raw_perencanaan_evaluasi",
}


def create_perencanaan_tasks(
    execute_sql,
    get_mysql_hook,
    raw_db,
    staging_db,
    dwh_db,
    api_base_url,
):

    @task(task_id="extract_to_raw_perencanaan")
    def extract_to_raw():
        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            logging.info("Memulai extract API -> raw_data...")

            cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`raw_perencanaan_skpa`;")
            cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`raw_perencanaan_program`;")
            cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`raw_perencanaan_kegiatan`;")
            cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`raw_perencanaan_target`;")
            cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`raw_perencanaan_realisasi`;")
            cursor.execute(f"DROP TABLE IF EXISTS `{raw_db}`.`raw_perencanaan_evaluasi`;")
            conn.commit()

            now_str = pendulum.now("Asia/Jakarta").to_datetime_string()

            for key, endpoint in SOURCE_ENDPOINTS.items():
                raw_table = RAW_TABLE_MAP[key]

                url = f"{api_base_url}{endpoint}"

                logging.info(
                    "Extract API %s -> %s.%s",
                    url,
                    raw_db,
                    raw_table,
                )

                records = []
                page = 1
                max_pages = 100  # safety limit

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
                                key,
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
                        row.append("db_perencanaan")
                        row.append(now_str)
                        rows.append(row)

                    cursor.executemany(sql_insert, rows)
                    total += len(rows)

                logging.info(
                    "Extract %s selesai. %d records.",
                    key,
                    total,
                )

            conn.commit()
            logging.info("Extract semua tabel selesai.")

        except Exception as e:
            conn.rollback()
            logging.error("ERROR extract_to_raw_perencanaan: %s", str(e))
            raise
        finally:
            cursor.close()
            conn.close()

    @task(task_id="transform_staging_perencanaan")
    def transform_staging():
        hook = get_mysql_hook()
        conn = hook.get_conn()
        cursor = conn.cursor()

        try:
            logging.info("Memulai transform raw_data -> staging_area...")

            cursor.execute(f"""
            ALTER DATABASE `{staging_db}`
            CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
            """)
            conn.commit()

            # ============================================================
            # STG SKPA
            # ============================================================
            logging.info("Transform: stg_perencanaan_skpa...")
            cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`stg_perencanaan_skpa`;")
            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_perencanaan_skpa` (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_skpa VARCHAR(20),
                kode_skpa VARCHAR(30),
                nama_skpa VARCHAR(200),
                bidang_urusan VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_perencanaan_skpa`
            (id_skpa, kode_skpa, nama_skpa, bidang_urusan, sumber_database, waktu_ekstraksi)
            SELECT DISTINCT
                TRIM(id_skpa),
                TRIM(kode_skpa),
                TRIM(nama_skpa),
                TRIM(bidang_urusan),
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_perencanaan_skpa`
            WHERE id_skpa IS NOT NULL AND TRIM(id_skpa) <> '';
            """)
            conn.commit()

            # ============================================================
            # STG PROGRAM
            # ============================================================
            logging.info("Transform: stg_perencanaan_program...")
            cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`stg_perencanaan_program`;")
            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_perencanaan_program` (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_program VARCHAR(20),
                id_skpa VARCHAR(20),
                kode_program VARCHAR(30),
                nama_program VARCHAR(250),
                bidang_urusan VARCHAR(150),
                tahun_anggaran YEAR,
                sumber_dana VARCHAR(30),
                pagu_anggaran_program DECIMAL(18,2),
                status_program VARCHAR(30),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_perencanaan_program`
            (id_program, id_skpa, kode_program, nama_program, bidang_urusan, tahun_anggaran,
             sumber_dana, pagu_anggaran_program, status_program, sumber_database, waktu_ekstraksi)
            SELECT DISTINCT
                TRIM(id_program),
                TRIM(id_skpa),
                TRIM(kode_program),
                TRIM(nama_program),
                TRIM(bidang_urusan),
                CAST(tahun_anggaran AS UNSIGNED),
                TRIM(sumber_dana),
                CAST(pagu_anggaran_program AS DECIMAL(18,2)),
                TRIM(status_program),
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_perencanaan_program`
            WHERE id_program IS NOT NULL AND TRIM(id_program) <> '';
            """)
            conn.commit()

            # ============================================================
            # STG KEGIATAN
            # ============================================================
            logging.info("Transform: stg_perencanaan_kegiatan...")
            cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`stg_perencanaan_kegiatan`;")
            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_perencanaan_kegiatan` (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_kegiatan VARCHAR(20),
                id_program VARCHAR(20),
                kode_kegiatan VARCHAR(40),
                nama_kegiatan VARCHAR(300),
                id_desa VARCHAR(10),
                nama_desa VARCHAR(150),
                id_kecamatan VARCHAR(10),
                nama_kecamatan VARCHAR(150),
                id_kabupaten_kota VARCHAR(10),
                nama_kabupaten_kota VARCHAR(150),
                pagu_anggaran_kegiatan DECIMAL(18,2),
                tanggal_mulai DATE,
                tanggal_selesai DATE,
                status_kegiatan VARCHAR(30),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            SELECT
                id_kegiatan, id_program, kode_kegiatan, nama_kegiatan,
                id_desa, nama_desa, id_kecamatan, nama_kecamatan,
                id_kabupaten_kota, nama_kabupaten_kota,
                pagu_anggaran_kegiatan, tanggal_mulai, tanggal_selesai, status_kegiatan,
                sumber_database, waktu_ekstraksi
            FROM `{raw_db}`.`raw_perencanaan_kegiatan`
            """)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            insert_sql = f"""
            INSERT INTO `{staging_db}`.`stg_perencanaan_kegiatan`
            (id_kegiatan, id_program, kode_kegiatan, nama_kegiatan,
             id_desa, nama_desa, id_kecamatan, nama_kecamatan,
             id_kabupaten_kota, nama_kabupaten_kota,
             pagu_anggaran_kegiatan, tanggal_mulai, tanggal_selesai, status_kegiatan,
             sumber_database, waktu_ekstraksi)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            for row in rows:
                r = dict(zip(columns, row))
                
                id_desa, nama_desa = standardize_desa(r.get("id_desa"), r.get("nama_desa"))
                id_kecamatan, nama_kecamatan = standardize_kecamatan(r.get("id_kecamatan"), r.get("nama_kecamatan"))
                id_kab_kota, nama_kab_kota = standardize_kab_kota(r.get("id_kabupaten_kota"), r.get("nama_kabupaten_kota"))
                
                nama_kegiatan_clean = proper_case_preserve_acronyms(clean_text(r.get("nama_kegiatan", "")))
                
                pagu = r.get("pagu_anggaran_kegiatan")
                try:
                    pagu_val = float(pagu) if pagu is not None else 0.0
                except Exception:
                    pagu_val = 0.0
                
                tgl_mulai = r.get("tanggal_mulai")
                tgl_selesai = r.get("tanggal_selesai")
                tgl_selesai_fixed = fix_tanggal_selesai(tgl_mulai, tgl_selesai)
                
                status = clean_text(r.get("status_kegiatan", ""))

                cursor.execute(insert_sql, (
                    clean_text(r.get("id_kegiatan", "")),
                    clean_text(r.get("id_program", "")),
                    clean_text(r.get("kode_kegiatan", "")),
                    nama_kegiatan_clean,
                    id_desa, nama_desa,
                    id_kecamatan, nama_kecamatan,
                    id_kab_kota, nama_kab_kota,
                    pagu_val,
                    tgl_mulai,
                    tgl_selesai_fixed,
                    status,
                    r.get("sumber_database"),
                    r.get("waktu_ekstraksi"),
                ))
            conn.commit()

            # ============================================================
            # STG TARGET
            # ============================================================
            logging.info("Transform: stg_perencanaan_target...")
            cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`stg_perencanaan_target`;")
            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_perencanaan_target` (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_target VARCHAR(20),
                id_kegiatan VARCHAR(20),
                tahun YEAR,
                triwulan VARCHAR(10),
                indikator_kinerja VARCHAR(300),
                target_fisik_nilai DECIMAL(12,2),
                satuan_fisik VARCHAR(50),
                target_persentase DECIMAL(5,2),
                target_anggaran DECIMAL(18,2),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_perencanaan_target`
            (id_target, id_kegiatan, tahun, triwulan, indikator_kinerja,
             target_fisik_nilai, satuan_fisik, target_persentase, target_anggaran,
             sumber_database, waktu_ekstraksi)
            SELECT DISTINCT
                TRIM(id_target),
                TRIM(id_kegiatan),
                CAST(tahun AS UNSIGNED),
                TRIM(triwulan),
                TRIM(indikator_kinerja),
                CAST(target_fisik_nilai AS DECIMAL(12,2)),
                TRIM(satuan_fisik),
                CAST(target_persentase AS DECIMAL(5,2)),
                CAST(target_anggaran AS DECIMAL(18,2)),
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_perencanaan_target`
            WHERE id_target IS NOT NULL AND TRIM(id_target) <> '';
            """)
            conn.commit()

            # Update satuan_fisik di staging target
            cursor.execute(f"""
            UPDATE `{staging_db}`.`stg_perencanaan_target`
            SET satuan_fisik = %s
            WHERE LOWER(TRIM(satuan_fisik)) IN ('ton', 'ton ')
            """, ("Ton",))
            cursor.execute(f"""
            UPDATE `{staging_db}`.`stg_perencanaan_target`
            SET satuan_fisik = %s
            WHERE LOWER(TRIM(satuan_fisik)) IN ('ha', 'hektar')
            """, ("Hektar",))
            cursor.execute(f"""
            UPDATE `{staging_db}`.`stg_perencanaan_target`
            SET satuan_fisik = %s
            WHERE LOWER(TRIM(satuan_fisik)) IN ('km', 'kilometer')
            """, ("Kilometer",))
            cursor.execute(f"""
            UPDATE `{staging_db}`.`stg_perencanaan_target`
            SET satuan_fisik = %s
            WHERE LOWER(TRIM(satuan_fisik)) IN ('unit')
            """, ("Unit",))
            conn.commit()

            # ============================================================
            # STG REALISASI
            # ============================================================
            logging.info("Transform: stg_perencanaan_realisasi...")
            cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`stg_perencanaan_realisasi`;")
            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_perencanaan_realisasi` (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_realisasi VARCHAR(20),
                id_kegiatan VARCHAR(20),
                id_target VARCHAR(20),
                tanggal_lapor DATE,
                triwulan VARCHAR(10),
                realisasi_fisik_nilai DECIMAL(12,2),
                realisasi_fisik_persen DECIMAL(5,2),
                realisasi_anggaran DECIMAL(18,2),
                serapan_anggaran_persen DECIMAL(5,2),
                kendala_lapangan TEXT,
                is_anomali TINYINT DEFAULT 0,
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)

            cursor.execute(f"""
            SELECT
                id_realisasi, id_kegiatan, id_target, tanggal_lapor, triwulan,
                realisasi_fisik_nilai, realisasi_fisik_persen, realisasi_anggaran,
                serapan_anggaran_persen, kendala_lapangan,
                sumber_database, waktu_ekstraksi
            FROM `{raw_db}`.`raw_perencanaan_realisasi`
            """)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            seen = set()
            insert_sql = f"""
            INSERT INTO `{staging_db}`.`stg_perencanaan_realisasi`
            (id_realisasi, id_kegiatan, id_target, tanggal_lapor, triwulan,
             realisasi_fisik_nilai, realisasi_fisik_persen, realisasi_anggaran,
             serapan_anggaran_persen, kendala_lapangan, is_anomali,
             sumber_database, waktu_ekstraksi)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            for row in rows:
                r = dict(zip(columns, row))
                
                dedup_key = (
                    clean_text(r.get("id_kegiatan", "")),
                    clean_text(r.get("id_target", "")),
                    clean_text(r.get("triwulan", "")),
                    str(r.get("tanggal_lapor", "")),
                )
                if dedup_key in seen:
                    logging.info("Deduplikasi realisasi: %s", r.get("id_realisasi"))
                    continue
                seen.add(dedup_key)

                tgl_lapor = r.get("tanggal_lapor")
                triwulan = clean_text(r.get("triwulan", ""))
                tahun = None
                cursor.execute(f"SELECT tahun FROM `{staging_db}`.`stg_perencanaan_target` WHERE id_target = %s LIMIT 1", (clean_text(r.get("id_target", "")),))
                target_row = cursor.fetchone()
                if target_row:
                    tahun = target_row[0]
                
                tgl_lapor_fixed = fix_tanggal_lapor(tgl_lapor, triwulan, tahun)

                real_anggaran = r.get("realisasi_anggaran")
                try:
                    real_anggaran_val = float(real_anggaran) if real_anggaran is not None else 0.0
                except Exception:
                    real_anggaran_val = 0.0

                real_fisik_persen = r.get("realisasi_fisik_persen")
                try:
                    real_fisik_persen_val = float(real_fisik_persen) if real_fisik_persen is not None else 0.0
                except Exception:
                    real_fisik_persen_val = 0.0

                is_anomali = 0
                if real_anggaran_val < 0:
                    is_anomali = 1
                    real_anggaran_val = abs(real_anggaran_val)
                if real_fisik_persen_val > 100:
                    is_anomali = 1

                kendala = standardize_kendala(r.get("kendala_lapangan"))

                cursor.execute(insert_sql, (
                    clean_text(r.get("id_realisasi", "")),
                    clean_text(r.get("id_kegiatan", "")),
                    clean_text(r.get("id_target", "")),
                    tgl_lapor_fixed,
                    triwulan,
                    float(r.get("realisasi_fisik_nilai") or 0),
                    real_fisik_persen_val,
                    real_anggaran_val,
                    float(r.get("serapan_anggaran_persen") or 0),
                    kendala,
                    is_anomali,
                    r.get("sumber_database"),
                    r.get("waktu_ekstraksi"),
                ))
            conn.commit()

            # ============================================================
            # STG EVALUASI
            # ============================================================
            logging.info("Transform: stg_perencanaan_evaluasi...")
            cursor.execute(f"DROP TABLE IF EXISTS `{staging_db}`.`stg_perencanaan_evaluasi`;")
            cursor.execute(f"""
            CREATE TABLE `{staging_db}`.`stg_perencanaan_evaluasi` (
                id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                id_evaluasi VARCHAR(20),
                id_program VARCHAR(20),
                id_kegiatan VARCHAR(20),
                id_realisasi VARCHAR(20),
                periode_evaluasi VARCHAR(30),
                tanggal_evaluasi DATE,
                skor_capaian_kinerja DECIMAL(5,2),
                predikat_kinerja VARCHAR(30),
                status_tindak_lanjut VARCHAR(30),
                catatan_evaluasi TEXT,
                rekomendasi_kebijakan TEXT,
                evaluator_skpa VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_ekstraksi DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """)
            cursor.execute(f"""
            INSERT INTO `{staging_db}`.`stg_perencanaan_evaluasi`
            (id_evaluasi, id_program, id_kegiatan, id_realisasi, periode_evaluasi,
             tanggal_evaluasi, skor_capaian_kinerja, predikat_kinerja, status_tindak_lanjut,
             catatan_evaluasi, rekomendasi_kebijakan, evaluator_skpa,
             sumber_database, waktu_ekstraksi)
            SELECT DISTINCT
                TRIM(id_evaluasi),
                TRIM(id_program),
                TRIM(id_kegiatan),
                TRIM(id_realisasi),
                TRIM(periode_evaluasi),
                tanggal_evaluasi,
                CAST(skor_capaian_kinerja AS DECIMAL(5,2)),
                TRIM(predikat_kinerja),
                TRIM(status_tindak_lanjut),
                TRIM(catatan_evaluasi),
                TRIM(rekomendasi_kebijakan),
                COALESCE(NULLIF(TRIM(evaluator_skpa), ''), 'Badan Perencanaan Pembangunan Daerah Aceh'),
                sumber_database,
                waktu_ekstraksi
            FROM `{raw_db}`.`raw_perencanaan_evaluasi`
            WHERE id_evaluasi IS NOT NULL AND TRIM(id_evaluasi) <> '';
            """)
            conn.commit()

            logging.info("Transform staging selesai.")

        except Exception as e:
            conn.rollback()
            logging.error("ERROR transform_staging_perencanaan: %s", str(e))
            raise
        finally:
            cursor.close()
            conn.close()

    @task(task_id="load_to_dwh_perencanaan")
    def load_to_dwh():
        logging.info("Memulai load staging_area -> dwh...")

        align_collation = f"""
        ALTER DATABASE `{dwh_db}`
        CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
        """

        dim_tables = [
            "dim_perencanaan_waktu",
            "dim_perencanaan_skpa",
            "dim_perencanaan_wilayah",
            "dim_perencanaan_program",
            "dim_perencanaan_kegiatan",
            "fact_perencanaan_realisasi",
            "fact_perencanaan_evaluasi",
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
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (dwh_db, dim_table),
                )
                if check_cursor.fetchone()[0]:
                    convert_dim_tables.append(
                        f"""
                        ALTER TABLE `{dwh_db}`.`{dim_table}`
                        CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
                        """
                    )
        finally:
            check_cursor.close()
            check_conn.close()

        execute_sql(convert_dim_tables)

        now_load = pendulum.now("Asia/Jakarta").to_datetime_string()

        create_tables = [
            # DIM WAKTU
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`dim_perencanaan_waktu` (
                waktu_key INT PRIMARY KEY,
                tanggal DATE NOT NULL,
                hari INT,
                bulan INT,
                nama_bulan VARCHAR(20),
                kuartal INT,
                tahun INT,
                waktu_load DATETIME NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,

            # DIM SKPA
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`dim_perencanaan_skpa` (
                skpa_key INT AUTO_INCREMENT PRIMARY KEY,
                id_skpa VARCHAR(20) NOT NULL,
                kode_skpa VARCHAR(30),
                nama_skpa VARCHAR(200),
                bidang_urusan VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_skpa (id_skpa)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,

            # DIM WILAYAH (denormalisasi)
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`dim_perencanaan_wilayah` (
                wilayah_key INT AUTO_INCREMENT PRIMARY KEY,
                id_desa VARCHAR(10) NOT NULL,
                nama_desa VARCHAR(150),
                id_kecamatan VARCHAR(10),
                nama_kecamatan VARCHAR(150),
                id_kabupaten_kota VARCHAR(10) NOT NULL,
                nama_kabupaten_kota VARCHAR(150) NOT NULL,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_wilayah (id_desa)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,

            # DIM PROGRAM
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`dim_perencanaan_program` (
                program_key INT AUTO_INCREMENT PRIMARY KEY,
                skpa_key INT,
                id_program VARCHAR(20) NOT NULL,
                kode_program VARCHAR(30),
                nama_program VARCHAR(250),
                bidang_urusan VARCHAR(150),
                tahun_anggaran YEAR,
                sumber_dana VARCHAR(30),
                pagu_anggaran_program DECIMAL(18,2),
                status_program VARCHAR(30),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_program (id_program),
                KEY idx_program_skpa (skpa_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,

            # DIM KEGIATAN
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`dim_perencanaan_kegiatan` (
                kegiatan_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                program_key INT,
                wilayah_key INT,
                id_kegiatan VARCHAR(20) NOT NULL,
                kode_kegiatan VARCHAR(40),
                nama_kegiatan VARCHAR(300),
                pagu_anggaran_kegiatan DECIMAL(18,2),
                tanggal_mulai DATE,
                tanggal_selesai DATE,
                status_kegiatan VARCHAR(30),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_kegiatan (id_kegiatan),
                KEY idx_kegiatan_program (program_key),
                KEY idx_kegiatan_wilayah (wilayah_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,

            # FACT REALISASI
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`fact_perencanaan_realisasi` (
                realisasi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                kegiatan_key BIGINT,
                program_key INT,
                skpa_key INT,
                wilayah_key INT,
                waktu_key INT,
                id_realisasi VARCHAR(20) NOT NULL,
                id_target VARCHAR(20),
                tahun YEAR,
                triwulan VARCHAR(10),
                indikator_kinerja VARCHAR(300),
                satuan_fisik VARCHAR(50),
                target_fisik_nilai DECIMAL(12,2),
                target_anggaran DECIMAL(18,2),
                realisasi_fisik_nilai DECIMAL(12,2),
                realisasi_fisik_persen DECIMAL(5,2),
                realisasi_anggaran DECIMAL(18,2),
                serapan_anggaran_persen DECIMAL(5,2),
                kendala_lapangan TEXT,
                is_anomali TINYINT DEFAULT 0,
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_realisasi (id_realisasi),
                KEY idx_fact_realisasi_kegiatan (kegiatan_key),
                KEY idx_fact_realisasi_program (program_key),
                KEY idx_fact_realisasi_skpa (skpa_key),
                KEY idx_fact_realisasi_wilayah (wilayah_key),
                KEY idx_fact_realisasi_waktu (waktu_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,

            # FACT EVALUASI
            f"""
            CREATE TABLE IF NOT EXISTS `{dwh_db}`.`fact_perencanaan_evaluasi` (
                evaluasi_key BIGINT AUTO_INCREMENT PRIMARY KEY,
                program_key INT,
                kegiatan_key BIGINT,
                skpa_key INT,
                wilayah_key INT,
                waktu_key INT,
                id_evaluasi VARCHAR(20) NOT NULL,
                id_realisasi VARCHAR(20),
                periode_evaluasi VARCHAR(30),
                skor_capaian_kinerja DECIMAL(5,2),
                predikat_kinerja VARCHAR(30),
                status_tindak_lanjut VARCHAR(30),
                catatan_evaluasi TEXT,
                rekomendasi_kebijakan TEXT,
                evaluator_skpa VARCHAR(150),
                sumber_database VARCHAR(100),
                waktu_load DATETIME NOT NULL,
                UNIQUE KEY uk_fact_evaluasi (id_evaluasi),
                KEY idx_fact_evaluasi_program (program_key),
                KEY idx_fact_evaluasi_kegiatan (kegiatan_key),
                KEY idx_fact_evaluasi_skpa (skpa_key),
                KEY idx_fact_evaluasi_wilayah (wilayah_key),
                KEY idx_fact_evaluasi_waktu (waktu_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
            """,
        ]

        execute_sql(create_tables)

        # Truncate dimensions
        truncate_dims = [
            f"TRUNCATE TABLE `{dwh_db}`.`dim_perencanaan_waktu`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_perencanaan_skpa`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_perencanaan_wilayah`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_perencanaan_program`;",
            f"TRUNCATE TABLE `{dwh_db}`.`dim_perencanaan_kegiatan`;",
        ]
        execute_sql(truncate_dims)
        logging.info("Truncate dimensions selesai")

        # Load DIM WAKTU (generate 2024-01-01 s/d 2026-12-31)
        load_dim_waktu = []
        bulan_nama = {
            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
            9: "September", 10: "Oktober", 11: "November", 12: "Desember",
        }
        current = pendulum.date(2024, 1, 1)
        end = pendulum.date(2026, 12, 31)
        batch = []
        while current <= end:
            wk = int(current.format("YYYYMMDD"))
            batch.append(f"""
            INSERT INTO `{dwh_db}`.`dim_perencanaan_waktu`
            (waktu_key, tanggal, hari, bulan, nama_bulan, kuartal, tahun, waktu_load)
            VALUES ({wk}, '{current}', {current.day}, {current.month},
                    '{bulan_nama[current.month]}', {current.quarter}, {current.year}, '{now_load}')
            ON DUPLICATE KEY UPDATE waktu_load = VALUES(waktu_load);
            """)
            current = current.add(days=1)
            if len(batch) >= 500:
                load_dim_waktu.extend(batch)
                batch = []
        if batch:
            load_dim_waktu.extend(batch)

        execute_sql(load_dim_waktu)
        logging.info("Load dim_perencanaan_waktu selesai")

        # Load DIM SKPA
        execute_sql([f"""
        INSERT INTO `{dwh_db}`.`dim_perencanaan_skpa`
        (id_skpa, kode_skpa, nama_skpa, bidang_urusan, sumber_database, waktu_load)
        SELECT id_skpa, kode_skpa, nama_skpa, bidang_urusan, sumber_database, '{now_load}'
        FROM `{staging_db}`.`stg_perencanaan_skpa`
        ON DUPLICATE KEY UPDATE
            kode_skpa = VALUES(kode_skpa),
            nama_skpa = VALUES(nama_skpa),
            bidang_urusan = VALUES(bidang_urusan),
            sumber_database = VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """])
        logging.info("Load dim_perencanaan_skpa selesai")

        # Load DIM WILAYAH
        execute_sql([f"""
        INSERT INTO `{dwh_db}`.`dim_perencanaan_wilayah`
        (id_desa, nama_desa, id_kecamatan, nama_kecamatan,
         id_kabupaten_kota, nama_kabupaten_kota, sumber_database, waktu_load)
        SELECT DISTINCT
            id_desa, nama_desa, id_kecamatan, nama_kecamatan,
            id_kabupaten_kota, nama_kabupaten_kota, sumber_database, '{now_load}'
        FROM `{staging_db}`.`stg_perencanaan_kegiatan`
        WHERE id_desa IS NOT NULL AND TRIM(id_desa) <> ''
        ON DUPLICATE KEY UPDATE
            nama_desa = VALUES(nama_desa),
            id_kecamatan = VALUES(id_kecamatan),
            nama_kecamatan = VALUES(nama_kecamatan),
            id_kabupaten_kota = VALUES(id_kabupaten_kota),
            nama_kabupaten_kota = VALUES(nama_kabupaten_kota),
            sumber_database = VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """])
        logging.info("Load dim_perencanaan_wilayah selesai")

        # Load DIM PROGRAM
        execute_sql([f"""
        INSERT INTO `{dwh_db}`.`dim_perencanaan_program`
        (skpa_key, id_program, kode_program, nama_program, bidang_urusan,
         tahun_anggaran, sumber_dana, pagu_anggaran_program, status_program,
         sumber_database, waktu_load)
        SELECT
            dsk.skpa_key,
            sp.id_program, sp.kode_program, sp.nama_program, sp.bidang_urusan,
            sp.tahun_anggaran, sp.sumber_dana, sp.pagu_anggaran_program, sp.status_program,
            sp.sumber_database, '{now_load}'
        FROM `{staging_db}`.`stg_perencanaan_program` sp
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_skpa` dsk
            ON sp.id_skpa = dsk.id_skpa
        ON DUPLICATE KEY UPDATE
            skpa_key = VALUES(skpa_key),
            kode_program = VALUES(kode_program),
            nama_program = VALUES(nama_program),
            bidang_urusan = VALUES(bidang_urusan),
            tahun_anggaran = VALUES(tahun_anggaran),
            sumber_dana = VALUES(sumber_dana),
            pagu_anggaran_program = VALUES(pagu_anggaran_program),
            status_program = VALUES(status_program),
            sumber_database = VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """])
        logging.info("Load dim_perencanaan_program selesai")

        # Load DIM KEGIATAN
        execute_sql([f"""
        INSERT INTO `{dwh_db}`.`dim_perencanaan_kegiatan`
        (program_key, wilayah_key, id_kegiatan, kode_kegiatan, nama_kegiatan,
         pagu_anggaran_kegiatan, tanggal_mulai, tanggal_selesai, status_kegiatan,
         sumber_database, waktu_load)
        SELECT
            dp.program_key,
            dw.wilayah_key,
            sk.id_kegiatan, sk.kode_kegiatan, sk.nama_kegiatan,
            sk.pagu_anggaran_kegiatan, sk.tanggal_mulai, sk.tanggal_selesai, sk.status_kegiatan,
            sk.sumber_database, '{now_load}'
        FROM `{staging_db}`.`stg_perencanaan_kegiatan` sk
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_program` dp
            ON sk.id_program = dp.id_program
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_wilayah` dw
            ON sk.id_desa = dw.id_desa
        ON DUPLICATE KEY UPDATE
            program_key = VALUES(program_key),
            wilayah_key = VALUES(wilayah_key),
            kode_kegiatan = VALUES(kode_kegiatan),
            nama_kegiatan = VALUES(nama_kegiatan),
            pagu_anggaran_kegiatan = VALUES(pagu_anggaran_kegiatan),
            tanggal_mulai = VALUES(tanggal_mulai),
            tanggal_selesai = VALUES(tanggal_selesai),
            status_kegiatan = VALUES(status_kegiatan),
            sumber_database = VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """])
        logging.info("Load dim_perencanaan_kegiatan selesai")

        # Load FACT REALISASI
        execute_sql([f"""
        INSERT INTO `{dwh_db}`.`fact_perencanaan_realisasi`
        (kegiatan_key, program_key, skpa_key, wilayah_key, waktu_key,
         id_realisasi, id_target, tahun, triwulan, indikator_kinerja,
         satuan_fisik, target_fisik_nilai, target_anggaran,
         realisasi_fisik_nilai, realisasi_fisik_persen, realisasi_anggaran,
         serapan_anggaran_persen, kendala_lapangan, is_anomali,
         sumber_database, waktu_load)
        SELECT
            dk.kegiatan_key,
            dp.program_key,
            dsk.skpa_key,
            dw.wilayah_key,
            CAST(DATE_FORMAT(sr.tanggal_lapor, '%Y%m%d') AS UNSIGNED),
            sr.id_realisasi, sr.id_target, st.tahun, sr.triwulan, st.indikator_kinerja,
            st.satuan_fisik, st.target_fisik_nilai, st.target_anggaran,
            sr.realisasi_fisik_nilai, sr.realisasi_fisik_persen, sr.realisasi_anggaran,
            sr.serapan_anggaran_persen, sr.kendala_lapangan, sr.is_anomali,
            sr.sumber_database, '{now_load}'
        FROM `{staging_db}`.`stg_perencanaan_realisasi` sr
        LEFT JOIN `{staging_db}`.`stg_perencanaan_target` st
            ON sr.id_target = st.id_target
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_kegiatan` dk
            ON sr.id_kegiatan = dk.id_kegiatan
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_program` dp
            ON dk.program_key = dp.program_key
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_skpa` dsk
            ON dp.skpa_key = dsk.skpa_key
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_wilayah` dw
            ON dk.wilayah_key = dw.wilayah_key
        ON DUPLICATE KEY UPDATE
            kegiatan_key = VALUES(kegiatan_key),
            program_key = VALUES(program_key),
            skpa_key = VALUES(skpa_key),
            wilayah_key = VALUES(wilayah_key),
            waktu_key = VALUES(waktu_key),
            id_target = VALUES(id_target),
            tahun = VALUES(tahun),
            triwulan = VALUES(triwulan),
            indikator_kinerja = VALUES(indikator_kinerja),
            satuan_fisik = VALUES(satuan_fisik),
            target_fisik_nilai = VALUES(target_fisik_nilai),
            target_anggaran = VALUES(target_anggaran),
            realisasi_fisik_nilai = VALUES(realisasi_fisik_nilai),
            realisasi_fisik_persen = VALUES(realisasi_fisik_persen),
            realisasi_anggaran = VALUES(realisasi_anggaran),
            serapan_anggaran_persen = VALUES(serapan_anggaran_persen),
            kendala_lapangan = VALUES(kendala_lapangan),
            is_anomali = VALUES(is_anomali),
            sumber_database = VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """])
        logging.info("Load fact_perencanaan_realisasi selesai")

        # Load FACT EVALUASI
        execute_sql([f"""
        INSERT INTO `{dwh_db}`.`fact_perencanaan_evaluasi`
        (program_key, kegiatan_key, skpa_key, wilayah_key, waktu_key,
         id_evaluasi, id_realisasi, periode_evaluasi, skor_capaian_kinerja,
         predikat_kinerja, status_tindak_lanjut, catatan_evaluasi,
         rekomendasi_kebijakan, evaluator_skpa, sumber_database, waktu_load)
        SELECT
            dp.program_key,
            dk.kegiatan_key,
            dsk.skpa_key,
            dw.wilayah_key,
            CAST(DATE_FORMAT(se.tanggal_evaluasi, '%Y%m%d') AS UNSIGNED),
            se.id_evaluasi, se.id_realisasi, se.periode_evaluasi, se.skor_capaian_kinerja,
            se.predikat_kinerja, se.status_tindak_lanjut, se.catatan_evaluasi,
            se.rekomendasi_kebijakan, se.evaluator_skpa, se.sumber_database, '{now_load}'
        FROM `{staging_db}`.`stg_perencanaan_evaluasi` se
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_kegiatan` dk
            ON se.id_kegiatan = dk.id_kegiatan
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_program` dp
            ON se.id_program = dp.id_program
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_skpa` dsk
            ON dp.skpa_key = dsk.skpa_key
        LEFT JOIN `{dwh_db}`.`dim_perencanaan_wilayah` dw
            ON dk.wilayah_key = dw.wilayah_key
        ON DUPLICATE KEY UPDATE
            program_key = VALUES(program_key),
            kegiatan_key = VALUES(kegiatan_key),
            skpa_key = VALUES(skpa_key),
            wilayah_key = VALUES(wilayah_key),
            waktu_key = VALUES(waktu_key),
            id_realisasi = VALUES(id_realisasi),
            periode_evaluasi = VALUES(periode_evaluasi),
            skor_capaian_kinerja = VALUES(skor_capaian_kinerja),
            predikat_kinerja = VALUES(predikat_kinerja),
            status_tindak_lanjut = VALUES(status_tindak_lanjut),
            catatan_evaluasi = VALUES(catatan_evaluasi),
            rekomendasi_kebijakan = VALUES(rekomendasi_kebijakan),
            evaluator_skpa = VALUES(evaluator_skpa),
            sumber_database = VALUES(sumber_database),
            waktu_load = VALUES(waktu_load);
        """])
        logging.info("Load fact_perencanaan_evaluasi selesai")

        logging.info("Load ke Data Warehouse selesai.")

    t_extract = extract_to_raw()
    t_transform = transform_staging()
    t_load = load_to_dwh()

    t_extract >> t_transform >> t_load

    return t_load