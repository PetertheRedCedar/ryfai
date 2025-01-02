@echo off
setlocal enabledelayedexpansion

set script_path=%~dp0
cd /d "%script_path%"

set log_file="%~dp0cpu_installation_errors.log"
> %log_file% echo Script started at %date% %time%

call :log "Script starting."

:: Check if Winget is installed
winget --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "Winget is not installed. Downloading and installing Winget..."
    
    :: Download the Winget installer
    curl -L -o "%~dp0AppInstaller.msixbundle" https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle >> %log_file% 2>&1

    if not exist "%~dp0AppInstaller.msixbundle" (
        call :log "Failed to download Winget installer. Exiting."
        pause
        exit /b 1
    )
    
    :: Install Winget
    call :log "Installing Winget..."
    powershell -Command "Start-Process -Wait powershell -ArgumentList 'Add-AppxPackage -Path \"%~dp0AppInstaller.msixbundle\"' -Verb RunAs" >> %log_file% 2>&1
    winget --version >nul 2>>%log_file%
    if errorlevel 1 (
        call :log "Winget installation failed. Exiting."
        pause
        exit /b 1
    )
) else (
    call :log "Winget is already installed."
)

:: Install Rust using Winget
call :log "Checking if Rust is installed..."
rustc --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "Rust is not installed. Installing Rust using Winget..."
    echo Installing Rust...
    winget install -e --id Rustlang.Rustup --interactive
    rustc --version >nul 2>>%log_file%
    if errorlevel 1 (
        call :log "Failed to install Rust. Exiting."
        pause
        exit /b 1
    )
) else (
    call :log "Rust is already installed."
)

:: Install Ollama using Winget
call :log "Checking if Ollama is installed..."
ollama --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "Ollama is not installed. Installing Ollama using Winget..."
    echo Installing Ollama...
    winget install -e --id Ollama.Ollama --interactive
    ollama --version >nul 2>>%log_file%
    if errorlevel 1 (
        call :log "Failed to install Ollama. Exiting."
        pause
        exit /b 1
    )
) else (
    call :log "Ollama is already installed."
)

:: Check if Python is installed
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

:: Ensure pip is installed
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

:: Install Python dependencies
call :log "Installing Python dependencies (CPU-only PyTorch)..."
powershell -Command "Start-Process python -ArgumentList '-m pip install --upgrade torch torchvision transformers diffusers ollama streamlit easygui' -Verb RunAs" >> %log_file% 2>&1
if errorlevel 1 (
    call :log "Failed to install Python dependencies. Exiting."
    pause
    exit /b 1
)

:: Launch RYFAI
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
