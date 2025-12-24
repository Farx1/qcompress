"""
Mock backend for testing frontend without heavy dependencies
Generates realistic compression outputs
"""
import asyncio
import json
import logging
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import random
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class ModelInfo(BaseModel):
    name: str
    description: str
    parameters: int
    size_mb: float

class CompressionRequest(BaseModel):
    model_name: str
    compression_ratio: float = 0.5
    target_rank: int = 10
    penalty_weight: float = 0.1

class CompressionResult(BaseModel):
    job_id: str
    status: str
    model_name: str
    original_size: float
    compressed_size: float
    compression_ratio: float
    speed_gain: float
    quality_loss: float
    original_params: int
    compressed_params: int
    timestamp: str

class CompressionMetrics(BaseModel):
    step: int
    compression_ratio: float
    original_params: int
    compressed_params: int
    timestamp: float
    layer_name: str

class ChatResponse(BaseModel):
    response: str
    model_used: str
    generation_time_ms: float

class BenchmarkResult(BaseModel):
    job_id: str
    test_name: str
    original_time: float
    compressed_time: float
    speedup: float
    accuracy_drop: float

# Create app
app = FastAPI(
    title="QCompress API (Mock)",
    description="Mock backend for testing frontend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
active_jobs: Dict[str, Dict] = {}
job_metrics: Dict[str, List[Dict]] = {}
job_results: Dict[str, Dict] = {}

# Available models with realistic parameters
AVAILABLE_MODELS = {
    "distilgpt2": {
        "name": "DistilGPT-2",
        "description": "Lightweight model based on GPT-2",
        "parameters": 82000000,
        "size_mb": 330,
        "layers": 12,
    },
    "gpt2": {
        "name": "GPT-2",
        "description": "Original GPT-2 language model",
        "parameters": 124000000,
        "size_mb": 500,
        "layers": 12,
    },
    "gpt2-medium": {
        "name": "GPT-2 Medium",
        "description": "Medium-sized GPT-2 variant",
        "parameters": 355000000,
        "size_mb": 1400,
        "layers": 24,
    },
    "gpt2-large": {
        "name": "GPT-2 Large",
        "description": "Large-sized GPT-2 variant",
        "parameters": 774000000,
        "size_mb": 3100,
        "layers": 36,
    },
    "microsoft/DialoGPT-small": {
        "name": "DialoGPT-small",
        "description": "Small dialogue model",
        "parameters": 117000000,
        "size_mb": 470,
        "layers": 12,
    },
    "microsoft/DialoGPT-medium": {
        "name": "DialoGPT-medium",
        "description": "Medium dialogue model",
        "parameters": 345000000,
        "size_mb": 1300,
        "layers": 24,
    },
    "meta-llama/Llama-2-7b": {
        "name": "Llama 2 (7B)",
        "description": "Meta Llama 2 7 billion parameters",
        "parameters": 7000000000,
        "size_mb": 13500,
        "layers": 32,
    },
    "mistralai/Mistral-7B": {
        "name": "Mistral 7B",
        "description": "Mistral 7 billion parameter model",
        "parameters": 7000000000,
        "size_mb": 14000,
        "layers": 32,
    },
}

def calculate_compression_output(model_id: str, compression_ratio: float, target_rank: int, penalty_weight: float) -> Dict:
    """Calculate realistic compression outputs based on model and parameters"""
    
    model_info = AVAILABLE_MODELS.get(model_id, AVAILABLE_MODELS["distilgpt2"])
    
    original_params = model_info["parameters"]
    original_size_mb = model_info["size_mb"]
    
    # Calculate compressed parameters based on compression ratio
    # Compression ratio affects how many parameters are retained
    compressed_params = int(original_params * (1 - compression_ratio))
    
    # Calculate compressed size (slightly better than linear due to quantization)
    compression_factor = 1 - compression_ratio
    compressed_size_mb = original_size_mb * compression_factor * 0.95  # 95% due to some overhead reduction
    
    # Calculate speed gain (typically 1.5x to 3x depending on compression)
    # Higher compression = more speed gain, but with diminishing returns
    speed_gain = min(0.3 + compression_ratio * 1.5, 0.65)  # Max 65% speedup
    
    # Calculate quality loss (typically 1-5% for reasonable compression)
    # Higher compression and higher penalty weight = lower quality loss
    quality_loss = max(0.01, compression_ratio * 0.04 - penalty_weight * 0.01)
    
    # Add some randomness to make it realistic
    quality_loss += random.uniform(-0.005, 0.005)
    speed_gain += random.uniform(-0.02, 0.02)
    
    return {
        "original_params": original_params,
        "compressed_params": max(1, compressed_params),
        "original_size_mb": original_size_mb,
        "compressed_size_mb": max(10, compressed_size_mb),
        "compression_ratio": compression_ratio,
        "speed_gain": max(0, min(1, speed_gain)),
        "quality_loss": max(0, min(1, quality_loss)),
        "layers": model_info["layers"],
    }

async def simulate_compression(job_id: str, model_id: str, compression_ratio: float, target_rank: int, penalty_weight: float):
    """Simulate compression process with WebSocket updates"""
    
    try:
        model_info = AVAILABLE_MODELS.get(model_id, AVAILABLE_MODELS["distilgpt2"])
        output = calculate_compression_output(model_id, compression_ratio, target_rank, penalty_weight)
        
        # Simulate compression steps
        num_steps = min(20, output["layers"])
        
        for step in range(num_steps):
            # Calculate metrics for this step
            progress = (step + 1) / num_steps
            current_params = int(output["original_params"] * (1 - compression_ratio * progress))
            current_ratio = 1 - (current_params / output["original_params"])
            
            metrics = {
                "step": step + 1,
                "total_steps": num_steps,
                "compression_ratio": current_ratio,
                "original_params": output["original_params"],
                "compressed_params": current_params,
                "layer_name": f"layer_{step % output['layers']}",
                "timestamp": datetime.now().timestamp(),
            }
            
            if job_id in active_jobs:
                if job_id not in job_metrics:
                    job_metrics[job_id] = []
                job_metrics[job_id].append(metrics)
            
            # Simulate processing time
            await asyncio.sleep(0.5)
        
        # Store final result
        job_results[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "model_name": model_info["name"],
            "original_size": output["original_size_mb"],
            "compressed_size": output["compressed_size_mb"],
            "compression_ratio": output["compression_ratio"],
            "speed_gain": output["speed_gain"],
            "quality_loss": output["quality_loss"],
            "original_params": output["original_params"],
            "compressed_params": output["compressed_params"],
            "timestamp": datetime.now().isoformat(),
        }
        
        if job_id in active_jobs:
            active_jobs[job_id]["status"] = "completed"
            
    except Exception as e:
        logger.error(f"Error in compression simulation: {e}")
        if job_id in active_jobs:
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["error"] = str(e)

# Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "parameters": info["parameters"],
                "size_mb": info["size_mb"],
            }
            for model_id, info in AVAILABLE_MODELS.items()
        ]
    }

@app.post("/compress")
async def start_compression(request: CompressionRequest):
    """Start a compression job"""
    
    if request.model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {request.model_name} not found")
    
    job_id = str(uuid.uuid4())
    
    # Create job
    active_jobs[job_id] = {
        "job_id": job_id,
        "model_name": request.model_name,
        "status": "running",
        "compression_ratio": request.compression_ratio,
        "target_rank": request.target_rank,
        "penalty_weight": request.penalty_weight,
        "created_at": datetime.now().isoformat(),
    }
    
    # Start compression simulation in background
    asyncio.create_task(
        simulate_compression(
            job_id,
            request.model_name,
            request.compression_ratio,
            request.target_rank,
            request.penalty_weight,
        )
    )
    
    return {
        "job_id": job_id,
        "status": "running",
        "message": f"Compression job {job_id} started"
    }

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = active_jobs[job_id]
    metrics = job_metrics.get(job_id, [])
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "model_name": job["model_name"],
        "metrics_count": len(metrics),
        "created_at": job["created_at"],
    }

@app.get("/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """Get job results"""
    
    if job_id not in job_results:
        raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")
    
    return job_results[job_id]

@app.get("/jobs/{job_id}/metrics")
async def get_job_metrics(job_id: str):
    """Get job metrics"""
    
    if job_id not in job_metrics:
        raise HTTPException(status_code=404, detail=f"Metrics for job {job_id} not found")
    
    return {
        "job_id": job_id,
        "metrics": job_metrics[job_id]
    }

@app.post("/chat")
async def chat(model_name: str, prompt: str):
    """Generate text using a model"""
    
    if model_name not in AVAILABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    model_info = AVAILABLE_MODELS[model_name]
    
    # Simulate generation time based on model size
    generation_time = 100 + (model_info["parameters"] / 1000000) * 0.1 + random.uniform(-20, 20)
    
    # Generate mock response
    responses = [
        "This is a generated response from the model. The compression technique shows promising results for reducing model size while maintaining performance.",
        "The Tensor-Train decomposition method provides an effective way to compress large language models without significant quality loss.",
        "Compression ratios of 50% can be achieved with minimal impact on model performance, making this approach practical for deployment.",
        "The model successfully processes the input and generates coherent text output.",
        "This demonstrates the effectiveness of the compression algorithm on different model architectures.",
    ]
    
    response = random.choice(responses)
    
    return {
        "response": response,
        "model_used": model_name,
        "generation_time_ms": generation_time,
        "prompt": prompt,
    }

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time updates"""
    
    await websocket.accept()
    
    try:
        last_metric_index = 0
        
        while True:
            # Check if job exists
            if job_id not in active_jobs:
                await websocket.send_json({
                    "type": "error",
                    "error": f"Job {job_id} not found"
                })
                break
            
            # Send new metrics
            if job_id in job_metrics:
                metrics = job_metrics[job_id]
                if len(metrics) > last_metric_index:
                    for metric in metrics[last_metric_index:]:
                        await websocket.send_json({
                            "type": "metrics",
                            "data": metric
                        })
                    last_metric_index = len(metrics)
            
            # Check if job is completed
            if active_jobs[job_id]["status"] == "completed":
                await websocket.send_json({
                    "type": "status",
                    "status": "completed",
                    "job_id": job_id
                })
                break
            
            elif active_jobs[job_id]["status"] == "failed":
                await websocket.send_json({
                    "type": "error",
                    "error": active_jobs[job_id].get("error", "Unknown error")
                })
                break
            
            await asyncio.sleep(0.5)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": str(e)
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
