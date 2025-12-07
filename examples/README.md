# Trellis 3D Enhancement - Examples

This directory contains example code demonstrating how to use the Trellis 3D Enhancement Tool.

## Files

- `example_usage.py` - Comprehensive examples showing different usage patterns

## Examples Included

### 1. Simple Enhancement
Basic texture enhancement with default settings (4x upscaling).

### 2. Custom Configuration
Load and use custom configuration from YAML file.

### 3. Stable Diffusion Enhancement
Use Stable Diffusion ControlNet for advanced texture enhancement.

### 4. Batch Processing
Process multiple 3D models in a directory.

### 5. Texture Only Enhancement
Enhance textures without geometry optimization.

### 6. Geometry Only Optimization
Optimize mesh geometry without texture changes.

### 7. CLI Usage
Command-line interface examples.

## Running Examples

### View CLI Examples
```bash
python examples/example_usage.py
```

This will display all CLI usage examples without requiring any input files.

### Run with Actual Files

1. Update the placeholder paths in `example_usage.py`:
   ```python
   # Change this:
   input_path="path/to/trellis_output.glb"
   
   # To actual path:
   input_path="examples/my_model.glb"
   ```

2. Run specific example functions:
   ```python
   from examples.example_usage import example_1_simple_enhancement
   example_1_simple_enhancement()
   ```

## Quick Start Examples

### Using Python API

```python
from src.texture_enhancer import TextureEnhancer

# Initialize enhancer
enhancer = TextureEnhancer(scale=4)

# Enhance a model
output_path = enhancer.enhance_model(
    input_path="model.glb",
    output_dir="enhanced/",
    upscale_factor=4
)
```

### Using CLI

```bash
# Basic enhancement
python enhance.py --input model.glb --output enhanced/

# With custom settings
python enhance.py --input model.glb --output enhanced/ --texture-scale 2

# Texture only
python enhance.py --input model.glb --output enhanced/ --no-geometry

# With Stable Diffusion
python enhance.py --input model.glb --output enhanced/ --use-sd
```

## Configuration

All examples can be customized using the `config/config.yaml` file. See the main README.md for configuration options.

## Requirements

The examples require the same dependencies as the main tool. Run the setup script first:

```bash
bash setup.sh
```

## Tips

- Start with Example 7 (CLI usage) - no files required
- Use Example 1 for basic API usage
- Use Example 4 for batch processing multiple models
- Use Example 3 if you want maximum quality (requires SD dependencies)

## Getting Help

For more information, see the main [README.md](../README.md) or run:

```bash
python enhance.py --help
```
