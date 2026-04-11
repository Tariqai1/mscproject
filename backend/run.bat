@echo off
REM Start FastAPI Backend Server

echo.
echo ======================================
echo Sarcasm-Aware Sentiment Analysis API
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking for required packages...
python -c "import fastapi, uvicorn, sqlalchemy" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Required packages not installed
    echo Please run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Display startup info
echo.
echo Starting FastAPI server...
echo.
echo API Documentation: http://localhost:8000/docs
echo Alternative Docs:  http://localhost:8000/redoc
echo Health Check:      http://localhost:8000/api/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause