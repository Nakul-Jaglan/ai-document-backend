@echo off
REM Django Backend Server Startup Script for Windows

echo Starting Django Backend Server...

REM Navigate to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists and activate it
if exist ".venv" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo Installing/updating dependencies...
    python -m pip install -r requirements.txt
)

REM Run migrations
echo Running database migrations...
python manage.py migrate

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Start the development server
echo Starting Django development server at http://127.0.0.1:8000/
echo Press CTRL+C to stop the server
python manage.py runserver

pause