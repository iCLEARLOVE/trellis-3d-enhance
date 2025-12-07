"""
Geometry optimization module using PyMeshLab.

This module provides mesh optimization capabilities using PyMeshLab,
with conservative operations to preserve the quality of Trellis-generated meshes.
"""

import logging
from pathlib import Path
from typing import Optional
import pymeshlab

logger = logging.getLogger(__name__)


class GeometryOptimizer:
    """
    Optimize 3D model geometry using PyMeshLab.
    
    This class provides methods to optimize mesh geometry with operations like
    removing duplicate vertices, fixing non-manifold edges, and optional
    subdivision/smoothing. Operations are conservative to preserve Trellis quality.
    
    Attributes:
        enable_subdivision: Whether to enable subdivision
        subdivision_iterations: Number of subdivision iterations
        enable_smoothing: Whether to enable light smoothing
        smoothing_steps: Number of smoothing steps
    """
    
    def __init__(
        self,
        enable_subdivision: bool = False,
        subdivision_iterations: int = 1,
        enable_smoothing: bool = False,
        smoothing_steps: int = 1
    ):
        """
        Initialize the GeometryOptimizer.
        
        Args:
            enable_subdivision: Enable subdivision (default: False)
            subdivision_iterations: Number of subdivision iterations (default: 1)
            enable_smoothing: Enable light smoothing (default: False)
            smoothing_steps: Number of smoothing steps (default: 1)
        """
        self.enable_subdivision = enable_subdivision
        self.subdivision_iterations = subdivision_iterations
        self.enable_smoothing = enable_smoothing
        self.smoothing_steps = smoothing_steps
        
        logger.info(
            f"Initializing GeometryOptimizer "
            f"(subdivision={enable_subdivision}, smoothing={enable_smoothing})"
        )
    
    def clean_mesh(self, ms: pymeshlab.MeshSet) -> None:
        """
        Clean a mesh by removing duplicates and fixing issues.
        
        Args:
            ms: PyMeshLab MeshSet to clean
        """
        logger.info("Cleaning mesh...")
        
        # Remove duplicate vertices
        try:
            ms.meshing_remove_duplicate_vertices()
            logger.info("Removed duplicate vertices")
        except Exception as e:
            logger.warning(f"Failed to remove duplicate vertices: {e}")
        
        # Remove duplicate faces
        try:
            ms.meshing_remove_duplicate_faces()
            logger.info("Removed duplicate faces")
        except Exception as e:
            logger.warning(f"Failed to remove duplicate faces: {e}")
        
        # Remove unreferenced vertices
        try:
            ms.meshing_remove_unreferenced_vertices()
            logger.info("Removed unreferenced vertices")
        except Exception as e:
            logger.warning(f"Failed to remove unreferenced vertices: {e}")
        
        # Fix non-manifold edges (conservative approach)
        try:
            ms.meshing_repair_non_manifold_edges()
            logger.info("Fixed non-manifold edges")
        except Exception as e:
            logger.warning(f"Failed to fix non-manifold edges: {e}")
        
        # Remove zero-area faces
        try:
            ms.meshing_remove_null_faces()
            logger.info("Removed null faces")
        except Exception as e:
            logger.warning(f"Failed to remove null faces: {e}")
    
    def subdivide_mesh(self, ms: pymeshlab.MeshSet) -> None:
        """
        Subdivide mesh to add more detail.
        
        Uses conservative subdivision to preserve the original shape while
        adding vertices for smoother geometry.
        
        Args:
            ms: PyMeshLab MeshSet to subdivide
        """
        if not self.enable_subdivision:
            logger.info("Subdivision disabled, skipping")
            return
        
        logger.info(f"Subdividing mesh ({self.subdivision_iterations} iterations)...")
        
        for i in range(self.subdivision_iterations):
            try:
                # Use midpoint subdivision for conservative approach
                ms.meshing_surface_subdivision_midpoint(threshold=pymeshlab.PercentageValue(1.0))
                logger.info(f"Subdivision iteration {i+1}/{self.subdivision_iterations} complete")
            except Exception as e:
                logger.warning(f"Subdivision iteration {i+1} failed: {e}")
                break
    
    def smooth_mesh(self, ms: pymeshlab.MeshSet) -> None:
        """
        Apply light smoothing to mesh.
        
        Uses Laplacian smoothing with conservative settings to slightly
        smooth the mesh without losing detail.
        
        Args:
            ms: PyMeshLab MeshSet to smooth
        """
        if not self.enable_smoothing:
            logger.info("Smoothing disabled, skipping")
            return
        
        logger.info(f"Smoothing mesh ({self.smoothing_steps} steps)...")
        
        try:
            # Use Laplacian smoothing with low iterations for conservative approach
            ms.apply_coord_laplacian_smoothing(
                stepsmoothnum=self.smoothing_steps,
                boundary=True,
                cotangentweight=False,
                selected=False
            )
            logger.info("Mesh smoothing complete")
        except Exception as e:
            logger.warning(f"Smoothing failed: {e}")
    
    def optimize_mesh(
        self,
        mesh_path: str,
        output_path: str,
        create_backup: bool = True
    ) -> str:
        """
        Optimize a 3D mesh file.
        
        This method loads a mesh, applies cleaning operations, and optionally
        applies subdivision and smoothing based on the configuration.
        
        Args:
            mesh_path: Path to input mesh file (.glb or .obj)
            output_path: Path where optimized mesh will be saved
            create_backup: Whether to create a backup of the original file
        
        Returns:
            Path to the optimized mesh file
        
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If file format is not supported
        """
        mesh_path = Path(mesh_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Optimizing mesh: {mesh_path}")
        
        # Validate input
        if not mesh_path.exists():
            raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
        
        ext = mesh_path.suffix.lower()
        if ext not in ['.glb', '.obj', '.ply', '.stl']:
            raise ValueError(f"Unsupported file format: {ext}")
        
        # Create backup if requested
        if create_backup:
            backup_path = mesh_path.parent / f"{mesh_path.stem}_backup{ext}"
            import shutil
            shutil.copy(mesh_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        # Load mesh
        try:
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(str(mesh_path))
            logger.info(f"Mesh loaded: {ms.current_mesh().vertex_number()} vertices, "
                       f"{ms.current_mesh().face_number()} faces")
        except Exception as e:
            logger.error(f"Failed to load mesh: {e}")
            raise
        
        # Clean mesh
        self.clean_mesh(ms)
        
        # Optional: Subdivide mesh
        self.subdivide_mesh(ms)
        
        # Optional: Smooth mesh
        self.smooth_mesh(ms)
        
        # Save optimized mesh
        try:
            # Determine output format from extension
            output_ext = output_path.suffix.lower()
            
            # Save mesh
            ms.save_current_mesh(str(output_path))
            
            logger.info(
                f"Optimized mesh saved: {ms.current_mesh().vertex_number()} vertices, "
                f"{ms.current_mesh().face_number()} faces -> {output_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to save mesh: {e}")
            raise
        
        return str(output_path)
    
    def get_mesh_stats(self, mesh_path: str) -> dict:
        """
        Get statistics about a mesh file.
        
        Args:
            mesh_path: Path to mesh file
        
        Returns:
            Dictionary with mesh statistics (vertices, faces, edges, etc.)
        """
        mesh_path = Path(mesh_path)
        
        if not mesh_path.exists():
            raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
        
        try:
            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(str(mesh_path))
            mesh = ms.current_mesh()
            
            stats = {
                'vertices': mesh.vertex_number(),
                'faces': mesh.face_number(),
                'edges': mesh.edge_number(),
                'is_compact': mesh.is_compact(),
                'bounding_box': mesh.bounding_box().diagonal(),
            }
            
            logger.info(f"Mesh stats for {mesh_path.name}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get mesh stats: {e}")
            raise
