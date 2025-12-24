from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Map job_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map WebSocket -> job_id
        self.connection_jobs: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept and register a WebSocket connection"""
        await websocket.accept()
        
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        
        self.active_connections[job_id].add(websocket)
        self.connection_jobs[websocket] = job_id
        logger.info(f"WebSocket connected for job {job_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_jobs:
            job_id = self.connection_jobs[websocket]
            if job_id in self.active_connections:
                self.active_connections[job_id].discard(websocket)
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
            del self.connection_jobs[websocket]
            logger.info(f"WebSocket disconnected for job {job_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_to_job(self, message: dict, job_id: str):
        """Broadcast a message to all connections for a job"""
        if job_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to job {job_id}: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_metrics(self, job_id: str, metrics: dict):
        """Broadcast compression metrics"""
        message = {
            "type": "metrics",
            "job_id": job_id,
            "data": metrics
        }
        await self.broadcast_to_job(message, job_id)
    
    async def broadcast_status(self, job_id: str, status: str, data: dict = None):
        """Broadcast job status update"""
        message = {
            "type": "status",
            "job_id": job_id,
            "status": status,
            "data": data or {}
        }
        await self.broadcast_to_job(message, job_id)
    
    async def broadcast_error(self, job_id: str, error: str):
        """Broadcast error message"""
        message = {
            "type": "error",
            "job_id": job_id,
            "error": error
        }
        await self.broadcast_to_job(message, job_id)
    
    async def broadcast_tt_core_data(self, job_id: str, core_data: dict):
        """Broadcast TT core data for 3D visualization"""
        message = {
            "type": "tt_core_data",
            "job_id": job_id,
            "data": core_data
        }
        await self.broadcast_to_job(message, job_id)
    
    async def broadcast_benchmark_result(self, job_id: str, result: dict):
        """Broadcast benchmark result"""
        message = {
            "type": "benchmark_result",
            "job_id": job_id,
            "data": result
        }
        await self.broadcast_to_job(message, job_id)


# Global connection manager instance
connection_manager = ConnectionManager()

