@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if not exist "backend\venv\Scripts\python.exe" (
  echo LOI: Khong tim thay backend\venv\Scripts\python.exe.
  exit /b 2
)

"backend\venv\Scripts\python.exe" "backend\scripts\reset_demo.py"
if errorlevel 1 (
  echo Dat lai du lieu demo that bai.
  exit /b 1
)

echo Dat lai du lieu demo thanh cong.
exit /b 0
