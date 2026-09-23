@echo off
title Astro Airflow Network

cd /d "%~dp0"

echo ============================================
echo       STARTING ASTRO AIRFLOW
echo ============================================
echo.

astro dev start

echo.
echo Astro Airflow sudah dijalankan.
echo.

echo Menunggu Airflow...
timeout /t 5 /nobreak

echo.
echo Status Airflow:
astro dev ps

echo.
echo ============================================
echo       AIRFLOW NETWORK ACCESS
echo ============================================
echo.
echo Buka dari komputer lain:
echo http://192.168.222.152:8080/
echo.
echo ============================================
echo.
echo Window ini akan tetap terbuka.
echo Tekan CTRL+C jika ingin menghentikan script.
echo.

cmd /k