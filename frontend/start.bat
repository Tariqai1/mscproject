@echo off
REM Start React Frontend Development Server

echo.
echo ======================================
echo Sarcasm-Aware Sentiment Analysis UI
echo ======================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 14.0+ from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed
    echo Please install Node.js and npm
    echo.
    pause
    exit /b 1
)

REM Check if node_modules exist
if not exist "node_modules" (
    echo.
    echo Installing dependencies...
    echo This may take a few minutes on first run...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Display startup info
echo.
echo Starting React development server...
echo.
echo Application URL: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the development server
call npm start

pause