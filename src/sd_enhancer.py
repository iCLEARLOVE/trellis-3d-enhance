"""
Optional Stable Diffusion enhancement module.

This module provides texture enhancement using Stable Diffusion with ControlNet
in Tile mode for detail enhancement while preserving structure.
"""

import logging
from typing import Optional
from PIL import Image
import torch

logger = logging.getLogger(__name__)


class SDEnhancer:
    """
    Enhance textures using Stable Diffusion with ControlNet.
    
    This is an optional enhancement that can add more detail to textures
    using Stable Diffusion's ControlNet in Tile mode. It's slower than
    Real-ESRGAN but can add more creative details.
    
    Attributes:
        model_id: HuggingFace model ID for ControlNet
        device: Device to use for inference
        pipe: Diffusion pipeline instance
    """
    
    def __init__(
        self,
        model_id: str = "lllyasviel/control_v11f1e_sd15_tile",
        device: Optional[str] = None,
        use_fp16: bool = True
    ):
        """
        Initialize the SDEnhancer.
        
        Args:
            model_id: HuggingFace model ID (default: ControlNet Tile v1.1)
            device: Device to use ('cuda', 'mps', 'cpu', or None for auto)
            use_fp16: Use FP16 precision for faster processing
        """
        self.model_id = model_id
        self.use_fp16 = use_fp16
        self.pipe = None
        
        # Import device detection from utils
        from .utils import get_device
        self.device = device if device else get_device()
        
        logger.info(
            f"Initializing SDEnhancer (model={model_id}, "
            f"device={self.device}, fp16={use_fp16})"
        )
        
        # Try to load the model
        try:
            self._load_model()
        except Exception as e:
            logger.warning(
                f"Failed to load Stable Diffusion model: {e}\n"
                "SD enhancement will not be available. "
                "Install with: pip install diffusers transformers accelerate"
            )
    
    def _load_model(self) -> None:
        """Load the Stable Diffusion ControlNet pipeline."""
        try:
            from diffusers import (
                StableDiffusionControlNetPipeline,
                ControlNetModel,
                UniPCMultistepScheduler
            )
            
            logger.info("Loading ControlNet model...")
            
            # Load ControlNet
            controlnet = ControlNetModel.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.use_fp16 and self.device == 'cuda' else torch.float32
            )
            
            # Load Stable Diffusion pipeline with ControlNet
            self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if self.use_fp16 and self.device == 'cuda' else torch.float32,
                safety_checker=None,
            )
            
            # Use efficient scheduler
            self.pipe.scheduler = UniPCMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            # Move to device
            self.pipe = self.pipe.to(self.device)
            
            # Enable memory optimizations
            if self.device == 'cuda':
                try:
                    self.pipe.enable_model_cpu_offload()
                    logger.info("Enabled CPU offload for memory efficiency")
                except Exception as e:
                    logger.warning(f"Could not enable CPU offload: {e}")
                
                try:
                    self.pipe.enable_attention_slicing()
                    logger.info("Enabled attention slicing")
                except Exception as e:
                    logger.warning(f"Could not enable attention slicing: {e}")
            
            logger.info("Stable Diffusion ControlNet pipeline loaded successfully")
            
        except ImportError as e:
            logger.error(
                f"Failed to import diffusers: {e}\n"
                "Install with: pip install diffusers transformers accelerate"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load Stable Diffusion model: {e}")
            raise
    
    def is_available(self) -> bool:
        """
        Check if SD enhancement is available.
        
        Returns:
            True if the pipeline is loaded and ready, False otherwise
        """
        return self.pipe is not None
    
    def enhance_texture(
        self,
        texture_image: Image.Image,
        prompt: str = "highly detailed texture, sharp details, 8k quality",
        negative_prompt: str = "blurry, smooth, low quality, artifacts",
        steps: int = 20,
        conditioning_scale: float = 0.7,
        seed: Optional[int] = None
    ) -> Image.Image:
        """
        Enhance a texture using Stable Diffusion ControlNet.
        
        Args:
            texture_image: PIL Image to enhance
            prompt: Positive prompt for generation
            negative_prompt: Negative prompt to avoid unwanted features
            steps: Number of diffusion steps (default: 20)
            conditioning_scale: ControlNet conditioning scale (default: 0.7)
            seed: Random seed for reproducibility (optional)
        
        Returns:
            Enhanced PIL Image
        
        Raises:
            RuntimeError: If model is not available
        """
        if not self.is_available():
            raise RuntimeError(
                "Stable Diffusion model not available. "
                "Check initialization logs for details."
            )
        
        logger.info(
            f"Enhancing texture with Stable Diffusion "
            f"(steps={steps}, scale={conditioning_scale})"
        )
        
        # Set seed if provided
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
        
        # Ensure image is RGB
        if texture_image.mode != 'RGB':
            texture_image = texture_image.convert('RGB')
        
        try:
            # Run ControlNet enhancement
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=texture_image,
                num_inference_steps=steps,
                controlnet_conditioning_scale=conditioning_scale,
                generator=generator,
            )
            
            enhanced_image = result.images[0]
            
            logger.info(
                f"Texture enhanced with SD: {texture_image.size} -> {enhanced_image.size}"
            )
            
            return enhanced_image
            
        except Exception as e:
            logger.error(f"SD enhancement failed: {e}")
            raise
    
    def enhance_texture_batch(
        self,
        texture_images: list[Image.Image],
        prompt: str = "highly detailed texture, sharp details, 8k quality",
        negative_prompt: str = "blurry, smooth, low quality, artifacts",
        steps: int = 20,
        conditioning_scale: float = 0.7,
    ) -> list[Image.Image]:
        """
        Enhance multiple textures in batch.
        
        Args:
            texture_images: List of PIL Images to enhance
            prompt: Positive prompt for generation
            negative_prompt: Negative prompt
            steps: Number of diffusion steps
            conditioning_scale: ControlNet conditioning scale
        
        Returns:
            List of enhanced PIL Images
        """
        if not self.is_available():
            raise RuntimeError("Stable Diffusion model not available")
        
        logger.info(f"Enhancing {len(texture_images)} textures in batch")
        
        enhanced_images = []
        for i, texture_image in enumerate(texture_images):
            logger.info(f"Processing texture {i+1}/{len(texture_images)}")
            enhanced = self.enhance_texture(
                texture_image,
                prompt=prompt,
                negative_prompt=negative_prompt,
                steps=steps,
                conditioning_scale=conditioning_scale,
            )
            enhanced_images.append(enhanced)
        
        return enhanced_images
    
    def unload_model(self) -> None:
        """
        Unload the model from memory.
        
        This can be useful to free up GPU memory when SD enhancement
        is no longer needed.
        """
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("SD model unloaded from memory")
