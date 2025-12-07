"""
Utility functions for 3D model enhancement.

This module provides helper functions for texture extraction, file validation,
downloading pretrained weights, and other common operations.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Tuple
import requests
from tqdm import tqdm
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


def validate_file(file_path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Validate if a file exists and has a valid extension.
    
    Args:
        file_path: Path to the file to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.glb', '.obj'])
                          If None, only checks if file exists
    
    Returns:
        True if file is valid, False otherwise
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file extension is not allowed
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if allowed_extensions is not None:
        ext = path.suffix.lower()
        if ext not in allowed_extensions:
            raise ValueError(
                f"Invalid file extension: {ext}. "
                f"Allowed extensions: {', '.join(allowed_extensions)}"
            )
    
    logger.info(f"File validated: {file_path}")
    return True


def download_file(url: str, output_path: str, desc: str = "Downloading") -> str:
    """
    Download a file from a URL with progress bar.
    
    Args:
        url: URL to download from
        output_path: Path where the file will be saved
        desc: Description for the progress bar
    
    Returns:
        Path to the downloaded file
    
    Raises:
        requests.RequestException: If download fails
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists
    if output_path.exists():
        logger.info(f"File already exists: {output_path}")
        return str(output_path)
    
    logger.info(f"Downloading from {url} to {output_path}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f, tqdm(
            desc=desc,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)
        
        logger.info(f"Download complete: {output_path}")
        return str(output_path)
    
    except requests.RequestException as e:
        if output_path.exists():
            output_path.unlink()
        logger.error(f"Download failed: {e}")
        raise


def extract_texture_from_mesh(
    mesh_path: str,
    texture_size: int = 2048,
    output_dir: Optional[str] = None
) -> Optional[str]:
    """
    Extract texture from a 3D mesh file (GLB/OBJ).
    
    This function attempts to extract texture images from mesh files.
    For GLB files, it extracts embedded textures.
    For OBJ files, it looks for associated MTL and texture files.
    
    Args:
        mesh_path: Path to the mesh file (.glb or .obj)
        texture_size: Target texture size (default: 2048)
        output_dir: Directory to save extracted texture (if None, uses temp dir)
    
    Returns:
        Path to extracted texture image, or None if no texture found
    """
    import trimesh
    
    mesh_path = Path(mesh_path)
    if output_dir is None:
        output_dir = mesh_path.parent / "textures"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Extracting texture from {mesh_path}")
    
    try:
        # Load mesh with trimesh
        scene = trimesh.load(str(mesh_path))
        
        # Handle both Scene and single mesh
        if isinstance(scene, trimesh.Scene):
            # Get textures from all geometries in the scene
            for name, geometry in scene.geometry.items():
                if hasattr(geometry, 'visual') and hasattr(geometry.visual, 'material'):
                    material = geometry.visual.material
                    
                    # Check for base color texture
                    if hasattr(material, 'baseColorTexture') and material.baseColorTexture is not None:
                        texture = material.baseColorTexture
                        texture_path = output_dir / f"{mesh_path.stem}_texture.png"
                        texture.save(texture_path)
                        logger.info(f"Extracted texture to {texture_path}")
                        return str(texture_path)
                    
                    # Check for image attribute
                    if hasattr(material, 'image') and material.image is not None:
                        texture = material.image
                        texture_path = output_dir / f"{mesh_path.stem}_texture.png"
                        if isinstance(texture, Image.Image):
                            texture.save(texture_path)
                        else:
                            Image.fromarray(texture).save(texture_path)
                        logger.info(f"Extracted texture to {texture_path}")
                        return str(texture_path)
        
        else:
            # Single mesh
            if hasattr(scene, 'visual') and hasattr(scene.visual, 'material'):
                material = scene.visual.material
                
                if hasattr(material, 'baseColorTexture') and material.baseColorTexture is not None:
                    texture = material.baseColorTexture
                    texture_path = output_dir / f"{mesh_path.stem}_texture.png"
                    texture.save(texture_path)
                    logger.info(f"Extracted texture to {texture_path}")
                    return str(texture_path)
                
                if hasattr(material, 'image') and material.image is not None:
                    texture = material.image
                    texture_path = output_dir / f"{mesh_path.stem}_texture.png"
                    if isinstance(texture, Image.Image):
                        texture.save(texture_path)
                    else:
                        Image.fromarray(texture).save(texture_path)
                    logger.info(f"Extracted texture to {texture_path}")
                    return str(texture_path)
        
        logger.warning(f"No texture found in {mesh_path}")
        return None
    
    except Exception as e:
        logger.error(f"Failed to extract texture: {e}")
        return None


def apply_texture_to_mesh(
    mesh_path: str,
    texture_path: str,
    output_path: str
) -> str:
    """
    Apply an enhanced texture back to a 3D mesh.
    
    Args:
        mesh_path: Path to the original mesh file
        texture_path: Path to the enhanced texture image
        output_path: Path where the new mesh will be saved
    
    Returns:
        Path to the output mesh file
    """
    import trimesh
    from PIL import Image
    
    logger.info(f"Applying texture {texture_path} to mesh {mesh_path}")
    
    # Load mesh
    scene = trimesh.load(str(mesh_path))
    
    # Load enhanced texture
    texture_image = Image.open(texture_path)
    
    # Apply texture based on mesh type
    if isinstance(scene, trimesh.Scene):
        for name, geometry in scene.geometry.items():
            if hasattr(geometry, 'visual') and hasattr(geometry.visual, 'material'):
                # Update material with new texture
                if hasattr(geometry.visual.material, 'baseColorTexture'):
                    geometry.visual.material.baseColorTexture = texture_image
                elif hasattr(geometry.visual.material, 'image'):
                    geometry.visual.material.image = texture_image
    else:
        if hasattr(scene, 'visual') and hasattr(scene.visual, 'material'):
            if hasattr(scene.visual.material, 'baseColorTexture'):
                scene.visual.material.baseColorTexture = texture_image
            elif hasattr(scene.visual.material, 'image'):
                scene.visual.material.image = texture_image
    
    # Save the mesh with updated texture
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scene.export(str(output_path))
    
    logger.info(f"Mesh with enhanced texture saved to {output_path}")
    return str(output_path)


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO) -> None:
    """
    Set up logging configuration.
    
    Args:
        log_file: Path to log file (if None, only logs to console)
        level: Logging level (default: INFO)
    """
    handlers = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def get_device() -> str:
    """
    Get the best available device (CUDA, MPS, or CPU).
    
    Returns:
        Device string ('cuda', 'mps', or 'cpu')
    """
    import torch
    
    if torch.cuda.is_available():
        device = 'cuda'
        logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        device = 'mps'
        logger.info("Using MPS device")
    else:
        device = 'cpu'
        logger.warning("No GPU available, using CPU (this will be slow)")
    
    return device


def ensure_dir(directory: str) -> Path:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Path to directory
    
    Returns:
        Path object for the directory
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path
