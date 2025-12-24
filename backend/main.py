import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

try:
    from backend.config import settings
    from backend.models import (
        CompressionRequest, CompressionResult, CompressionStatus,
        ChatRequest, ChatResponse, ModelInfo, ExportFormat, ExportRequest
    )
    from backend.websocket_manager import connection_manager
    from backend.compression_service import compression_service
    from backend.benchmark_service import benchmark_service
    from backend.export_service import export_service
except ImportError:
    # Try relative imports if absolute imports fail
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from backend.config import settings
    from backend.models import (
        CompressionRequest, CompressionResult, CompressionStatus,
        ChatRequest, ChatResponse, ModelInfo, ExportFormat, ExportRequest
    )
    from backend.websocket_manager import connection_manager
    from backend.compression_service import compression_service
    from backend.benchmark_service import benchmark_service
    from backend.export_service import export_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("Starting QCompress API server...")
    yield
    logger.info("Shutting down QCompress API server...")


app = FastAPI(
    title="QCompress API",
    description="API for quantum-inspired compression with Tensor-Train",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "QCompress API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/models", response_model=list[ModelInfo])
async def get_models():
    """Get list of available models"""
    models = [
        ModelInfo(
            name="distilgpt2",
            description="DistilGPT-2: smaller, faster version of GPT-2"
        ),
        ModelInfo(
            name="gpt2",
            description="GPT-2: Generative Pre-trained Transformer 2"
        ),
        ModelInfo(
            name="microsoft/DialoGPT-small",
            description="DialoGPT-small: Conversational AI model"
        ),
    ]
    return models


@app.post("/api/compress", response_model=CompressionResult)
async def start_compression(
    request: CompressionRequest,
    background_tasks: BackgroundTasks
):
    """Start a compression job"""
    try:
        job_id = compression_service.create_job(
            request.model_name,
            request.compression_configs
        )
        
        # Run compression in background
        background_tasks.add_task(
            compression_service.run_compression,
            job_id
        )
        
        # Return initial result
        return CompressionResult(
            job_id=job_id,
            status=CompressionStatus.PENDING,
            original_params=0,
            compressed_params=0,
            compression_ratio=0.0,
            original_size_mb=0.0,
            compressed_size_mb=0.0
        )
    except Exception as e:
        logger.error(f"Error starting compression: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{job_id}", response_model=dict)
async def get_job_status(job_id: str):
    """Get compression job status"""
    job = compression_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job.get("result"),
        "error": job.get("error")
    }


@app.get("/api/results/{job_id}", response_model=CompressionResult)
async def get_job_results(job_id: str):
    """Get compression job results"""
    result = compression_service.get_job_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Results for job {job_id} not found")
    return result


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate chat response"""
    try:
        # This is a simplified version - full implementation would load models
        # For now, return a placeholder
        return ChatResponse(
            response="Chat functionality will be implemented with model loading",
            generation_time=0.0,
            model_type="original" if not request.use_compressed else "compressed"
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/compression/{job_id}")
async def websocket_compression(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for compression monitoring"""
    await connection_manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await connection_manager.send_personal_message(
                {"type": "pong", "data": data},
                websocket
            )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for job {job_id}")


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for chat streaming"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Placeholder for chat streaming
            await websocket.send_json({
                "type": "chunk",
                "token": "Chat streaming will be implemented",
                "finished": True
            })
    except WebSocketDisconnect:
        logger.info("Chat WebSocket disconnected")


@app.post("/api/benchmark/{job_id}")
async def start_benchmark(job_id: str, background_tasks: BackgroundTasks):
    """Start benchmark evaluation for a compressed model"""
    try:
        # Get compression job result
        compression_result = compression_service.get_job_result(job_id)
        if not compression_result:
            raise HTTPException(status_code=404, detail=f"Compression job {job_id} not found or not completed")
        
        if compression_result.status != CompressionStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=f"Compression job {job_id} is not completed yet")
        
        # Get the compressed model from the job
        job = compression_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Load model and tokenizer (from cache if available)
        model_name = job.get("model_name", "gpt2")
        model, tokenizer, device = await compression_service._load_model(model_name)
        
        # Create benchmark job
        benchmark_id = benchmark_service.create_benchmark_job(
            job_id=job_id,
            model=model,
            tokenizer=tokenizer,
            tasks=['wikitext', 'hellaswag', 'arc', 'mmlu']
        )
        
        # Run benchmark in background
        background_tasks.add_task(
            benchmark_service.run_benchmark,
            benchmark_id
        )
        
        return {
            "benchmark_id": benchmark_id,
            "job_id": job_id,
            "status": "pending",
            "message": "Benchmark evaluation started"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting benchmark: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/benchmark/{job_id}/results")
async def get_benchmark_results(job_id: str):
    """Get benchmark results for a compression job"""
    try:
        # Find benchmark job by compression job_id
        benchmark_job = None
        for bid, job in benchmark_service.benchmark_jobs.items():
            if job.get("job_id") == job_id:
                benchmark_job = job
                break
        
        if not benchmark_job:
            raise HTTPException(status_code=404, detail=f"Benchmark results for job {job_id} not found")
        
        result = benchmark_service.get_benchmark_result(benchmark_job["benchmark_id"])
        if not result:
            return {
                "job_id": job_id,
                "status": benchmark_job.get("status", "pending"),
                "message": "Benchmark still running or not started"
            }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting benchmark results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/export/pytorch")
async def export_model_pytorch(job_id: str):
    """Export compressed model to PyTorch format"""
    try:
        job = compression_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.get("status") != CompressionStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=f"Job {job_id} is not completed yet")
        
        compressed_model = job.get("compressed_model")
        if not compressed_model:
            raise HTTPException(status_code=404, detail=f"Compressed model for job {job_id} not found")
        
        result = job.get("result")
        metadata = export_service.get_export_metadata(job_id, {
            "compression_ratio": result.compression_ratio if result else 0,
            "original_params": result.original_params if result else 0,
            "compressed_params": result.compressed_params if result else 0,
            "original_size_mb": result.original_size_mb if result else 0,
            "compressed_size_mb": result.compressed_size_mb if result else 0,
            "model_name": job.get("model_name", "unknown"),
        })
        
        export_path = export_service.export_to_pytorch(compressed_model, job_id, metadata)
        
        return FileResponse(
            export_path,
            media_type="application/octet-stream",
            filename=f"{job_id}_model.pt"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting to PyTorch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/export/safetensors")
async def export_model_safetensors(job_id: str):
    """Export compressed model to SafeTensors format"""
    try:
        job = compression_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.get("status") != CompressionStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=f"Job {job_id} is not completed yet")
        
        compressed_model = job.get("compressed_model")
        if not compressed_model:
            raise HTTPException(status_code=404, detail=f"Compressed model for job {job_id} not found")
        
        result = job.get("result")
        metadata = export_service.get_export_metadata(job_id, {
            "compression_ratio": result.compression_ratio if result else 0,
            "original_params": result.original_params if result else 0,
            "compressed_params": result.compressed_params if result else 0,
            "original_size_mb": result.original_size_mb if result else 0,
            "compressed_size_mb": result.compressed_size_mb if result else 0,
            "model_name": job.get("model_name", "unknown"),
        })
        
        export_path = export_service.export_to_safetensors(compressed_model, job_id, metadata)
        
        return FileResponse(
            export_path,
            media_type="application/octet-stream",
            filename=f"{job_id}_model.safetensors"
        )
    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(status_code=400, detail=f"SafeTensors export requires safetensors package: {str(e)}")
    except Exception as e:
        logger.error(f"Error exporting to SafeTensors: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/export/onnx")
async def export_model_onnx(job_id: str):
    """Export compressed model to ONNX format"""
    try:
        job = compression_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if job.get("status") != CompressionStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=f"Job {job_id} is not completed yet")
        
        compressed_model = job.get("compressed_model")
        if not compressed_model:
            raise HTTPException(status_code=404, detail=f"Compressed model for job {job_id} not found")
        
        result = job.get("result")
        metadata = export_service.get_export_metadata(job_id, {
            "compression_ratio": result.compression_ratio if result else 0,
            "original_params": result.original_params if result else 0,
            "compressed_params": result.compressed_params if result else 0,
            "original_size_mb": result.original_size_mb if result else 0,
            "compressed_size_mb": result.compressed_size_mb if result else 0,
            "model_name": job.get("model_name", "unknown"),
        })
        
        export_path = export_service.export_to_onnx(compressed_model, job_id, metadata=metadata)
        
        return FileResponse(
            export_path,
            media_type="application/octet-stream",
            filename=f"{job_id}_model.onnx"
        )
    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(status_code=400, detail=f"ONNX export requires onnx package: {str(e)}")
    except Exception as e:
        logger.error(f"Error exporting to ONNX: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}/export/metadata")
async def get_export_metadata(job_id: str):
    """Get export metadata for a compression job"""
    try:
        job = compression_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        result = job.get("result")
        if not result:
            raise HTTPException(status_code=404, detail=f"Result for job {job_id} not found")
        
        metadata = export_service.get_export_metadata(job_id, {
            "compression_ratio": result.compression_ratio,
            "original_params": result.original_params,
            "compressed_params": result.compressed_params,
            "original_size_mb": result.original_size_mb,
            "compressed_size_mb": result.compressed_size_mb,
            "model_name": job.get("model_name", "unknown"),
        })
        
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting export metadata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )

