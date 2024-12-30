#!/bin/bash

# Function to detect package manager
detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    else
        echo "unsupported"
    fi
}

# Function to install CUDA with apt
install_python_with_apt() {
    sudo apt update && sudo apt upgrade -y
    sudo apt install python3 python3-pip -y
}

# Function to install CUDA with yum or dnf
install_python_with_dnf_or_yum() {
    sudo yum update -y || sudo dnf update -y
    sudo yum install -y python3 python3-pip 
}

# Function to install CUDA with pacman
install_python_with_pacman() {
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm nvidia nvidia-utils cuda nvidia-cuda-toolkit
    sudo pacman -S --noconfirm python3 python3-pip
}

# Main function
main() {
    PACKAGE_MANAGER=$(detect_package_manager)

    case $PACKAGE_MANAGER in
        apt)
            install_python_with_apt
            ;;
        yum|dnf)
            install_python_with_dnf_or_yum
            ;;
        pacman)
            install_python_with_pacman
            ;;
        *)
            echo "Unsupported package manager: $PACKAGE_MANAGER"
            exit 1
            ;;
    esac

    echo -e "\nInstalling Ollama..."
    curl -fSsL https://ollama.com/install.sh | sh
    pip3 install easygui pyinstaller torch torchvision torchaudio transformers streamlit ollama diffusers --upgrade
}

main
