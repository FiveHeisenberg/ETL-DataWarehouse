#!/bin/bash
export INFRASTRUKTUR_DB_HOST="127.0.0.1"
export INFRASTRUKTUR_DB_PORT="3306"
export INFRASTRUKTUR_DB_USER="root"
export INFRASTRUKTUR_DB_PASSWORD="GANTI_PASSWORD_MYSQL"
export INFRASTRUKTUR_DB_NAME="db_infrastruktur"
uvicorn main:app --host 0.0.0.0 --port 8000
