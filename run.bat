@echo off
echo Starting CloudRoom Flask Application...
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    echo Using virtual environment Python...
    venv\Scripts\python.exe app.py
) else (
    echo Virtual environment Python not found. Trying system Python...
    python app.py
    if errorlevel 1 (
        echo Error: Python not found. Please install Python 3.8+ and try again.
        echo You can download Python from https://www.python.org/downloads/
        pause
    )
)
