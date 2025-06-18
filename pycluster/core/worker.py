"""
Worker system for PyCluster
"""

import asyncio
import logging
import socket
import cloudpickle
import time
import os
from typing import Optional, Any, Callable
from ..network import SocketManager, EncryptionManager
from ..config import config

class Worker:
    """Worker that connects to host and executes tasks"""
    
    def __init__(self, worker_id: str, host: str, port: int, otp: str, encryption_key: Optional[bytes] = None):
        """Initialize the worker"""
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.otp = otp
        self.encryption_manager = EncryptionManager(encryption_key)
        self.socket_manager = SocketManager(self.encryption_manager)
        self.is_connected = False
        self.is_running = False
        self.hostname = socket.gethostname()
        
        # Setup logging
        self.logger = logging.getLogger(f"pycluster.worker.{worker_id}")
        self.logger.setLevel(config.LOG_LEVEL)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(config.LOG_FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def connect(self) -> bool:
        """Connect to the host"""
        try:
            await self.socket_manager.connect(self.host, self.port)
            
            # Send authentication
            await self.socket_manager.send_message({
                "type": "auth",
                "otp": self.otp,
                "worker_id": self.worker_id,
                "hostname": self.hostname
            })
            
            # Wait for authentication response
            auth_response = await self.socket_manager.receive_message()
            if not auth_response.get("success"):
                self.logger.error(f"Authentication failed: {auth_response.get('message')}")
                return False
            
            # Update encryption key if provided by host
            if "encryption_key" in auth_response:
                host_key = bytes.fromhex(auth_response["encryption_key"])
                self.encryption_manager = EncryptionManager(host_key)
                self.socket_manager.encryption_manager = self.encryption_manager
                self.logger.info("Updated encryption key from host")
            
            self.is_connected = True
            self.logger.info(f"Connected to host {self.host}:{self.port}")
            
            # Start heartbeat and message handling
            asyncio.create_task(self._heartbeat_loop())
            asyncio.create_task(self._message_handler())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to host: {e}")
            return False
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to host"""
        while self.is_connected and self.is_running:
            try:
                await self.socket_manager.send_message({
                    "type": "heartbeat",
                    "worker_id": self.worker_id
                })
                await asyncio.sleep(config.HEARTBEAT_INTERVAL)
            except Exception as e:
                self.logger.error(f"Heartbeat failed: {e}")
                break
        
        self.is_connected = False
    
    async def _message_handler(self) -> None:
        """Handle messages from host"""
        try:
            while self.is_connected and self.is_running:
                message = await self.socket_manager.receive_message()
                
                if message["type"] == "execute_task":
                    await self._execute_task(message)
                
                elif message["type"] == "heartbeat_response":
                    # Heartbeat acknowledged
                    pass
                
                elif message["type"] == "disconnect":
                    break
                    
        except Exception as e:
            self.logger.error(f"Error handling messages: {e}")
        finally:
            self.is_connected = False
    
    async def _execute_task(self, message: dict) -> None:
        """Execute a task received from host"""
        task_id = message["task_id"]
        serialized_func = message["func"]
        serialized_args = message["args"]
        serialized_kwargs = message["kwargs"]
        
        try:
            # Deserialize function and arguments
            func = cloudpickle.loads(serialized_func)
            args = cloudpickle.loads(serialized_args)
            kwargs = cloudpickle.loads(serialized_kwargs)
            
            self.logger.info(f"Executing task {task_id}")
            
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Run in thread pool for blocking functions
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, func, *args, **kwargs)
            
            # Send result back to host
            await self.socket_manager.send_message({
                "type": "task_result",
                "task_id": task_id,
                "result": result,
                "success": True
            })
            
            self.logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Task {task_id} failed: {e}")
            
            # Send error back to host
            await self.socket_manager.send_message({
                "type": "task_result",
                "task_id": task_id,
                "result": str(e),
                "success": False
            })
    
    async def start(self) -> None:
        """Start the worker"""
        self.is_running = True
        
        if not await self.connect():
            raise ConnectionError("Failed to connect to host")
        
        self.logger.info(f"Worker {self.worker_id} started")
        
        # Keep running until disconnected
        while self.is_connected and self.is_running:
            await asyncio.sleep(1)
    
    async def stop(self) -> None:
        """Stop the worker"""
        self.is_running = False
        
        if self.is_connected:
            try:
                await self.socket_manager.send_message({
                    "type": "disconnect",
                    "worker_id": self.worker_id
                })
            except:
                pass
            
            self.socket_manager.close()
            await self.socket_manager.wait_closed()
        
        self.logger.info(f"Worker {self.worker_id} stopped")
    
    def get_status(self) -> dict:
        """Get worker status"""
        return {
            "worker_id": self.worker_id,
            "hostname": self.hostname,
            "is_connected": self.is_connected,
            "is_running": self.is_running,
            "host": self.host,
            "port": self.port
        } 