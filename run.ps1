# Flask Application Startup Script
# This script starts the CloudRoom Flask application

Write-Host "Starting CloudRoom Flask Application..." -ForegroundColor Green

# Change to the application directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Try to use venv Python if it exists and is valid
$venvPython = Join-Path $scriptPath "venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Using virtual environment Python..." -ForegroundColor Yellow
    & $venvPython app.py
} else {
    Write-Host "Virtual environment Python not found. Trying system Python..." -ForegroundColor Yellow
    
    # Try system Python
    try {
        python app.py
    } catch {
        Write-Host "Error: Python not found. Please install Python 3.8+ and try again." -ForegroundColor Red
        Write-Host "You can download Python from https://www.python.org/downloads/" -ForegroundColor Yellow
        pause
    }
}
