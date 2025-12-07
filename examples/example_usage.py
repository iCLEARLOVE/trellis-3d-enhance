"""
Example usage of Trellis 3D Enhancement Tool

This file demonstrates various ways to use the enhancement tool,
both via the command-line interface and programmatically via the Python API.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.texture_enhancer import TextureEnhancer
from src.geometry_optimizer import GeometryOptimizer
from src.sd_enhancer import SDEnhancer
import yaml


def example_1_simple_enhancement():
    """
    Example 1: Simple texture enhancement
    
    Enhance a 3D model with default settings (4x upscaling)
    """
    print("=" * 60)
    print("Example 1: Simple Texture Enhancement")
    print("=" * 60)
    
    enhancer = TextureEnhancer()
    
    # Enhance model
    output_path = enhancer.enhance_model(
        input_path="path/to/trellis_output.glb",
        output_dir="output/example1/",
        upscale_factor=4
    )
    
    print(f"Enhanced model saved to: {output_path}")


def example_2_custom_config():
    """
    Example 2: Enhancement with custom configuration
    
    Load settings from config file and apply custom parameters
    """
    print("=" * 60)
    print("Example 2: Custom Configuration")
    print("=" * 60)
    
    # Load config
    with open('../config/config.yaml') as f:
        config = yaml.safe_load(f)
    
    # Initialize enhancers with config
    texture_enhancer = TextureEnhancer(
        scale=config['texture']['upscale_factor'],
        tile_size=config['texture']['tile_size'],
        use_fp16=config['texture']['use_fp16']
    )
    
    geometry_optimizer = GeometryOptimizer(
        enable_subdivision=config['geometry']['enable_subdivision'],
        subdivision_iterations=config['geometry']['subdivision_iterations'],
        enable_smoothing=config['geometry']['enable_smoothing'],
        smoothing_steps=config['geometry']['smoothing_steps']
    )
    
    # Enhance texture
    texture_output = texture_enhancer.enhance_model(
        "path/to/model.glb",
        "output/example2/texture/"
    )
    
    # Optimize geometry
    final_output = geometry_optimizer.optimize_mesh(
        texture_output,
        "output/example2/final/model_enhanced.glb"
    )
    
    print(f"Final enhanced model: {final_output}")


def example_3_sd_enhancement():
    """
    Example 3: Stable Diffusion texture enhancement
    
    Use Stable Diffusion ControlNet for more detailed texture enhancement
    """
    print("=" * 60)
    print("Example 3: Stable Diffusion Enhancement")
    print("=" * 60)
    
    # Initialize SD enhancer
    sd_enhancer = SDEnhancer(
        model_id="lllyasviel/control_v11f1e_sd15_tile",
        use_fp16=True
    )
    
    if not sd_enhancer.is_available():
        print("⚠ SD enhancer not available, skipping example")
        print("  Install with: pip install diffusers transformers accelerate")
        return
    
    # Extract texture from model
    from src.utils import extract_texture_from_mesh, apply_texture_to_mesh
    from PIL import Image
    
    input_path = "path/to/model.glb"
    
    # Extract texture
    texture_path = extract_texture_from_mesh(
        input_path,
        output_dir="output/example3/temp/"
    )
    
    if texture_path:
        # Load texture
        texture_img = Image.open(texture_path)
        
        # Enhance with SD
        enhanced_texture = sd_enhancer.enhance_texture(
            texture_img,
            prompt="highly detailed 3D model texture, sharp, 8k quality",
            negative_prompt="blurry, smooth, low quality, artifacts, distorted",
            steps=20,
            conditioning_scale=0.7
        )
        
        # Save enhanced texture
        enhanced_texture_path = "output/example3/texture_sd_enhanced.png"
        enhanced_texture.save(enhanced_texture_path)
        
        # Apply back to model
        output_path = apply_texture_to_mesh(
            input_path,
            enhanced_texture_path,
            "output/example3/model_sd_enhanced.glb"
        )
        
        print(f"SD-enhanced model saved to: {output_path}")


def example_4_batch_processing():
    """
    Example 4: Batch processing multiple models
    
    Enhance multiple models in a directory
    """
    print("=" * 60)
    print("Example 4: Batch Processing")
    print("=" * 60)
    
    from pathlib import Path
    
    # Get all GLB files in input directory
    input_dir = Path("path/to/input_models/")
    model_files = list(input_dir.glob("*.glb"))
    
    print(f"Found {len(model_files)} models to process")
    
    # Initialize enhancer
    enhancer = TextureEnhancer(scale=4)
    
    # Process each model
    for i, model_file in enumerate(model_files, 1):
        print(f"\nProcessing {i}/{len(model_files)}: {model_file.name}")
        
        try:
            output_path = enhancer.enhance_model(
                str(model_file),
                f"output/example4/{model_file.stem}/",
                upscale_factor=4
            )
            print(f"✓ Saved to: {output_path}")
        
        except Exception as e:
            print(f"✗ Failed: {e}")
            continue


def example_5_texture_only():
    """
    Example 5: Texture enhancement only (no geometry)
    
    Enhance only the texture without geometry optimization
    """
    print("=" * 60)
    print("Example 5: Texture Only Enhancement")
    print("=" * 60)
    
    from PIL import Image
    
    # Initialize enhancer
    enhancer = TextureEnhancer(
        scale=4,
        tile_size=1024,
        use_fp16=True
    )
    
    # Load texture image directly
    texture_path = "path/to/texture.png"
    texture_img = Image.open(texture_path)
    
    # Enhance texture
    enhanced_texture = enhancer.enhance_texture(
        texture_img,
        outscale=4
    )
    
    # Save enhanced texture
    output_path = "output/example5/texture_enhanced.png"
    enhanced_texture.save(output_path)
    
    print(f"Enhanced texture saved to: {output_path}")


def example_6_geometry_only():
    """
    Example 6: Geometry optimization only (no texture enhancement)
    
    Optimize mesh geometry without texture changes
    """
    print("=" * 60)
    print("Example 6: Geometry Only Optimization")
    print("=" * 60)
    
    # Initialize optimizer with custom settings
    optimizer = GeometryOptimizer(
        enable_subdivision=True,
        subdivision_iterations=1,
        enable_smoothing=True,
        smoothing_steps=2
    )
    
    # Optimize mesh
    output_path = optimizer.optimize_mesh(
        "path/to/model.glb",
        "output/example6/model_optimized.glb",
        create_backup=True
    )
    
    # Get mesh statistics
    stats = optimizer.get_mesh_stats(output_path)
    print(f"Optimized mesh stats: {stats}")


def example_7_cli_usage():
    """
    Example 7: Command-line interface usage
    
    Examples of how to use the CLI tool
    """
    print("=" * 60)
    print("Example 7: CLI Usage Examples")
    print("=" * 60)
    
    examples = [
        "# Basic enhancement",
        "python enhance.py --input model.glb --output enhanced/",
        "",
        "# 2x texture upscaling",
        "python enhance.py --input model.glb --output enhanced/ --texture-scale 2",
        "",
        "# Texture only (no geometry optimization)",
        "python enhance.py --input model.glb --output enhanced/ --no-geometry",
        "",
        "# Use Stable Diffusion enhancement",
        "python enhance.py --input model.glb --output enhanced/ --use-sd",
        "",
        "# Custom config file",
        "python enhance.py --input model.glb --output enhanced/ --config my_config.yaml",
        "",
        "# Debug mode with verbose logging",
        "python enhance.py --input model.glb --output enhanced/ --log-level DEBUG",
    ]
    
    print("\n".join(examples))


def main():
    """Run all examples (with placeholders for file paths)"""
    print("\n" + "=" * 60)
    print("Trellis 3D Enhancement Tool - Usage Examples")
    print("=" * 60 + "\n")
    
    print("NOTE: These examples use placeholder paths.")
    print("Replace 'path/to/...' with actual file paths to run.\n")
    
    # Display CLI usage examples (no file I/O required)
    example_7_cli_usage()
    
    print("\n" + "=" * 60)
    print("For working examples with actual files:")
    print("1. Place a .glb or .obj file in the examples directory")
    print("2. Update the paths in this file")
    print("3. Run: python examples/example_usage.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
