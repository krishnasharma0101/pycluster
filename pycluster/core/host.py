"""
Host/dispatcher system for PyCluster
"""

import asyncio
import logging
import socket
import cloudpickle
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from ..network import SocketManager, EncryptionManager
from ..config import config

@dataclass
class WorkerInfo:
    """Information about a connected worker"""
    id: str
    hostname: str
    socket_manager: SocketManager
    last_heartbeat: float
    is_active: bool = True
    current_task: Optional[str] = None

class Host:
    """Central dispatcher that manages workers and distributes tasks"""
    
    def __init__(self, port: int = None, encryption_key: Optional[bytes] = None):
        """Initialize the host dispatcher"""
        self.port = port or config.DEFAULT_HOST_PORT
        self.encryption_manager = EncryptionManager(encryption_key)
        self.workers: Dict[str, WorkerInfo] = {}
        self.server: Optional[asyncio.Server] = None
        self.is_running = False
        self.otp = EncryptionManager.generate_otp(config.OTP_LENGTH)
        
        # Setup logging
        self.logger = logging.getLogger("pycluster.host")
        self.logger.setLevel(config.LOG_LEVEL)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(config.LOG_FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def start(self) -> None:
        """Start the host server"""
        self.server = await asyncio.start_server(
            self._handle_worker_connection,
            config.HOST_ADDRESS,
            self.port
        )
        
        self.is_running = True
        self.logger.info(f"Host started on {config.HOST_ADDRESS}:{self.port}")
        self.logger.info(f"One-time password: {self.otp}")
        
        # Start heartbeat monitoring
        asyncio.create_task(self._heartbeat_monitor())
        
        async with self.server:
            await self.server.serve_forever()
    
    async def _handle_worker_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming worker connections"""
        try:
            # Create socket manager for this connection
            socket_manager = SocketManager(self.encryption_manager)
            socket_manager.reader = reader
            socket_manager.writer = writer
            
            self.logger.info("Worker attempting to connect...")
            
            # Wait for authentication
            try:
                auth_msg = await socket_manager.receive_message()
                self.logger.info(f"Received auth message: {auth_msg}")
                
                if auth_msg["type"] != "auth":
                    raise ValueError(f"Expected authentication message, got {auth_msg['type']}")
                
                otp = auth_msg.get("otp")
                worker_id = auth_msg.get("worker_id")
                hostname = auth_msg.get("hostname", "unknown")
                
                self.logger.info(f"Worker {worker_id} ({hostname}) attempting auth with OTP: {otp}")
                
                if otp != self.otp:
                    self.logger.warning(f"Invalid OTP from {worker_id}: {otp} != {self.otp}")
                    await socket_manager.send_message({
                        "type": "auth_response",
                        "success": False,
                        "message": "Invalid OTP"
                    })
                    return
                
                # Accept worker
                await socket_manager.send_message({
                    "type": "auth_response",
                    "success": True,
                    "message": "Authentication successful",
                    "encryption_key": self.encryption_manager.get_key().hex()
                })
                
                # Register worker
                worker_info = WorkerInfo(
                    id=worker_id,
                    hostname=hostname,
                    socket_manager=socket_manager,
                    last_heartbeat=time.time()
                )
                self.workers[worker_id] = worker_info
                
                self.logger.info(f"Worker connected: {worker_id} ({hostname})")
                
                # Handle worker messages
                await self._handle_worker_messages(worker_info)
                
            except Exception as auth_error:
                self.logger.error(f"Authentication error: {auth_error}")
                # Try to send error response
                try:
                    await socket_manager.send_message({
                        "type": "auth_response",
                        "success": False,
                        "message": f"Authentication failed: {auth_error}"
                    })
                except:
                    pass
                raise
            
        except Exception as e:
            self.logger.error(f"Error handling worker connection: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _handle_worker_messages(self, worker_info: WorkerInfo) -> None:
        """Handle messages from a specific worker"""
        try:
            while worker_info.is_active:
                message = await worker_info.socket_manager.receive_message()
                
                if message["type"] == "heartbeat":
                    worker_info.last_heartbeat = time.time()
                    await worker_info.socket_manager.send_message({
                        "type": "heartbeat_response"
                    })
                
                elif message["type"] == "task_result":
                    # Handle task completion
                    task_id = message["task_id"]
                    result = message["result"]
                    success = message["success"]
                    
                    if success:
                        self.logger.info(f"Task {task_id} completed successfully on {worker_info.id}")
                        # Set the result in the future
                        if hasattr(self, '_task_results') and task_id in self._task_results:
                            future = self._task_results[task_id]
                            if not future.done():
                                future.set_result(result)
                    else:
                        self.logger.error(f"Task {task_id} failed on {worker_info.id}: {result}")
                        # Set the exception in the future
                        if hasattr(self, '_task_results') and task_id in self._task_results:
                            future = self._task_results[task_id]
                            if not future.done():
                                future.set_exception(RuntimeError(f"Task failed: {result}"))
                    
                    worker_info.current_task = None
                
                elif message["type"] == "disconnect":
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling messages from {worker_info.id}: {e}")
        finally:
            # Remove worker
            if worker_info.id in self.workers:
                del self.workers[worker_info.id]
                self.logger.info(f"Worker disconnected: {worker_info.id}")
    
    async def _heartbeat_monitor(self) -> None:
        """Monitor worker heartbeats and mark inactive workers"""
        while self.is_running:
            current_time = time.time()
            inactive_workers = []
            
            for worker_id, worker_info in self.workers.items():
                if current_time - worker_info.last_heartbeat > config.HEARTBEAT_INTERVAL * 2:
                    worker_info.is_active = False
                    inactive_workers.append(worker_id)
            
            for worker_id in inactive_workers:
                if worker_id in self.workers:
                    del self.workers[worker_id]
                    self.logger.warning(f"Worker {worker_id} marked as inactive")
            
            await asyncio.sleep(config.HEARTBEAT_INTERVAL)
    
    async def execute_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict, target_worker: Optional[str] = None) -> Any:
        """Execute a task on a worker"""
        # Find available worker
        if target_worker:
            if target_worker not in self.workers:
                raise ValueError(f"Target worker {target_worker} not found")
            worker_info = self.workers[target_worker]
        else:
            # Find worker with no current task
            available_workers = [w for w in self.workers.values() if w.current_task is None and w.is_active]
            if not available_workers:
                raise RuntimeError("No available workers")
            worker_info = available_workers[0]
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Store the future for this task
        if not hasattr(self, '_task_results'):
            self._task_results = {}
        self._task_results[task_id] = result_future
        
        # Serialize function and arguments
        serialized_func = cloudpickle.dumps(func)
        serialized_args = cloudpickle.dumps(args)
        serialized_kwargs = cloudpickle.dumps(kwargs)
        
        # Send task to worker
        worker_info.current_task = task_id
        await worker_info.socket_manager.send_message({
            "type": "execute_task",
            "task_id": task_id,
            "func": serialized_func,
            "args": serialized_args,
            "kwargs": serialized_kwargs
        })
        
        self.logger.info(f"Task {task_id} sent to worker {worker_info.id}")
        
        # Wait for result with timeout
        try:
            result = await asyncio.wait_for(result_future, timeout=config.TASK_TIMEOUT)
            return result
        except asyncio.TimeoutError:
            raise RuntimeError(f"Task {task_id} timed out after {config.TASK_TIMEOUT} seconds")
        finally:
            # Clean up
            if task_id in self._task_results:
                del self._task_results[task_id]
            worker_info.current_task = None
    
    def get_workers_info(self) -> List[Dict[str, Any]]:
        """Get information about all connected workers"""
        workers_info = []
        for worker_id, worker_info in self.workers.items():
            workers_info.append({
                "id": worker_id,
                "hostname": worker_info.hostname,
                "is_active": worker_info.is_active,
                "current_task": worker_info.current_task,
                "last_heartbeat": worker_info.last_heartbeat
            })
        return workers_info
    
    def get_otp(self) -> str:
        """Get the current one-time password"""
        return self.otp
    
    def generate_new_otp(self) -> str:
        """Generate a new one-time password"""
        self.otp = EncryptionManager.generate_otp(config.OTP_LENGTH)
        self.logger.info(f"New OTP generated: {self.otp}")
        return self.otp
    
    async def stop(self) -> None:
        """Stop the host server"""
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.logger.info("Host stopped") 