# Trellis 3D Model Enhancer 🎨

> Enhance your Trellis-generated 3D models with AI-powered texture upscaling and geometry optimization.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CUDA](https://img.shields.io/badge/CUDA-11.8-green.svg)](https://developer.nvidia.com/cuda-toolkit)

Transform your Trellis 3D models into high-quality assets with AI-powered enhancement. This tool provides plug-and-play texture upscaling using Real-ESRGAN and intelligent geometry optimization using PyMeshLab—no training required.

## ✨ Features

- 🚀 **Texture Super-Resolution** - 2x/4x upscaling with Real-ESRGAN
- 🎯 **Geometry Optimization** - Smart mesh refinement with PyMeshLab
- 🎨 **Optional SD Enhancement** - Advanced detail enhancement with Stable Diffusion ControlNet
- ⚡ **GPU Optimized** - FP16 precision optimized for NVIDIA A6000
- 🔧 **Easy to Use** - Simple CLI and Python API
- 📦 **Plug-and-Play** - No training required, pretrained models auto-download
- 🛠️ **Conservative Enhancement** - Preserves Trellis model quality
- 📊 **Progress Tracking** - Real-time progress bars and logging

## 🎬 Quick Start

Get up and running in 3 simple steps:

```bash
# 1. Clone and setup
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance
bash setup.sh

# 2. Enhance your model
python enhance.py --input your_model.glb --output enhanced/

# 3. Done! Check the enhanced/ folder
```

## 📋 Requirements

### Hardware
- **GPU**: NVIDIA GPU with 8GB+ VRAM (A6000 recommended)
  - CPU-only mode available but significantly slower
- **RAM**: 16GB+ recommended
- **Storage**: 5GB for dependencies and model weights

### Software
- **Python**: 3.8 or higher
- **CUDA**: 11.8 or higher (for GPU acceleration)
- **OS**: Linux, macOS, or Windows with WSL

## 🚀 Installation

### Option 1: Automatic Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance

# Run setup script (handles everything)
bash setup.sh
```

The setup script will:
- ✅ Check Python version
- ✅ Create virtual environment (optional)
- ✅ Install PyTorch with CUDA support
- ✅ Install all dependencies
- ✅ Download pretrained weights
- ✅ Set up project directories

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p weights output logs

# Download weights (automatic on first run)
python enhance.py --help
```

### Optional: Stable Diffusion Support

For advanced texture enhancement with Stable Diffusion:

```bash
pip install diffusers>=0.21.0 transformers>=4.30.0 accelerate>=0.20.0
```

## 📖 Usage

### Command-Line Interface

#### Basic Enhancement
```bash
python enhance.py --input model.glb --output enhanced/
```

#### Custom Texture Scale
```bash
# 2x upscaling (faster)
python enhance.py --input model.glb --output enhanced/ --texture-scale 2

# 4x upscaling (default, higher quality)
python enhance.py --input model.glb --output enhanced/ --texture-scale 4
```

#### Texture Only (Skip Geometry Optimization)
```bash
python enhance.py --input model.glb --output enhanced/ --no-geometry
```

#### Stable Diffusion Enhancement
```bash
# Use SD for maximum quality (slower)
python enhance.py --input model.glb --output enhanced/ --use-sd
```

#### Custom Configuration
```bash
python enhance.py --input model.glb --output enhanced/ --config my_config.yaml
```

#### Debug Mode
```bash
python enhance.py --input model.glb --output enhanced/ --log-level DEBUG
```

### Python API

#### Simple Enhancement
```python
from src.texture_enhancer import TextureEnhancer

# Initialize enhancer
enhancer = TextureEnhancer(scale=4)

# Enhance model
output_path = enhancer.enhance_model(
    input_path="model.glb",
    output_dir="enhanced/",
    upscale_factor=4
)

print(f"Enhanced model saved to: {output_path}")
```

#### Full Pipeline with Configuration
```python
import yaml
from src.texture_enhancer import TextureEnhancer
from src.geometry_optimizer import GeometryOptimizer

# Load configuration
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Enhance texture
texture_enhancer = TextureEnhancer(
    scale=config['texture']['upscale_factor'],
    tile_size=config['texture']['tile_size']
)
texture_output = texture_enhancer.enhance_model("model.glb", "output/texture/")

# Optimize geometry
geometry_optimizer = GeometryOptimizer(
    enable_subdivision=config['geometry']['enable_subdivision']
)
final_output = geometry_optimizer.optimize_mesh(
    texture_output,
    "output/final/model_enhanced.glb"
)
```

#### Stable Diffusion Enhancement
```python
from src.sd_enhancer import SDEnhancer
from PIL import Image

# Initialize SD enhancer
sd_enhancer = SDEnhancer()

if sd_enhancer.is_available():
    # Load texture
    texture = Image.open("texture.png")
    
    # Enhance with SD
    enhanced = sd_enhancer.enhance_texture(
        texture,
        prompt="highly detailed texture, 8k quality",
        steps=20,
        conditioning_scale=0.7
    )
    
    enhanced.save("texture_enhanced.png")
```

See [examples/](examples/) directory for more usage examples.

## ⚙️ Configuration

Configuration is managed through `config/config.yaml`. Here's what you can customize:

### Texture Enhancement
```yaml
texture:
  upscale_factor: 4      # 2 or 4
  use_fp16: true         # FP16 for faster processing
  tile_size: 1024        # Tile size (1024 for A6000)
  output_format: "png"   # png or jpg
```

### Geometry Optimization
```yaml
geometry:
  enable_subdivision: false    # Conservative by default
  subdivision_iterations: 1    # Subdivision iterations
  enable_smoothing: false      # Light smoothing
  smoothing_steps: 1          # Smoothing steps
```

### Stable Diffusion
```yaml
sd_enhancement:
  enable: false                # Disabled by default
  model: "lllyasviel/control_v11f1e_sd15_tile"
  steps: 20                    # Diffusion steps
  conditioning_scale: 0.7      # ControlNet strength
  prompt: "highly detailed texture, sharp details, 8k quality"
  negative_prompt: "blurry, smooth, low quality, artifacts"
```

### Output Settings
```yaml
output:
  create_backup: true          # Backup original file
  save_intermediate: false     # Save intermediate results
  compression: true            # Compress output
```

See [config/config.yaml](config/config.yaml) for full configuration options.

## 🎯 Supported Formats

- **Input**: `.glb`, `.obj`, `.ply`
- **Output**: `.glb`, `.obj`, `.ply` (same as input)
- **Textures**: `.png`, `.jpg`

## 📊 Performance

Benchmarks on NVIDIA A6000 (48GB VRAM):

| Operation | Input | Output | Time | VRAM |
|-----------|-------|--------|------|------|
| Texture 2K→8K (4x) | 2048×2048 | 8192×8192 | ~8s | ~6GB |
| Texture 1K→4K (4x) | 1024×1024 | 4096×4096 | ~3s | ~4GB |
| Geometry Optimization | 50K faces | 50K faces | ~2s | ~1GB |
| Full Enhancement | - | - | ~30-60s | ~8GB |
| SD Enhancement (optional) | 2048×2048 | 2048×2048 | ~45s | ~12GB |

**Tips for Best Performance:**
- Use FP16 precision (enabled by default on CUDA)
- Set `tile_size=1024` for A6000 (default)
- Use `--no-geometry` if you only need texture enhancement
- For large batches, process in parallel using multiple GPUs

## 🔧 Troubleshooting

### Common Issues

#### "No GPU available, using CPU"
- **Cause**: CUDA not detected or PyTorch not installed with CUDA support
- **Solution**: 
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

#### "Out of memory" error
- **Cause**: VRAM exceeded
- **Solutions**:
  - Reduce `tile_size` in config (e.g., 512 instead of 1024)
  - Use 2x upscaling instead of 4x
  - Process smaller textures
  - Enable CPU offloading (automatic for SD)

#### "Failed to load mesh"
- **Cause**: Corrupted or unsupported file format
- **Solution**: 
  - Verify file is valid `.glb` or `.obj`
  - Try opening in Blender or other 3D software
  - Re-export from Trellis

#### "Weights not found"
- **Cause**: Download failed or blocked
- **Solution**:
  - Check internet connection
  - Manually download from: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
  - Place in `weights/` directory

#### "SD enhancement not available"
- **Cause**: Diffusers not installed
- **Solution**:
  ```bash
  pip install diffusers transformers accelerate
  ```

### Debug Mode

Enable debug logging for detailed error information:

```bash
python enhance.py --input model.glb --output enhanced/ --log-level DEBUG
```

Check the log file: `enhancement.log`

### Getting Help

- Check [examples/](examples/) for usage patterns
- Review [config/config.yaml](config/config.yaml) for all options
- Open an issue on GitHub with:
  - Error message
  - Input file format and size
  - GPU model and VRAM
  - Log file contents

## 🏗️ Project Structure

```
trellis-3d-enhance/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
├── enhance.py               # Main CLI tool
├── src/
│   ├── __init__.py
│   ├── texture_enhancer.py  # Real-ESRGAN texture upscaling
│   ├── geometry_optimizer.py # PyMeshLab mesh optimization
│   ├── sd_enhancer.py       # Stable Diffusion enhancement
│   └── utils.py             # Helper functions
├── config/
│   └── config.yaml          # Configuration file
├── weights/                 # Pretrained models (auto-download)
│   └── .gitkeep
└── examples/
    ├── example_usage.py     # Usage examples
    └── README.md
```

## 🤝 Contributing

Contributions are welcome! Here are some ways you can contribute:

- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests

Please open an issue first to discuss major changes.

## 📚 API Documentation

### TextureEnhancer

```python
class TextureEnhancer:
    """Enhance textures using Real-ESRGAN"""
    
    def __init__(self, scale=4, tile_size=1024, use_fp16=True):
        """Initialize enhancer"""
        
    def enhance_texture(self, texture_image, outscale=4):
        """Enhance a single texture image"""
        
    def enhance_model(self, input_path, output_dir, upscale_factor=4):
        """Enhance textures in a 3D model"""
```

### GeometryOptimizer

```python
class GeometryOptimizer:
    """Optimize mesh geometry using PyMeshLab"""
    
    def __init__(self, enable_subdivision=False, subdivision_iterations=1):
        """Initialize optimizer"""
        
    def optimize_mesh(self, mesh_path, output_path):
        """Optimize a 3D mesh file"""
        
    def get_mesh_stats(self, mesh_path):
        """Get mesh statistics"""
```

### SDEnhancer

```python
class SDEnhancer:
    """Enhance textures using Stable Diffusion"""
    
    def __init__(self, model_id="lllyasviel/control_v11f1e_sd15_tile"):
        """Initialize SD enhancer"""
        
    def enhance_texture(self, texture_image, prompt, steps=20):
        """Enhance texture with SD ControlNet"""
        
    def is_available(self):
        """Check if SD is available"""
```

See source code for detailed API documentation.

## 🙏 Credits

This tool builds upon excellent open-source projects:

- **[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)** - Texture super-resolution
- **[PyMeshLab](https://github.com/cnr-isti-vclab/PyMeshLab)** - Mesh processing
- **[Stable Diffusion](https://github.com/CompVis/stable-diffusion)** - Optional texture enhancement
- **[ControlNet](https://github.com/lllyasviel/ControlNet)** - Structure-preserving enhancement
- **[Trellis](https://github.com/microsoft/TRELLIS)** - 3D model generation

Special thanks to the creators and maintainers of these projects!

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 Trellis 3D Enhancement Tool

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🌟 Star History

If you find this tool useful, please consider giving it a star ⭐!

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/iCLEARLOVE/trellis-3d-enhance/issues)
- **Discussions**: [GitHub Discussions](https://github.com/iCLEARLOVE/trellis-3d-enhance/discussions)

---

**Built with ❤️ for the 3D and AI community**

Enhance your 3D models today! 🎨✨
