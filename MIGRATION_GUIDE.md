# Migration Guide: Python 3.10+ and CUDA 12.x Support

## What Changed?

This project has been updated to better support modern Python versions (3.10+) and CUDA versions (12.x, including CUDA 12.8) for compatibility with newer GPUs like the A6000 PRO.

### Key Changes

1. **Default Texture Enhancement Backend Changed**
   - **Old**: ISR (Image Super-Resolution) was the default
   - **New**: Real-ESRGAN is now the default
   - **Reason**: ISR requires TensorFlow 2.0.0, which is incompatible with Python 3.10+

2. **Requirements Updated**
   - Added Real-ESRGAN and dependencies (realesrgan, basicsr, facexlib, gfpgan) as default
   - Moved ISR to optional/legacy status for Python 3.7-3.9 users only
   - Clarified CUDA 12.x (including 12.8) support in PyTorch installation instructions

3. **Documentation Updated**
   - README.md now recommends Real-ESRGAN for Python 3.10+
   - INSTALL.md includes troubleshooting for ISR/TensorFlow issues
   - setup.sh prompts for ISR only as a legacy option

## Why This Change?

### The Problem

When using Python 3.10 or higher, installing the old requirements.txt would fail with:

```
ERROR: Could not find a version that satisfies the requirement tensorflow==2.0.0 (from isr)
ERROR: No matching distribution found for tensorflow==2.0.0
```

This is because:
- ISR requires TensorFlow 2.0.0
- TensorFlow 2.0.0 is only available for Python 3.7-3.9
- Modern Python (3.10+) only has TensorFlow 2.8.0+
- CUDA 12.x is not supported by TensorFlow 2.0.0

### The Solution

Real-ESRGAN is a better choice for modern environments because:
- ✅ Works with PyTorch (better CUDA 12.x support)
- ✅ Compatible with Python 3.10, 3.11, 3.12
- ✅ Works with CUDA 12.x (including 12.8)
- ✅ Better quality results
- ✅ Optimized for modern GPUs like A6000 PRO

## Migration Instructions

### For New Installations (Python 3.10+)

Simply follow the normal installation steps:

```bash
# Clone repository
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance

# Run setup (will install Real-ESRGAN by default)
bash setup.sh

# Or manual installation:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### For Existing Users

#### If You Were Using ISR (Python 3.10+)

You need to switch to Real-ESRGAN:

```bash
# Uninstall ISR and TensorFlow
pip uninstall ISR tensorflow tensorflow-gpu -y

# Install Real-ESRGAN
pip install realesrgan==0.3.0 basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8

# No code changes needed - the tool will automatically use Real-ESRGAN
```

#### If You Want to Keep Using ISR (Python 3.7-3.9 only)

If you're using Python 3.7-3.9 and want to keep ISR:

```bash
# Make sure you have Python 3.7-3.9
python --version

# Install ISR instead of Real-ESRGAN
pip install ISR==2.2.0

# Comment out Real-ESRGAN in requirements.txt
# Uncomment ISR line in requirements.txt
```

**Warning**: ISR is not compatible with:
- Python 3.10 or higher
- CUDA 12.x
- Modern GPUs with latest drivers

## Environment Compatibility

### Recommended Setup (Modern)

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.10, 3.11, 3.12 | Recommended for best compatibility |
| CUDA | 12.1, 12.4, 12.8 | Full support |
| GPU | A6000, RTX 3090, RTX 4090 | Modern NVIDIA GPUs |
| Backend | Real-ESRGAN | Default and recommended |

### Legacy Setup (Not Recommended)

| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.7, 3.8, 3.9 | Limited support |
| CUDA | 10.x, 11.x | Older versions |
| GPU | GTX 1080, RTX 2080 | Older NVIDIA GPUs |
| Backend | ISR | Legacy option only |

## What Stays the Same?

Good news! The following remain unchanged:

1. **API Compatibility**: All Python APIs work exactly the same
2. **CLI Commands**: All command-line options are identical
3. **Configuration**: config.yaml format is unchanged
4. **Model Quality**: Real-ESRGAN provides equal or better quality
5. **Automatic Fallback**: Code still supports ISR as fallback if available

### Example Usage (Unchanged)

```bash
# All these commands work exactly the same
python enhance.py --input model.glb --output enhanced/
python enhance.py --input model.glb --output enhanced/ --texture-scale 2
python enhance.py --input model.glb --output enhanced/ --no-geometry
```

```python
# Python API also unchanged
from src.texture_enhancer import TextureEnhancer

enhancer = TextureEnhancer(scale=4)
output = enhancer.enhance_model("model.glb", "enhanced/")
```

## Troubleshooting

### "basicsr installation failed"

If Real-ESRGAN installation fails, you may need build tools:

**Linux/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev
pip install realesrgan==0.3.0 basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8
```

**macOS:**
```bash
xcode-select --install
pip install realesrgan==0.3.0 basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8
```

### "CUDA not found" with PyTorch

Make sure you install PyTorch with CUDA support:

```bash
# For CUDA 12.x (including 12.8)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Still Having Issues?

1. Check your Python version: `python --version`
2. Check your CUDA version: `nvidia-smi`
3. See [INSTALL.md](INSTALL.md) for detailed troubleshooting
4. Open an issue on GitHub with error details

## FAQ

### Q: Will my existing enhanced models still work?

**A:** Yes! The output format hasn't changed. All previously enhanced models remain compatible.

### Q: Is Real-ESRGAN slower than ISR?

**A:** No, Real-ESRGAN is actually faster on modern GPUs with CUDA 12.x because PyTorch has better optimization than TensorFlow 2.0.

### Q: Can I use both backends?

**A:** Yes, the tool will automatically detect and use whichever backend is available. Real-ESRGAN takes priority if both are installed.

### Q: What about CPU-only systems?

**A:** Real-ESRGAN works on CPU too (though slower). ISR also works on CPU if you have Python 3.7-3.9.

### Q: Do I need to re-enhance my models?

**A:** No, but you may want to. Real-ESRGAN often produces better quality than ISR.

## Summary

**Bottom line**: If you have Python 3.10+ and CUDA 12.x (like on A6000 PRO), use Real-ESRGAN (now the default). Everything else works the same!

For questions or issues, please see:
- [README.md](README.md) - Main documentation
- [INSTALL.md](INSTALL.md) - Installation guide
- [GitHub Issues](https://github.com/iCLEARLOVE/trellis-3d-enhance/issues) - Report problems
