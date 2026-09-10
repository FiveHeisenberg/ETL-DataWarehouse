from __future__ import annotations

import logging

import pendulum

from airflow.sdk import dag, task
from airflow.providers.mysql.hooks.mysql import MySqlHook


# ============================================================
# KONFIGURASI
# ============================================================

MYSQL_CONN_ID = "mysql_warehouse"
RAW_DB = "raw_data"
STAGING_DB = "staging_area"
DWH_DB = "dwh"

# ============================================================
# DATA SOURCES
#
# Untuk menambah source baru:
# 1. Buat file baru di dags/ (misal: kesehatan.py)
# 2. Definisikan fungsi create_<nama>_tasks() di dalamnya
# 3. Import di bawah ini
# 4. Tambahkan entry ke list PIPELINE_TASKS
#    beserta api_base_url source masing-masing
# ============================================================

from dukcapil import create_dukcapil_tasks

PIPELINE_TASKS = [
    {
        "name": "dukcapil",
        "create_tasks": create_dukcapil_tasks,
        "api_base_url": "http://192.168.222.152:8000/api",
    },
    # Contoh source baru dengan IP berbeda:
    # {
    #     "name": "kependudukan",
    #     "create_tasks": create_kependudukan_tasks,
    #     "api_base_url": "http://10.0.0.35:8080/api",
    # },
]


# ============================================================
# UTILITIES
# ============================================================

def get_mysql_hook():
    return MySqlHook(mysql_conn_id=MYSQL_CONN_ID)


def execute_sql(statements):
    """
    Menjalankan sekumpulan SQL dalam satu koneksi.
    """
    hook = get_mysql_hook()
    conn = hook.get_conn()
    cursor = conn.cursor()

    try:
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


# ============================================================
# DAG
# ============================================================

@dag(
    dag_id="ETL-Warehouse",
    description="ETL API -> raw_data -> staging_area -> dwh",
    start_date=pendulum.datetime(
        2026, 9, 7,
        tz="Asia/Jakarta"
    ),
    schedule=None,
    catchup=False,
    tags=["magang", "etl", "data-warehouse"],
)
def etl_dukcapil_to_dwh():

    # ========================================================
    # TASK: MEMBUAT DATABASE RAW_DATA
    # ========================================================

    @task
    def create_raw_database():

        logging.info("Memeriksa database raw_data...")

        sql = f"""
        CREATE DATABASE IF NOT EXISTS `{RAW_DB}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        execute_sql([sql])

        logging.info(
            "Database %s tersedia.",
            RAW_DB
        )

    # ========================================================
    # TASK: MEMBUAT DATABASE STAGING
    # ========================================================

    @task
    def create_staging_database():

        logging.info("Memeriksa database staging_area...")

        sql = f"""
        CREATE DATABASE IF NOT EXISTS `{STAGING_DB}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        execute_sql([sql])

        logging.info(
            "Database %s tersedia.",
            STAGING_DB
        )

    # ========================================================
    # TASK: MEMBUAT DATABASE DWH
    # ========================================================

    @task
    def create_dwh_database():

        logging.info("Memeriksa database dwh...")

        sql = f"""
        CREATE DATABASE IF NOT EXISTS `{DWH_DB}`
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_0900_ai_ci;
        """

        execute_sql([sql])

        logging.info(
            "Database %s tersedia.",
            DWH_DB
        )

    # ========================================================
    # SHARED SETUP TASKS
    # ========================================================

    t_raw = create_raw_database()
    t_staging = create_staging_database()
    t_dwh = create_dwh_database()

    t_raw >> t_staging >> t_dwh

    # ========================================================
    # DATA SOURCE PIPELINES
    #
    # Setiap source punya api_base_url sendiri.
    # create_*_tasks() mengembalikan task terakhir dari
    # pipeline-nya, lalu di-chain secara berurutan.
    # ========================================================

    shared_kwargs = dict(
        execute_sql=execute_sql,
        get_mysql_hook=get_mysql_hook,
        raw_db=RAW_DB,
        staging_db=STAGING_DB,
        dwh_db=DWH_DB,
    )

    prev_task = t_dwh

    for source in PIPELINE_TASKS:

        logging.info(
            "Membuat pipeline untuk source %s...",
            source["name"],
        )

        source_kwargs = {
            **shared_kwargs,
            "api_base_url": source["api_base_url"],
        }

        current_task = source["create_tasks"](**source_kwargs)

        prev_task >> current_task
        prev_task = current_task


etl_dukcapil_to_dwh()