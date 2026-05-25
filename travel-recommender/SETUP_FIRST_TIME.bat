@echo off
echo ========================================
echo   TRAVEL RECOMMENDER - FIRST TIME SETUP
echo ========================================
echo.

echo [1/3] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies!
    pause
    exit /b 1
)

echo.
echo [2/3] Testing Data Loading...
python mining/preprocess.py
if errorlevel 1 (
    echo WARNING: Data loading test failed, but continuing...
)

echo.
echo [3/3] Installing Frontend Dependencies...
cd ../frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies!
    pause
    exit /b 1
)

cd ..
echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run START_BACKEND.bat
echo 2. Run START_FRONTEND.bat
echo 3. Open http://localhost:3000
echo.
pause
