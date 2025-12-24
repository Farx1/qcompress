import os
import sys
import asyncio
import logging
import uuid
from typing import Dict, Optional, List, Callable
import torch
from torch import nn
from transformers import AutoModelForCausalLM, AutoTokenizer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.websocket_manager import connection_manager

logger = logging.getLogger(__name__)


class BenchmarkService:
    """Service for running benchmark evaluations on compressed models"""
    
    def __init__(self):
        self.benchmark_jobs: Dict[str, Dict] = {}
    
    def create_benchmark_job(self, job_id: str, model: nn.Module, tokenizer, tasks: List[str] = None) -> str:
        """Create a new benchmark job"""
        benchmark_id = str(uuid.uuid4())
        if tasks is None:
            tasks = ['hellaswag', 'arc', 'mmlu', 'wikitext']
        
        self.benchmark_jobs[benchmark_id] = {
            "benchmark_id": benchmark_id,
            "job_id": job_id,
            "model": model,
            "tokenizer": tokenizer,
            "tasks": tasks,
            "status": "pending",
            "results": {},
            "progress": 0.0
        }
        logger.info(f"Created benchmark job {benchmark_id} for compression job {job_id}")
        return benchmark_id
    
    async def run_benchmark(
        self,
        benchmark_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """Run benchmark evaluation"""
        if benchmark_id not in self.benchmark_jobs:
            raise ValueError(f"Benchmark job {benchmark_id} not found")
        
        job = self.benchmark_jobs[benchmark_id]
        job["status"] = "running"
        job_id = job["job_id"]
        model = job["model"]
        tokenizer = job["tokenizer"]
        tasks = job["tasks"]
        
        try:
            # Broadcast start
            await connection_manager.broadcast_benchmark_result(job_id, {
                "status": "running",
                "message": "Starting benchmark evaluation...",
                "progress": 0.0
            })
            
            results = {}
            total_tasks = len(tasks)
            
            for idx, task_name in enumerate(tasks):
                await connection_manager.broadcast_benchmark_result(job_id, {
                    "status": "running",
                    "task": task_name,
                    "message": f"Running {task_name}...",
                    "progress": idx / total_tasks
                })
                
                # Run benchmark task (simplified - in production, use lm-eval)
                task_result = await self._run_task(model, tokenizer, task_name)
                results[task_name] = task_result
                
                # Broadcast result
                await connection_manager.broadcast_benchmark_result(job_id, {
                    "status": "running",
                    "task": task_name,
                    "metrics": task_result,
                    "progress": (idx + 1) / total_tasks
                })
            
            # Calculate overall metrics
            overall_metrics = self._calculate_overall_metrics(results)
            
            job["status"] = "completed"
            job["results"] = results
            job["overall_metrics"] = overall_metrics
            
            # Broadcast completion
            await connection_manager.broadcast_benchmark_result(job_id, {
                "status": "completed",
                "results": results,
                "overall_metrics": overall_metrics,
                "progress": 1.0
            })
            
            return {
                "benchmark_id": benchmark_id,
                "status": "completed",
                "results": results,
                "overall_metrics": overall_metrics
            }
            
        except Exception as e:
            logger.error(f"Benchmark job {benchmark_id} failed: {e}", exc_info=True)
            job["status"] = "failed"
            job["error"] = str(e)
            
            await connection_manager.broadcast_benchmark_result(job_id, {
                "status": "failed",
                "error": str(e)
            })
            
            return {
                "benchmark_id": benchmark_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def _run_task(self, model: nn.Module, tokenizer, task_name: str) -> Dict:
        """Run a single benchmark task"""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._run_task_sync,
            model,
            tokenizer,
            task_name
        )
    
    def _run_task_sync(self, model: nn.Module, tokenizer, task_name: str) -> Dict:
        """Synchronous task execution"""
        model.eval()
        
        # Simplified benchmark - in production, integrate with lm-eval
        # For now, we'll compute perplexity on a small sample
        
        if task_name == "wikitext":
            # Compute perplexity on a sample text
            sample_text = "The quick brown fox jumps over the lazy dog. " * 10
            inputs = tokenizer(sample_text, return_tensors="pt", truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss if hasattr(outputs, 'loss') else None
                
                if loss is not None:
                    perplexity = torch.exp(loss).item()
                else:
                    # Fallback: compute from logits
                    logits = outputs.logits
                    shift_logits = logits[..., :-1, :].contiguous()
                    shift_labels = inputs["input_ids"][..., 1:].contiguous()
                    loss_fct = nn.CrossEntropyLoss()
                    loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
                    perplexity = torch.exp(loss).item()
            
            return {
                "perplexity": perplexity,
                "loss": float(loss.item()) if isinstance(loss, torch.Tensor) else None,
                "samples": 1
            }
        
        elif task_name in ["hellaswag", "arc", "mmlu"]:
            # Placeholder for actual benchmark tasks
            # In production, use lm-eval library
            return {
                "accuracy": 0.0,
                "f1": 0.0,
                "samples": 0,
                "note": "Full benchmark integration requires lm-eval library"
            }
        
        else:
            return {
                "error": f"Unknown task: {task_name}",
                "samples": 0
            }
    
    def _calculate_overall_metrics(self, results: Dict) -> Dict:
        """Calculate overall metrics from task results"""
        metrics = {
            "total_tasks": len(results),
            "completed_tasks": 0,
            "average_accuracy": 0.0,
            "average_perplexity": None,
            "total_samples": 0
        }
        
        accuracies = []
        perplexities = []
        
        for task_name, result in results.items():
            if "error" not in result:
                metrics["completed_tasks"] += 1
                metrics["total_samples"] += result.get("samples", 0)
                
                if "accuracy" in result:
                    accuracies.append(result["accuracy"])
                if "perplexity" in result:
                    perplexities.append(result["perplexity"])
        
        if accuracies:
            metrics["average_accuracy"] = sum(accuracies) / len(accuracies)
        
        if perplexities:
            metrics["average_perplexity"] = sum(perplexities) / len(perplexities)
        
        return metrics
    
    def get_benchmark_job(self, benchmark_id: str) -> Optional[Dict]:
        """Get benchmark job information"""
        return self.benchmark_jobs.get(benchmark_id)
    
    def get_benchmark_result(self, benchmark_id: str) -> Optional[Dict]:
        """Get benchmark result"""
        job = self.benchmark_jobs.get(benchmark_id)
        if job and job.get("results"):
            return {
                "benchmark_id": benchmark_id,
                "status": job["status"],
                "results": job.get("results", {}),
                "overall_metrics": job.get("overall_metrics", {})
            }
        return None


# Global service instance
benchmark_service = BenchmarkService()

