#!/bin/bash

# Trellis 3D Enhancement Tool - Setup Script
# Optimized for Python 3.10+ and CUDA 12.x
# This script sets up the environment and installs all dependencies

set -e  # Exit on error

echo "=========================================="
echo "Trellis 3D Enhancement Tool - Setup"
echo "Python 3.10+ | CUDA 12.x optimized"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
echo "✓ Python version: $python_version"

# Check if Python version is 3.10 or higher (recommended)
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✓ Python 3.10+ detected (recommended)"
elif python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "⚠ Python 3.8-3.9 detected. Python 3.10+ is recommended for best compatibility."
else
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

echo ""

# Ask about virtual environment
read -p "Create virtual environment? (recommended) [Y/n]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "✓ Virtual environment created and activated"
    echo "  To activate later, run: source venv/bin/activate"
else
    echo "Skipping virtual environment creation"
fi

echo ""

# Upgrade pip and install build tools
echo "Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

echo ""

# Detect CUDA version
echo "=========================================="
echo "Detecting CUDA version..."
echo "=========================================="
echo ""

CUDA_VERSION=""
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1
    
    # Try to detect CUDA version
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep -oP 'release \K[0-9]+\.[0-9]+' | head -1)
        echo "CUDA version detected: $CUDA_VERSION"
    else
        echo "nvcc not found, checking nvidia-smi..."
        CUDA_VERSION=$(nvidia-smi | grep -oP 'CUDA Version: \K[0-9]+\.[0-9]+' | head -1)
        if [ -n "$CUDA_VERSION" ]; then
            echo "CUDA version from nvidia-smi: $CUDA_VERSION"
        fi
    fi
fi

# Determine PyTorch installation command
echo ""
echo "=========================================="
echo "Installing PyTorch..."
echo "=========================================="
echo ""

if [ -n "$CUDA_VERSION" ]; then
    # Convert CUDA version to major version
    CUDA_MAJOR=$(echo "$CUDA_VERSION" | cut -d. -f1)
    
    if [ "$CUDA_MAJOR" -ge 12 ]; then
        echo "Installing PyTorch with CUDA 12.1 support..."
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
    elif [ "$CUDA_MAJOR" -eq 11 ]; then
        echo "Installing PyTorch with CUDA 11.8 support..."
        pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
    else
        echo "⚠ CUDA version $CUDA_VERSION detected. Installing CPU version."
        pip install torch torchvision
    fi
else
    echo "No NVIDIA GPU detected or CUDA not available."
    echo "Installing CPU-only PyTorch..."
    pip install torch torchvision
fi

echo ""

# Install core dependencies
echo "=========================================="
echo "Installing core dependencies..."
echo "=========================================="
echo ""

pip install -r requirements.txt

echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p weights
mkdir -p output
mkdir -p logs

echo "✓ Directories created"

echo ""

# Choose texture enhancement backend
echo "=========================================="
echo "Texture Enhancement Backend"
echo "=========================================="
echo ""
echo "Current setup uses ISR (lightweight, easy to install)"
echo ""
read -p "Do you want to install Real-ESRGAN instead? (better quality but more dependencies) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Real-ESRGAN and dependencies..."
    pip install realesrgan==0.3.0 basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8
    echo "✓ Real-ESRGAN installed"
else
    echo "Using ISR (already installed)"
fi

echo ""

# Test installation
echo "=========================================="
echo "Testing installation..."
echo "=========================================="
echo ""

python3 << 'EOF'
import sys
print(f"Python version: {sys.version}")

try:
    import torch
    print(f"✓ PyTorch {torch.__version__}")
    print(f"✓ CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"✓ CUDA version: {torch.version.cuda}")
        print(f"✓ GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"⚠ PyTorch check failed: {e}")

try:
    import pymeshlab
    print(f"✓ PyMeshLab installed")
except Exception as e:
    print(f"⚠ PyMeshLab check failed: {e}")

try:
    from ISR.models import RDN
    print(f"✓ ISR installed")
except:
    try:
        from realesrgan import RealESRGANer
        print(f"✓ Real-ESRGAN installed")
    except:
        print(f"⚠ No texture enhancement backend found")

print("\nInstallation test complete!")
EOF

echo ""

# Optional: Install Stable Diffusion dependencies
echo ""
read -p "Install Stable Diffusion dependencies? (enables --use-sd option) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Stable Diffusion dependencies..."
    pip install diffusers>=0.24.0 transformers>=4.35.0 accelerate>=0.24.0 safetensors>=0.4.0
    echo "✓ Stable Diffusion dependencies installed"
else
    echo "Skipping Stable Diffusion installation"
    echo "  You can install later with: pip install diffusers transformers accelerate"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Quick Start:"
echo "  1. Activate environment (if using venv): source venv/bin/activate"
echo "  2. Run enhancement: python enhance.py --input model.glb --output enhanced/"
echo "  3. Get help: python enhance.py --help"
echo ""
echo "Examples:"
echo "  python enhance.py --input model.glb --output enhanced/"
echo "  python enhance.py --input model.ply --output enhanced/ --texture-scale 2"
echo "  python enhance.py --input model.obj --output enhanced/ --no-geometry"
echo ""
echo "For more information, see README.md"
echo ""
