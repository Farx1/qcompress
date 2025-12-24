from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CompressionStatus(str, Enum):
    """Compression job status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelInfo(BaseModel):
    """Model information"""
    name: str
    size_mb: Optional[float] = None
    parameters: Optional[int] = None
    description: Optional[str] = None


class CompressionConfig(BaseModel):
    """Compression configuration"""
    model_name: str
    compression_configs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dictionary mapping layer names to compression configs"
    )


class CompressionRequest(BaseModel):
    """Request to start compression"""
    model_name: str = Field(..., description="HuggingFace model name")
    compression_configs: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Compression configurations per layer"
    )


class CompressionResult(BaseModel):
    """Compression result"""
    job_id: str
    status: CompressionStatus
    original_params: int
    compressed_params: int
    compression_ratio: float
    original_size_mb: float
    compressed_size_mb: float
    error: Optional[str] = None


class CompressionMetrics(BaseModel):
    """Real-time compression metrics"""
    job_id: str
    step: int
    loss: Optional[float] = None
    compression_ratio: Optional[float] = None
    parameters: Optional[int] = None
    timestamp: float


class ChatRequest(BaseModel):
    """Chat generation request"""
    prompt: str
    model_name: Optional[str] = None
    use_compressed: bool = False
    max_length: int = 100
    temperature: float = 0.7


class ChatResponse(BaseModel):
    """Chat generation response"""
    response: str
    generation_time: float
    model_type: str


class ChatStreamChunk(BaseModel):
    """Streaming chat chunk"""
    token: str
    finished: bool = False


class ExportFormat(str, Enum):
    """Export format options"""
    PYTORCH = "pytorch"
    SAFETENSORS = "safetensors"
    ONNX = "onnx"


class ExportRequest(BaseModel):
    """Request to export a model"""
    job_id: str
    format: ExportFormat
    include_metadata: bool = True


class ExportMetadata(BaseModel):
    """Export metadata"""
    job_id: str
    format: ExportFormat
    file_path: str
    file_size_mb: float
    compression_ratio: float
    original_params: int
    compressed_params: int
    model_name: str
    exported_at: str

