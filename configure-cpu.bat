@echo off
setlocal enabledelayedexpansion

set script_path=%~dp0
cd /d "%script_path%"

set log_file="%~dp0cpu_installation_errors.log"
> %log_file% echo Script started at %date% %time%

call :log "Script starting."

python --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "Python is not installed. Downloading Python installer..."

    curl -L -o "%~dp0python-3.12.3-amd64.exe" https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe >> %log_file% 2>&1

    if not exist "%~dp0python-3.12.3-amd64.exe" (
        call :log "Failed to download Python installer. Exiting."
        pause
        exit /b 1
    )

    call :log "Installing Python as administrator..."
    powershell -Command "Start-Process '%~dp0python-3.12.3-amd64.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1' -Verb RunAs" >> %log_file% 2>&1
    python --version >nul 2>>%log_file%
    if errorlevel 1 (
        call :log "Python installation failed. Exiting."
        pause
        exit /b 1
    )
)

python --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "Python installation failed. Please install Python manually: https://www.python.org/"
    pause
    exit /b 1
)

pip --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "pip not found. Installing pip..."
    python -m ensurepip --upgrade >> %log_file% 2>&1
    python -m pip install --upgrade pip >> %log_file% 2>&1
    if errorlevel 1 (
        call :log "Failed to install pip. Exiting."
        pause
        exit /b 1
    )
)

call :log "Installing Python dependencies (CPU-only PyTorch)..."
powershell -Command "Start-Process python -ArgumentList '-m pip install --upgrade torch torchvision transformers diffusers ollama streamlit easygui' -Verb RunAs" >> %log_file% 2>&1
if errorlevel 1 (
    call :log "Failed to install Python dependencies. Exiting."
    pause
    exit /b 1
)

call :log "Launching RYFAI..."
streamlit run "%~dp0ryfai.py" >> %log_file% 2>&1
if errorlevel 1 (
    call :log "Failed to launch RYFAI. Exiting."
    pause
    exit /b 1
)

call :log "Script completed successfully."
pause
exit /b 0

:log
    echo [%time%] %~1 >> %log_file%
    echo %~1
    goto :eof
