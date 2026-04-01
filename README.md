# Trellis 3D Model Enhancer 🎨

> Enhance Trellis-generated 3D models with AI-powered texture upscaling and geometry optimization.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CUDA](https://img.shields.io/badge/CUDA-11.8-green.svg)](https://developer.nvidia.com/cuda-toolkit)

## ✨ Features

- 🚀 **Texture Super-Resolution** - 2x/4x upscaling with Real-ESRGAN
- 🎯 **Geometry Optimization** - Mesh refinement with PyMeshLab
- 🎨 **Optional SD Enhancement** - Stable Diffusion ControlNet support
- ⚡ **GPU Optimized** - FP16 precision for NVIDIA GPUs
- 📦 **Plug-and-Play** - Pretrained models auto-download

## 🎬 Quick Start

```bash
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance
bash setup.sh
python enhance.py --input your_model.glb --output enhanced/
```

## 📋 Requirements

- **GPU**: NVIDIA GPU with 8GB+ VRAM (CPU-only mode available but significantly slower)
- **RAM**: 16GB+ recommended
- **Python**: 3.8+, **CUDA**: 11.8+
- **OS**: Linux, macOS, or Windows with WSL

## 🚀 Installation

### Automatic Setup (Recommended)

```bash
git clone https://github.com/iCLEARLOVE/trellis-3d-enhance.git
cd trellis-3d-enhance
bash setup.sh
```

### Manual Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
mkdir -p weights output logs
```

### Optional: Stable Diffusion Support

```bash
pip install diffusers>=0.21.0 transformers>=4.30.0 accelerate>=0.20.0
```

## 📖 Usage

### CLI

```bash
# Basic
python enhance.py --input model.glb --output enhanced/

# 2x upscaling (faster)
python enhance.py --input model.glb --output enhanced/ --texture-scale 2

# Texture only
python enhance.py --input model.glb --output enhanced/ --no-geometry

# SD enhancement
python enhance.py --input model.glb --output enhanced/ --use-sd

# Custom config / debug
python enhance.py --input model.glb --output enhanced/ --config my_config.yaml
python enhance.py --input model.glb --output enhanced/ --log-level DEBUG
```

### Python API

```python
from src.texture_enhancer import TextureEnhancer
from src.geometry_optimizer import GeometryOptimizer

enhancer = TextureEnhancer(scale=4)
output_path = enhancer.enhance_model("model.glb", "enhanced/", upscale_factor=4)

optimizer = GeometryOptimizer()
optimizer.optimize_mesh(output_path, "output/final/model_enhanced.glb")
```

## ⚙️ Configuration

Edit `config/config.yaml`:

```yaml
texture:
  upscale_factor: 4      # 2 or 4
  use_fp16: true
  tile_size: 1024
  output_format: "png"

geometry:
  enable_subdivision: false
  enable_smoothing: false

sd_enhancement:
  enable: false
  steps: 20
  conditioning_scale: 0.7
  prompt: "highly detailed texture, sharp details, 8k quality"

output:
  create_backup: true
  compression: true
```

## 🎯 Supported Formats

- **Input/Output**: `.glb`, `.obj`, `.ply`
- **Textures**: `.png`, `.jpg`

## 📊 Performance Benchmarks (NVIDIA A6000, 48GB VRAM)

| Operation | Time | VRAM |
|-----------|------|------|
| Texture 2K→8K (4x) | ~8s | ~6GB |
| Texture 1K→4K (4x) | ~3s | ~4GB |
| Geometry Optimization | ~2s | ~1GB |
| Full Enhancement | ~30-60s | ~8GB |
| SD Enhancement | ~45s | ~12GB |

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| No GPU / CUDA not detected | `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118` |
| `basicsr` / Real-ESRGAN fails | `pip install ISR` (auto-fallback) or `pip install realesrgan basicsr` |
| Out of memory | Reduce `tile_size` to 512, use 2x upscaling |
| Failed to load mesh | Verify file format; re-export from Trellis |
| Weights not found | Download [RealESRGAN_x4plus.pth](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth) to `weights/` |
| SD not available | `pip install diffusers transformers accelerate` |

Debug logs: `python enhance.py --input model.glb --output enhanced/ --log-level DEBUG`

## 🏗️ Project Structure

```
trellis-3d-enhance/
├── enhance.py               # Main CLI
├── requirements.txt
├── setup.sh
├── src/
│   ├── texture_enhancer.py  # Real-ESRGAN upscaling
│   ├── geometry_optimizer.py
│   ├── sd_enhancer.py
│   └── utils.py
├── config/config.yaml
└── examples/
```

## 🤝 Contributing

Open an issue first to discuss changes. PRs welcome for bug fixes, features, and docs.

## 📚 API Reference

| Class | Key Methods |
|-------|-------------|
| `TextureEnhancer(scale, tile_size, use_fp16)` | `enhance_texture(img)`, `enhance_model(path, out_dir)` |
| `GeometryOptimizer(enable_subdivision)` | `optimize_mesh(path, out)`, `get_mesh_stats(path)` |
| `SDEnhancer(model_id)` | `enhance_texture(img, prompt, steps)`, `is_available()` |

## 🙏 Credits

[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) · [PyMeshLab](https://github.com/cnr-isti-vclab/PyMeshLab) · [Stable Diffusion](https://github.com/CompVis/stable-diffusion) · [ControlNet](https://github.com/lllyasviel/ControlNet) · [Trellis](https://github.com/microsoft/TRELLIS)

## 📄 License

[MIT License](https://opensource.org/licenses/MIT) © 2024 Trellis 3D Enhancement Tool

---

**Built with ❤️ for the 3D and AI community** · [Issues](https://github.com/iCLEARLOVE/trellis-3d-enhance/issues) · [Discussions](https://github.com/iCLEARLOVE/trellis-3d-enhance/discussions)
