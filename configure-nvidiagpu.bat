@echo off
setlocal enabledelayedexpansion

:: Ensure the script runs from its directory
set script_path=%~dp0
cd /d "%script_path%"

:: Prevent running from System32 directory
if /i "%script_path%"=="C:\\Windows\\System32\\" (
    echo This script cannot be run from System32. Please run it from a different directory.
    pause
    exit /b 1
)

:: Display the current working directory
echo Current working directory: %cd%

:: Redirect error output to a log file
set log_file="%~dp0script_errors.log"
> %log_file% echo Script started at %date% %time%

:: Helper function for logging progress
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
    powershell -Command "Add-AppxPackage -Path '%~dp0AppInstaller.msixbundle'" >> %log_file% 2>&1
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
    winget install -e --id Rustlang.Rustup >> %log_file% 2>&1
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
    winget install -e --id Ollama.Ollama >> %log_file% 2>&1
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

    :: Download Python installer
    curl -L -o "%~dp0python-3.12.3-amd64.exe" https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe >> %log_file% 2>&1
    if not exist "%~dp0python-3.12.3-amd64.exe" (
        call :log "Failed to download Python installer. Exiting."
        pause
        exit /b 1
    )

    :: Run Python installer as administrator
    call :log "Installing Python as administrator..."
    powershell -Command "Start-Process '%~dp0python-3.12.3-amd64.exe' -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1' -Verb RunAs" >> %log_file% 2>&1
    python --version >nul 2>>%log_file%
    if errorlevel 1 (
        call :log "Python installation failed. Exiting."
        pause
        exit /b 1
    )
)

:: Check if CUDA is installed
nvcc --version >nul 2>>%log_file%
if errorlevel 1 (
    call :log "CUDA is not installed. Downloading CUDA 11.8 installer..."
    curl -L -o "%~dp0cuda_11.8.exe" https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_windows.exe >> %log_file% 2>&1
    if not exist "%~dp0cuda_11.8.exe" (
        call :log "Failed to download CUDA installer. Exiting."
        pause
        exit /b 1
    )

    call :log "Installing CUDA as administrator..."
    powershell -Command "Start-Process '%~dp0cuda_11.8.exe' -ArgumentList '-s' -Verb RunAs" >> %log_file% 2>&1
    nvcc --version >nul 2>>%log_file%
    if errorlevel 1 (
        call :log "CUDA installation failed. Exiting."
        pause
        exit /b 1
    )
) else (
    call :log "CUDA is already installed."
)

:: Install Python dependencies
call :log "Installing Python dependencies..."
powershell -Command "Start-Process python -ArgumentList '-m pip install --upgrade torch torchvision transformers diffusers ollama streamlit easygui --extra-index-url https://download.pytorch.org/whl/cpu' -Verb RunAs" >> %log_file% 2>&1
if errorlevel 1 (
    call :log "Failed to install Python dependencies. Exiting."
    pause
    exit /b 1
)

:: Launch RYFAI
call :log "Launching RYFAI..."
streamlit run "%~dp0ryfai.py" >> %log_file% 2>&1
if errorlevel 1 (
    call :log "RYFAI launch failed. Exiting."
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

