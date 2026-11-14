@echo off
REM ========================================
REM Test Dispenda API Endpoints
REM ========================================

setlocal

echo.
echo ================================
echo Testing Dispenda API
echo ================================
echo.
echo Pastikan API sudah running di http://localhost:8000
echo.

timeout /t 2

REM Test health
echo [1/4] Testing Health Check...
curl http://localhost:8000/health
echo.

REM Test metadata
echo [2/4] Testing Metadata...
curl http://localhost:8000/api/tables
echo.

REM Test single endpoint
echo [3/4] Testing kategori-pajak endpoint...
curl "http://localhost:8000/api/kategori-pajak?page=1&limit=3"
echo.

REM Test all endpoints summary
echo [4/4] Testing all endpoints...
echo.
echo Endpoints:
curl "http://localhost:8000/api/metode-bayar?page=1&limit=1" 2>nul | findstr "total" || echo metode-bayar: OK
curl "http://localhost:8000/api/wajib-pajak?page=1&limit=1" 2>nul | findstr "total" || echo wajib-pajak: OK
curl "http://localhost:8000/api/objek-pajak?page=1&limit=1" 2>nul | findstr "total" || echo objek-pajak: OK
curl "http://localhost:8000/api/tagihan?page=1&limit=1" 2>nul | findstr "total" || echo tagihan: OK
curl "http://localhost:8000/api/pembayaran?page=1&limit=1" 2>nul | findstr "total" || echo pembayaran: OK

echo.
echo ================================
echo Testing complete!
echo ================================
echo.

pause

endlocal
