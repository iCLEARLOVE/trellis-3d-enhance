#!/bin/bash

# Trellis 3D Enhancement Tool - Setup Script
# This script sets up the environment and installs all dependencies

set -e  # Exit on error

echo "=========================================="
echo "Trellis 3D Enhancement Tool - Setup"
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

# Check if Python version is 3.8 or higher
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

echo ""

# Ask about virtual environment
read -p "Create virtual environment? (recommended) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
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

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

echo ""

# Install PyTorch with CUDA support
echo "=========================================="
echo "Installing PyTorch with CUDA support..."
echo "=========================================="
echo ""

# Detect CUDA availability
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected"
    nvidia-smi --query-gpu=name --format=csv,noheader | head -n 1
    
    # Install PyTorch with CUDA 11.8 support
    echo "Installing PyTorch with CUDA 11.8..."
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
else
    echo "No NVIDIA GPU detected, installing CPU-only PyTorch"
    pip install torch torchvision
fi

echo ""

# Install other dependencies
echo "=========================================="
echo "Installing other dependencies..."
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

# Download pretrained weights
echo "=========================================="
echo "Downloading pretrained weights..."
echo "=========================================="
echo ""

python3 << 'EOF'
try:
    from src.texture_enhancer import TextureEnhancer
    enhancer = TextureEnhancer()
    print("✓ Real-ESRGAN weights downloaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not download weights automatically: {e}")
    print("  Weights will be downloaded on first use")
EOF

echo ""

# Optional: Install Stable Diffusion dependencies
echo ""
read -p "Install Stable Diffusion dependencies? (enables --use-sd option) [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Stable Diffusion dependencies..."
    pip install diffusers>=0.21.0 transformers>=4.30.0 accelerate>=0.20.0
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
echo "  python enhance.py --input model.glb --output enhanced/ --texture-scale 2"
echo "  python enhance.py --input model.glb --output enhanced/ --use-sd"
echo ""
