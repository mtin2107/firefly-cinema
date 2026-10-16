@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if not exist "backend\venv\Scripts\python.exe" (
  echo LOI: Khong tim thay moi truong backend.
  exit /b 2
)
if not exist "frontend\package.json" (
  echo LOI: Khong tim thay frontend\package.json.
  exit /b 2
)

start "Firefly Cinema - Backend" cmd /k "cd /d ""%~dp0backend"" && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
start "Firefly Cinema - Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

echo Dang cho backend va model PhoBERT san sang...
powershell -NoProfile -Command "$deadline=(Get-Date).AddMinutes(3); do { try { $h=Invoke-RestMethod -Uri 'http://localhost:8000/api/health' -TimeoutSec 3; if ($h.classifier -like 'phobert*') { Write-Host ('Backend san sang: classifier=' + $h.classifier); exit 0 } } catch {} Start-Sleep -Seconds 2 } while ((Get-Date) -lt $deadline); Write-Error 'Backend chua bao classifier PhoBERT sau 3 phut.'; exit 1"
if errorlevel 1 (
  echo Hay xem cua so Backend de biet chi tiet loi model.
  exit /b 1
)

echo Firefly Cinema da san sang tai http://localhost:5173
exit /b 0
