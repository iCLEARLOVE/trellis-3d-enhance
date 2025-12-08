# Installation Guide

Comprehensive installation guide for Trellis 3D Model Enhancement Tool.

## System Requirements

### Hardware
- **GPU**: NVIDIA GPU with 8GB+ VRAM (recommended: A6000, RTX 3090, RTX 4090)
- **CPU**: Modern multi-core processor (fallback if no GPU)
- **RAM**: 16GB+ recommended
- **Storage**: 10GB free space (for dependencies and model weights)

### Software
- **Python**: 3.10 or higher (3.10, 3.11, 3.12 supported)
- **CUDA**: 12.x recommended (11.8+ supported)
- **OS**: Linux (tested), macOS, Windows with WSL2

## Quick Installation

### Method 1: Automatic Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance

# Run the automated setup script
bash setup.sh
```

The script will:
- ✅ Check Python version (3.10+ recommended)
- ✅ Create virtual environment (optional)
- ✅ Detect CUDA version automatically
- ✅ Install PyTorch with appropriate CUDA support
- ✅ Install all dependencies
- ✅ Set up project directories
- ✅ Test the installation

### Method 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Upgrade pip
pip install --upgrade pip setuptools wheel

# 4. Install PyTorch (choose based on your CUDA version)

# For CUDA 12.x:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CPU only:
pip install torch torchvision

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create directories
mkdir -p weights output logs
```

## Texture Enhancement Backend

Choose one of the following backends:

### Option 1: ISR (Recommended for Easy Setup)

**Pros:**
- ✅ Easy to install, no complex dependencies
- ✅ Works out of the box
- ✅ Good quality results

**Installation:**
```bash
pip install ISR==2.2.0
```

This is the default in `requirements.txt`.

### Option 2: Real-ESRGAN (Best Quality)

**Pros:**
- ✅ Best quality results
- ✅ Industry-standard upscaling

**Cons:**
- ⚠️ More complex dependencies (basicsr)
- ⚠️ May have installation issues on some systems

**Installation:**
```bash
pip install realesrgan==0.3.0 basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8
```

**Note:** The tool automatically detects which backend is available and uses it.

## Optional: Stable Diffusion Enhancement

For advanced texture enhancement with Stable Diffusion ControlNet:

```bash
pip install diffusers>=0.24.0 transformers>=4.35.0 accelerate>=0.24.0 safetensors>=0.4.0
```

This enables the `--use-sd` option for maximum quality.

## Verification

Test your installation:

```bash
python3 << 'EOF'
import sys
import torch

print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Test imports
try:
    import pymeshlab
    print("✓ PyMeshLab OK")
except:
    print("✗ PyMeshLab FAILED")

try:
    from ISR.models import RDN
    print("✓ ISR OK")
except:
    print("⚠ ISR not installed")

try:
    from realesrgan import RealESRGANer
    print("✓ Real-ESRGAN OK")
except:
    print("⚠ Real-ESRGAN not installed")
EOF
```

## Dependency Version Matrix

Compatible versions tested for Python 3.10 with CUDA 12.1:

| Package | Version | Notes |
|---------|---------|-------|
| Python | 3.10, 3.11, 3.12 | 3.10+ recommended |
| CUDA | 11.8, 12.1, 12.4 | 12.1+ recommended |
| PyTorch | 2.0.0 - 2.2.0 | Auto-installed |
| pymeshlab | 2022.2.post4 | Mesh processing |
| trimesh | 4.0.10 | 3D format support |
| numpy | 1.24.0 - 1.26.4 | <2.0 for compatibility |
| ISR | 2.2.0 | Default backend |
| Real-ESRGAN | 0.3.0 | Optional backend |

## Troubleshooting

### Issue: CUDA not detected

**Solution:**
1. Verify CUDA installation: `nvidia-smi`
2. Check CUDA version: `nvcc --version`
3. Reinstall PyTorch with correct CUDA version

### Issue: PyMeshLab installation fails

**Solution:**
```bash
# Install system dependencies (Linux)
sudo apt-get install libgl1-mesa-glx libglib2.0-0

# Retry installation
pip install pymeshlab==2022.2.post4
```

### Issue: ISR installation fails

**Solution:**
```bash
# Install TensorFlow (ISR dependency)
pip install tensorflow>=2.10.0

# Retry ISR
pip install ISR==2.2.0
```

### Issue: Out of memory errors

**Solutions:**
1. Reduce `tile_size` in config.yaml (e.g., from 1024 to 512)
2. Use 2x upscaling instead of 4x
3. Process smaller models
4. Close other GPU applications

### Issue: basicsr installation fails

**Solution:**
```bash
# Use ISR instead (already in requirements.txt)
pip install ISR==2.2.0

# The tool will automatically use ISR if Real-ESRGAN is unavailable
```

## Platform-Specific Notes

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10+
brew install python@3.10

# Note: CUDA not available on macOS, tool will use CPU mode
```

### Windows (WSL2)

```bash
# Use Windows Subsystem for Linux 2
# Follow Linux installation steps above

# Ensure CUDA is available in WSL2
nvidia-smi  # Should work in WSL2 with NVIDIA drivers
```

## Upgrading

To upgrade to the latest version:

```bash
cd trellis-3d-enhance
git pull origin main

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove the entire directory
cd ..
rm -rf trellis-3d-enhance
```

## Getting Help

- **Documentation**: See [README.md](README.md)
- **Examples**: See [examples/](examples/)
- **Issues**: https://github.com/iCLEARLOVE/trellis-3d-enhance/issues
