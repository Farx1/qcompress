import os
import logging
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
import torch
from torch import nn

logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting compressed models to various formats"""
    
    def __init__(self):
        self.export_dir = Path(os.getenv("EXPORT_DIR", os.path.join(tempfile.gettempdir(), "qcompress_exports")))
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_pytorch(
        self,
        model: nn.Module,
        job_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export model to PyTorch format (.pt)
        
        Args:
            model: The compressed model to export
            job_id: Job ID for filename
            metadata: Optional metadata to include
            
        Returns:
            Path to exported file
        """
        try:
            export_path = self.export_dir / f"{job_id}_model.pt"
            
            # Prepare state dict
            state_dict = model.state_dict()
            
            # Add metadata if provided
            export_data = {
                "model_state_dict": state_dict,
                "metadata": metadata or {}
            }
            
            # Save model
            torch.save(export_data, export_path)
            
            logger.info(f"Exported model to PyTorch format: {export_path}")
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export to PyTorch: {e}")
            raise
    
    def export_to_safetensors(
        self,
        model: nn.Module,
        job_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export model to SafeTensors format
        
        Args:
            model: The compressed model to export
            job_id: Job ID for filename
            metadata: Optional metadata to include
            
        Returns:
            Path to exported file
        """
        try:
            try:
                from safetensors.torch import save_file
            except ImportError:
                raise ImportError(
                    "safetensors is required for SafeTensors export. "
                    "Install it with: pip install safetensors"
                )
            
            export_path = self.export_dir / f"{job_id}_model.safetensors"
            
            # Get state dict
            state_dict = model.state_dict()
            
            # Save in SafeTensors format
            save_file(state_dict, export_path)
            
            # Save metadata separately if provided
            if metadata:
                metadata_path = self.export_dir / f"{job_id}_metadata.json"
                import json
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            logger.info(f"Exported model to SafeTensors format: {export_path}")
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export to SafeTensors: {e}")
            raise
    
    def export_to_onnx(
        self,
        model: nn.Module,
        job_id: str,
        input_shape: tuple = (1, 128),
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export model to ONNX format
        
        Args:
            model: The compressed model to export
            job_id: Job ID for filename
            input_shape: Input shape for ONNX export (batch_size, sequence_length)
            metadata: Optional metadata to include
            
        Returns:
            Path to exported file
        """
        try:
            try:
                import onnx
            except ImportError:
                raise ImportError(
                    "onnx is required for ONNX export. "
                    "Install it with: pip install onnx"
                )
            
            export_path = self.export_dir / f"{job_id}_model.onnx"
            
            # Set model to eval mode
            model.eval()
            
            # Create dummy input
            dummy_input = torch.randint(0, 50257, input_shape)
            
            # Export to ONNX
            torch.onnx.export(
                model,
                dummy_input,
                export_path,
                input_names=['input_ids'],
                output_names=['logits'],
                dynamic_axes={
                    'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                    'logits': {0: 'batch_size', 1: 'sequence_length'}
                },
                opset_version=14,
                do_constant_folding=True,
            )
            
            # Add metadata to ONNX model if provided
            if metadata:
                onnx_model = onnx.load(str(export_path))
                for key, value in metadata.items():
                    meta = onnx_model.metadata_props.add()
                    meta.key = str(key)
                    meta.value = str(value)
                onnx.save(onnx_model, str(export_path))
            
            logger.info(f"Exported model to ONNX format: {export_path}")
            return str(export_path)
        except Exception as e:
            logger.error(f"Failed to export to ONNX: {e}")
            raise
    
    def get_export_metadata(self, job_id: str, compression_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata for export
        
        Args:
            job_id: Job ID
            compression_result: Compression result data
            
        Returns:
            Metadata dictionary
        """
        return {
            "job_id": job_id,
            "compression_ratio": compression_result.get("compression_ratio", 0),
            "original_params": compression_result.get("original_params", 0),
            "compressed_params": compression_result.get("compressed_params", 0),
            "original_size_mb": compression_result.get("original_size_mb", 0),
            "compressed_size_mb": compression_result.get("compressed_size_mb", 0),
            "model_name": compression_result.get("model_name", "unknown"),
        }
    
    def cleanup_export(self, file_path: str):
        """Clean up exported file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up export file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup export file {file_path}: {e}")


# Global service instance
export_service = ExportService()

