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
install_cuda_with_apt() {
    echo "Using apt for CUDA installation."
    sudo apt purge nvidia* -y
    sudo apt autoremove -y && sudo apt autoclean -y
    sudo rm -rf /usr/local/cuda*
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y g++ freeglut3-dev build-essential libx11-dev libxmu-dev libxi-dev libglu1-mesa libglu1-mesa-dev
    sudo add-apt-repository ppa:graphics-drivers/ppa -y
    sudo apt update
    sudo apt install -y libnvidia-common-515 libnvidia-gl-515 nvidia-driver-515
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
    sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
    sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" -y
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y cuda-11-8
    sudo apt install nvidia-cuda-toolkit -y
    sudo apt install python3 python3-pip -y
}

# Function to install CUDA with yum or dnf
install_cuda_with_dnf_or_yum() {
    echo "Using yum/dnf for CUDA installation."
    sudo yum remove nvidia* -y || sudo dnf remove nvidia* -y
    sudo yum update -y || sudo dnf update -y
    sudo yum groupinstall "Development Tools" -y || sudo dnf groupinstall "Development Tools" -y
    sudo yum install -y kernel-devel epel-release || sudo dnf install -y kernel-devel epel-release
    sudo yum-config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-rhel7.repo || \
        sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-rhel7.repo
    sudo yum install -y cuda || sudo dnf install -y cuda
    sudo yum install -y nvidia-cuda-toolkit || sudo dnf install -y nvidia-cuda-toolkit
    sudo yum install -y python3 python3-pip 
}

# Function to install CUDA with pacman
install_cuda_with_pacman() {
    echo "Using pacman for CUDA installation."
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm nvidia nvidia-utils cuda nvidia-cuda-toolkit
    sudo pacman -S --noconfirm python3 python3-pip
}

# Main function
main() {
    PACKAGE_MANAGER=$(detect_package_manager)

    case $PACKAGE_MANAGER in
        apt)
            install_cuda_with_apt
            ;;
        yum|dnf)
            install_cuda_with_dnf_or_yum
            ;;
        pacman)
            install_cuda_with_pacman
            ;;
        *)
            echo "Unsupported package manager: $PACKAGE_MANAGER"
            exit 1
            ;;
    esac

    echo -e "\nCUDA installation completed. Verifying..."
    nvidia-smi || echo "nvidia-smi not found or failed."
    nvcc --version || echo "nvcc not found or failed."
    echo -e "\nInstalling Ollama..."
    curl -fSsL https://ollama.com/install.sh | sh
    pip3 install easygui pyinstaller torch torchvision torchaudio transformers streamlit ollama diffusers --upgrade
}

main
