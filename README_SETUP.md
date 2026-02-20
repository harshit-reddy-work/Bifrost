# CloudRoom Flask Application - Setup Instructions

## Current Status
✅ All dependencies are installed in the virtual environment
⚠️ The virtual environment was created with a different user's Python path

## Quick Start Options

### Option 1: Use the Run Scripts (Recommended)
I've created two run scripts for you:

**For PowerShell:**
```powershell
.\run.ps1
```

**For Command Prompt:**
```cmd
run.bat
```

These scripts will automatically detect and use the correct Python installation.

### Option 2: Manual Start

1. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Run the application:**
   ```powershell
   python app.py
   ```

### Option 3: Fix Virtual Environment (If Option 1 doesn't work)

If the virtual environment Python path is incorrect, you can recreate it:

1. **Delete the existing venv:**
   ```powershell
   Remove-Item -Recurse -Force venv
   ```

2. **Create a new virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate and install dependencies:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   python app.py
   ```

## Application Details

- **Port:** 5000
- **URL:** http://localhost:5000
- **Debug Mode:** Enabled

## Dependencies Installed

- Flask==2.3.3
- Flask-SQLAlchemy==3.0.3
- Flask-Migrate==4.0.4
- Flask-Login==0.6.3
- python-dotenv==1.0.0

## Troubleshooting

If you encounter "Python not found" errors:
1. Install Python 3.8 or higher from https://www.python.org/downloads/
2. Make sure Python is added to your system PATH
3. Restart your terminal/command prompt after installation
