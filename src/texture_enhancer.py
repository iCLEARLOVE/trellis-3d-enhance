"""
Texture enhancement module using Real-ESRGAN.

This module provides texture upscaling capabilities using the Real-ESRGAN model,
optimized for NVIDIA A6000 GPU with FP16 and tiling support.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from PIL import Image
import torch
from tqdm import tqdm

from .utils import download_file, extract_texture_from_mesh, apply_texture_to_mesh, get_device

logger = logging.getLogger(__name__)


class TextureEnhancer:
    """
    Enhance 3D model textures using Real-ESRGAN.
    
    This class provides methods to upscale textures from 3D models using
    the Real-ESRGAN super-resolution model. It's optimized for A6000 GPUs
    with FP16 precision and tiling for large textures.
    
    Attributes:
        scale: Upscaling factor (2 or 4)
        tile_size: Size of tiles for processing large images
        use_fp16: Whether to use FP16 precision for faster processing
        device: Device to use for inference ('cuda', 'mps', or 'cpu')
        model: The Real-ESRGAN model instance
    """
    
    def __init__(
        self,
        scale: int = 4,
        tile_size: int = 1024,
        use_fp16: bool = True,
        device: Optional[str] = None,
        weights_url: Optional[str] = None
    ):
        """
        Initialize the TextureEnhancer.
        
        Args:
            scale: Upscaling factor (2 or 4, default: 4)
            tile_size: Tile size for processing (default: 1024 for A6000)
            use_fp16: Use FP16 precision for faster processing (default: True)
            device: Device to use ('cuda', 'mps', 'cpu', or None for auto-detect)
            weights_url: URL to download weights from (if None, uses default)
        """
        self.scale = scale
        self.tile_size = tile_size
        self.use_fp16 = use_fp16
        self.device = device if device else get_device()
        self.model = None
        self.weights_dir = Path("weights")
        self.weights_dir.mkdir(exist_ok=True)
        self.weights_url = weights_url or "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
        
        logger.info(
            f"Initializing TextureEnhancer (scale={scale}, "
            f"tile_size={tile_size}, fp16={use_fp16}, device={self.device})"
        )
        
        # Initialize model
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the texture upscaling model (tries Real-ESRGAN first, falls back to ISR)."""
        # Try Real-ESRGAN first (requires basicsr)
        try:
            from realesrgan import RealESRGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            
            logger.info("Loading Real-ESRGAN model...")
            
            # Check if weights exist, download if not
            weights_path = self.weights_dir / "RealESRGAN_x4plus.pth"
            if not weights_path.exists():
                logger.info("Weights not found, downloading...")
                self.download_weights()
            
            # Initialize model architecture
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4
            )
            
            # Initialize upsampler
            self.model = RealESRGANer(
                scale=4,
                model_path=str(weights_path),
                model=model,
                tile=self.tile_size,
                tile_pad=10,
                pre_pad=0,
                half=self.use_fp16 and self.device == 'cuda',
                device=self.device
            )
            
            self.model_type = 'realesrgan'
            logger.info("Real-ESRGAN model loaded successfully")
            return
            
        except ImportError as e:
            logger.warning(
                f"Real-ESRGAN not available: {e}\n"
                "Falling back to ISR (Image Super-Resolution)..."
            )
        
        # Fallback to ISR (doesn't require basicsr)
        try:
            from ISR.models import RDN
            
            logger.info("Loading ISR RDN model...")
            
            # ISR supports 2x and 4x upscaling
            if self.scale == 2:
                self.model = RDN(arch_params={'C': 3, 'D': 10, 'G': 64, 'G0': 64, 'x': 2})
                weights_name = 'rdn-C3-D10-G64-G064-x2_PSNR_epoch086.hdf5'
            else:  # scale == 4
                self.model = RDN(arch_params={'C': 6, 'D': 20, 'G': 64, 'G0': 64, 'x': 4})
                weights_name = 'rdn-C6-D20-G64-G064-x4_PSNR_epoch134.hdf5'
            
            # ISR auto-downloads weights if not present
            weights_path = self.weights_dir / weights_name
            if not weights_path.exists():
                logger.info("Downloading ISR weights (this may take a moment)...")
            
            # ISR models use TensorFlow/Keras, load to appropriate device
            self.model_type = 'isr'
            logger.info(f"ISR RDN {self.scale}x model loaded successfully")
            logger.info("Note: ISR is used as fallback. For best quality, install Real-ESRGAN with: pip install realesrgan basicsr")
            return
            
        except ImportError as e:
            logger.error(
                f"Failed to load texture enhancement model: {e}\n"
                "Install either:\n"
                "  1. Real-ESRGAN: pip install realesrgan basicsr (recommended)\n"
                "  2. ISR: pip install ISR (lightweight alternative)\n"
                "At least one is required for texture enhancement."
            )
            raise RuntimeError("No texture enhancement model available")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def download_weights(self) -> str:
        """
        Download Real-ESRGAN pretrained weights.
        
        Downloads RealESRGAN_x4plus.pth from the configured URL.
        
        Returns:
            Path to the downloaded weights file
        """
        output_path = self.weights_dir / "RealESRGAN_x4plus.pth"
        
        logger.info("Downloading Real-ESRGAN weights...")
        return download_file(self.weights_url, str(output_path), desc="Downloading Real-ESRGAN weights")
    
    def enhance_texture(
        self,
        texture_image: Image.Image,
        outscale: Optional[int] = None
    ) -> Image.Image:
        """
        Enhance a single texture image.
        
        Args:
            texture_image: PIL Image to enhance
            outscale: Output scale factor (if None, uses self.scale)
        
        Returns:
            Enhanced PIL Image
        
        Raises:
            ValueError: If model is not loaded
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call _load_model() first.")
        
        if outscale is None:
            outscale = self.scale
        
        logger.info(f"Enhancing texture with {outscale}x upscaling using {self.model_type}")
        
        # Convert PIL Image to numpy array
        img_array = np.array(texture_image)
        
        # Enhance based on model type
        try:
            if self.model_type == 'realesrgan':
                # Real-ESRGAN processing
                output, _ = self.model.enhance(img_array, outscale=outscale)
                enhanced_image = Image.fromarray(output)
                
            elif self.model_type == 'isr':
                # ISR processing
                # ISR expects RGB image in range [0, 255]
                if img_array.ndim == 2:  # Grayscale
                    img_array = np.stack([img_array] * 3, axis=-1)
                
                # ISR predict method
                output = self.model.predict(img_array)
                
                # Convert to uint8
                output = np.clip(output, 0, 255).astype(np.uint8)
                enhanced_image = Image.fromarray(output)
            
            else:
                raise ValueError(f"Unknown model type: {self.model_type}")
            
            logger.info(
                f"Texture enhanced: {texture_image.size} -> {enhanced_image.size}"
            )
            return enhanced_image
            
        except Exception as e:
            logger.error(f"Enhancement failed: {e}")
            raise
    
    def enhance_model(
        self,
        input_path: str,
        output_dir: str,
        upscale_factor: Optional[int] = None,
        save_texture: bool = True
    ) -> str:
        """
        Enhance textures in a 3D model file.
        
        This method extracts textures from the input model, enhances them
        using Real-ESRGAN, and saves the model with enhanced textures.
        
        Args:
            input_path: Path to input 3D model (.glb, .obj, or .ply)
            output_dir: Directory where enhanced model will be saved
            upscale_factor: Upscaling factor (if None, uses self.scale)
            save_texture: Whether to also save the enhanced texture separately
        
        Returns:
            Path to the enhanced model file
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file format is not supported
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if upscale_factor is None:
            upscale_factor = self.scale
        
        logger.info(f"Enhancing model: {input_path}")
        
        # Validate input file
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        ext = input_path.suffix.lower()
        if ext not in ['.glb', '.obj', '.ply']:
            raise ValueError(f"Unsupported file format: {ext}. Supported formats: .glb, .obj, .ply")
        
        # Extract texture from mesh
        logger.info("Extracting texture from mesh...")
        temp_texture_dir = output_dir / "temp_textures"
        texture_path = extract_texture_from_mesh(
            str(input_path),
            output_dir=str(temp_texture_dir)
        )
        
        if texture_path is None:
            logger.warning("No texture found in model, copying original file")
            output_path = output_dir / f"{input_path.stem}_enhanced{ext}"
            import shutil
            shutil.copy(input_path, output_path)
            return str(output_path)
        
        # Load and enhance texture
        logger.info(f"Loading texture from {texture_path}")
        texture_image = Image.open(texture_path)
        
        with tqdm(total=1, desc="Enhancing texture") as pbar:
            enhanced_texture = self.enhance_texture(texture_image, outscale=upscale_factor)
            pbar.update(1)
        
        # Save enhanced texture
        enhanced_texture_path = output_dir / f"{input_path.stem}_texture_enhanced.png"
        enhanced_texture.save(enhanced_texture_path)
        logger.info(f"Enhanced texture saved to {enhanced_texture_path}")
        
        # Apply enhanced texture back to model
        logger.info("Applying enhanced texture to model...")
        output_path = output_dir / f"{input_path.stem}_enhanced{ext}"
        
        try:
            apply_texture_to_mesh(
                str(input_path),
                str(enhanced_texture_path),
                str(output_path)
            )
        except Exception as e:
            logger.warning(f"Failed to apply texture to mesh: {e}")
            logger.info("Saving enhanced texture only")
            if not save_texture:
                logger.warning("Model enhancement incomplete")
        
        # Clean up temporary texture directory
        if temp_texture_dir.exists():
            import shutil
            shutil.rmtree(temp_texture_dir)
        
        # Optionally remove separate texture file
        if not save_texture and output_path.exists():
            enhanced_texture_path.unlink()
        
        logger.info(f"Model enhancement complete: {output_path}")
        return str(output_path)
