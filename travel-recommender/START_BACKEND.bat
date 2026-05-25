@echo off
echo ========================================
echo   TRAVEL RECOMMENDER - BACKEND
echo ========================================
echo.

cd backend

echo [1/2] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/2] Starting Backend Server...
echo.
echo API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.

python main.py

pause
