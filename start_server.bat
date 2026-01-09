@echo off
echo ================================================
echo FloorPlan To 3D Analyzer - Starting Server
echo ================================================
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found at .venv
    echo Please create one with: python -m venv .venv
    pause
    exit /b 1
)

REM Set environment variable for Keras compatibility
set TF_USE_LEGACY_KERAS=1

echo.
echo Starting Flask server on http://localhost:5000
echo.
echo To use the application:
echo   1. Keep this window open
echo   2. Open frontend.html in your web browser
echo   3. Upload a floor plan image to analyze
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

REM Start the Flask application
python application.py

pause
