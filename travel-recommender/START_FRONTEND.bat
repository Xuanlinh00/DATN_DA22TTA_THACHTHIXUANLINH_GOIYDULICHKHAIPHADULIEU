@echo off
echo ========================================
echo   TRAVEL RECOMMENDER - FRONTEND
echo ========================================
echo.

cd frontend

echo [1/2] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)

echo.
echo [2/2] Starting Frontend Server...
echo.
echo App will be available at: http://localhost:3000
echo.

npm start

pause
