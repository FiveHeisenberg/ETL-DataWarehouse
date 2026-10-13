# PowerShell script to run ketaben API
# Usage: .\run_windows.ps1

Write-Host "Starting db_ketaben REST API..." -ForegroundColor Green

# Load .env file if exists
if (Test-Path .env) {
    Write-Host "Loading environment variables from .env file..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "  $name = $value" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "Starting uvicorn server..." -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
