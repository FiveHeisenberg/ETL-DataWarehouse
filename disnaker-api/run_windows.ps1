$env:DISNAKER_DB_HOST="127.0.0.1"
$env:DISNAKER_DB_PORT="3306"
$env:DISNAKER_DB_USER="root"
$env:DISNAKER_DB_PASSWORD="GANTI_PASSWORD_MYSQL"
$env:DISNAKER_DB_NAME="db_disnaker"
uvicorn main:app --host 0.0.0.0 --port 8000
