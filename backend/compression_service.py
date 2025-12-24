import os
import sys
import uuid
import asyncio
import logging
import time
from typing import Dict, Optional, Callable
import torch
from torch import nn
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import src.tn.tt_layers as tt_layers
from src.qtc.apply import count_params
from backend.websocket_manager import connection_manager
from backend.models import CompressionStatus, CompressionResult

logger = logging.getLogger(__name__)


class CompressionService:
    """Service for managing compression jobs"""
    
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.model_cache: Dict[str, tuple] = {}  # Cache for loaded models
        self.pending_core_data: Dict[str, list] = {}  # job_id -> list of core_data
    
    def create_job(self, model_name: str, compression_configs: Dict) -> str:
        """Create a new compression job"""
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "job_id": job_id,
            "model_name": model_name,
            "compression_configs": compression_configs,
            "status": CompressionStatus.PENDING,
            "created_at": time.time(),
            "result": None,
            "error": None
        }
        logger.info(f"Created compression job {job_id} for model {model_name}")
        return job_id
    
    async def run_compression(
        self, 
        job_id: str,
        progress_callback: Optional[Callable] = None
    ) -> CompressionResult:
        """Run compression job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        job["status"] = CompressionStatus.RUNNING
        
        try:
            # Broadcast start
            await connection_manager.broadcast_status(job_id, "running", {
                "message": "Starting compression..."
            })
            
            # Load model
            await connection_manager.broadcast_status(job_id, "running", {
                "message": f"Loading model {job['model_name']}..."
            })
            
            model, tokenizer, device = await self._load_model(job['model_name'])
            
            # Count original parameters
            original_params = count_params(model)
            original_size_mb = self._get_model_size_mb(model)
            
            await connection_manager.broadcast_metrics(job_id, {
                "original_params": original_params,
                "original_size_mb": original_size_mb,
                "step": 0
            })
            
            # Create compressed model
            await connection_manager.broadcast_status(job_id, "running", {
                "message": "Creating compressed model..."
            })
            
            compressed_model = await self._create_compressed_model(
                model, 
                job['compression_configs'],
                progress_callback=lambda step, data: self._on_progress(job_id, step, data),
                job_id=job_id
            )
            
            # Broadcast all pending metrics collected during sync operation
            if "pending_metrics" in job:
                for metrics in job["pending_metrics"]:
                    await connection_manager.broadcast_metrics(job_id, metrics)
                del job["pending_metrics"]
            
            # Broadcast all collected TT core data
            if job_id in self.pending_core_data:
                for core_data in self.pending_core_data[job_id]:
                    await connection_manager.broadcast_tt_core_data(job_id, core_data)
                del self.pending_core_data[job_id]
            
            # Count compressed parameters
            compressed_params = count_params(compressed_model)
            compressed_size_mb = self._get_model_size_mb(compressed_model)
            compression_ratio = original_params / compressed_params if compressed_params > 0 else 0.0
            
            # Final metrics
            await connection_manager.broadcast_metrics(job_id, {
                "compressed_params": compressed_params,
                "compressed_size_mb": compressed_size_mb,
                "compression_ratio": compression_ratio,
                "step": 100
            })
            
            result = CompressionResult(
                job_id=job_id,
                status=CompressionStatus.COMPLETED,
                original_params=original_params,
                compressed_params=compressed_params,
                compression_ratio=compression_ratio,
                original_size_mb=original_size_mb,
                compressed_size_mb=compressed_size_mb
            )
            
            # Store compressed model for export
            job["compressed_model"] = compressed_model
            job["model_name"] = job['model_name']
            job["status"] = CompressionStatus.COMPLETED
            job["result"] = result
            
            await connection_manager.broadcast_status(job_id, "completed", {
                "compression_ratio": compression_ratio,
                "original_params": original_params,
                "compressed_params": compressed_params
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Compression job {job_id} failed: {e}", exc_info=True)
            job["status"] = CompressionStatus.FAILED
            job["error"] = str(e)
            
            await connection_manager.broadcast_error(job_id, str(e))
            
            return CompressionResult(
                job_id=job_id,
                status=CompressionStatus.FAILED,
                original_params=0,
                compressed_params=0,
                compression_ratio=0.0,
                original_size_mb=0.0,
                compressed_size_mb=0.0,
                error=str(e)
            )
    
    async def _load_model(self, model_name: str) -> tuple:
        """Load model with caching"""
        if model_name in self.model_cache:
            return self.model_cache[model_name]
        
        # Run in thread pool to avoid blocking
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # If no running loop, get the event loop
            loop = asyncio.get_event_loop()
        model, tokenizer, device = await loop.run_in_executor(
            None,
            self._load_model_sync,
            model_name
        )
        
        self.model_cache[model_name] = (model, tokenizer, device)
        return model, tokenizer, device
    
    def _load_model_sync(self, model_name: str) -> tuple:
        """Synchronous model loading"""
        device = torch.device('cpu')  # Force CPU for now
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map='cpu'
        )
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        return model, tokenizer, device
    
    async def _create_compressed_model(
        self,
        model: nn.Module,
        compression_configs: Dict,
        progress_callback: Optional[Callable] = None,
        job_id: Optional[str] = None
    ) -> nn.Module:
        """Create compressed model"""
        # Run in thread pool
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # If no running loop, get the event loop
            loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            None,
            self._create_compressed_model_sync,
            model,
            compression_configs,
            progress_callback,
            job_id
        )
    
    def _extract_tt_core_data(self, tt_layer, layer_name: str, layer_index: int) -> Dict:
        """Extract TT core data for visualization"""
        cores_data = []
        try:
            for core_idx, core in enumerate(tt_layer.cores):
                core_shape = list(core.shape)
                # Flatten core values for transmission (convert to list for JSON)
                # Use .tolist() directly instead of numpy to avoid any asyncio issues
                try:
                    # Try direct tensor to list conversion
                    core_tensor = core.detach().cpu()
                    core_values = core_tensor.flatten().tolist()
                except Exception:
                    # Fallback: use numpy if direct conversion fails
                    core_values = core_tensor.numpy().flatten().tolist()
                
                cores_data.append({
                    "core_index": core_idx,
                    "core_shape": core_shape,
                    "core_values": core_values[:1000] if len(core_values) > 1000 else core_values,  # Limit size for transmission
                    "rank_left": int(core_shape[0]),
                    "rank_right": int(core_shape[-1]),
                    "out_mode": int(core_shape[1]) if len(core_shape) > 1 else 1,
                    "in_mode": int(core_shape[2]) if len(core_shape) > 2 else 1,
                })
        except Exception as e:
            logger.warning(f"Error extracting core data for {layer_name}: {e}")
            # Return minimal data if extraction fails
            cores_data = [{
                "core_index": 0,
                "core_shape": [1, 1, 1, 1],
                "core_values": [],
                "rank_left": 1,
                "rank_right": 1,
                "out_mode": 1,
                "in_mode": 1,
            }]
        
        return {
            "layer_name": layer_name,
            "layer_index": layer_index,
            "in_modes": tt_layer.in_modes if hasattr(tt_layer, 'in_modes') else [],
            "out_modes": tt_layer.out_modes if hasattr(tt_layer, 'out_modes') else [],
            "ranks": tt_layer.ranks if hasattr(tt_layer, 'ranks') else [],
            "cores": cores_data,
            "position": {
                "x": layer_index * 2.0,  # Spacing between layers
                "y": 0.0,
                "z": 0.0
            }
        }
    
    def _create_compressed_model_sync(
        self,
        model: nn.Module,
        compression_configs: Dict,
        progress_callback: Optional[Callable] = None,
        job_id: Optional[str] = None
    ) -> nn.Module:
        """Synchronous compressed model creation"""
        # Create a copy of the model
        model_name = model.config._name_or_path if hasattr(model.config, '_name_or_path') else 'gpt2'
        compressed_model = type(model).from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map='cpu'
        )
        
        # Replace modules with TT layers
        total_layers = len(compression_configs)
        for idx, (name, config) in enumerate(compression_configs.items()):
            try:
                module = dict(model.named_modules())[name]
                
                if isinstance(module, nn.Linear):
                    try:
                        tt_layer = tt_layers.TTLinear(
                            in_modes=config['in_modes'],
                            out_modes=config['out_modes'],
                            ranks=config['ranks'],
                            bias=(module.bias is not None),
                            use_dense_path=False
                        )
                    except Exception as e:
                        logger.warning(f"Error creating TTLinear for layer {name}: {e}", exc_info=True)
                        continue
                elif isinstance(module, nn.Embedding):
                    try:
                        tt_layer = tt_layers.TTEmbedding(
                            in_modes=config['in_modes'],
                            out_modes=config['out_modes'],
                            ranks=config['ranks'],
                            use_dense_path=False
                        )
                    except Exception as e:
                        logger.warning(f"Error creating TTEmbedding for layer {name}: {e}", exc_info=True)
                        continue
                else:
                    logger.debug(f"Skipping layer {name}: not Linear or Embedding")
                    continue
                
                # Set the TT layer
                try:
                    parent_name = '.'.join(name.split('.')[:-1])
                    child_name = name.split('.')[-1]
                    
                    if parent_name:
                        parent = compressed_model.get_submodule(parent_name)
                        setattr(parent, child_name, tt_layer)
                    else:
                        setattr(compressed_model, child_name, tt_layer)
                except Exception as e:
                    logger.warning(f"Error setting TT layer for {name}: {e}", exc_info=True)
                    continue
                
                # Extract TT core data for visualization
                if job_id:
                    try:
                        core_data = self._extract_tt_core_data(tt_layer, name, idx)
                        if job_id not in self.pending_core_data:
                            self.pending_core_data[job_id] = []
                        self.pending_core_data[job_id].append(core_data)
                    except Exception as e:
                        logger.warning(f"Error extracting TT core data for {name}: {e}", exc_info=True)
                        # Continue even if core data extraction fails
                
                if progress_callback:
                    try:
                        progress_callback(idx + 1, {"layer": name})
                    except Exception as e:
                        # Don't fail the whole compression if progress callback fails
                        logger.debug(f"Progress callback failed for {name}: {e}")
                    
            except Exception as e:
                logger.warning(f"Error compressing layer {name}: {e}", exc_info=True)
                continue
        
        return compressed_model
    
    def _get_model_size_mb(self, model: nn.Module) -> float:
        """Calculate model size in MB"""
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
        return (param_size + buffer_size) / (1024 ** 2)
    
    def _on_progress(self, job_id: str, step: int, data: Dict):
        """Progress callback - stores metrics to be sent later"""
        # Store metrics to be sent after sync operation completes
        # We can't use asyncio.create_task here because we're in a thread executor
        if job_id not in self.jobs:
            return
        
        # Store metrics in job for later broadcasting
        if "pending_metrics" not in self.jobs[job_id]:
            self.jobs[job_id]["pending_metrics"] = []
        
        self.jobs[job_id]["pending_metrics"].append({
            "step": step,
            **data
        })
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job information"""
        return self.jobs.get(job_id)
    
    def get_job_result(self, job_id: str) -> Optional[CompressionResult]:
        """Get job result"""
        job = self.jobs.get(job_id)
        if job and job.get("result"):
            return job["result"]
        return None


# Global service instance
compression_service = CompressionService()

