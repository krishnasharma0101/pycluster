"""
File transfer utilities for PyCluster
"""

import os
import asyncio
import aiofiles
from typing import Optional, Callable
from .socket_manager import SocketManager

class FileTransfer:
    """Handles file transfers with progress tracking"""
    
    def __init__(self, socket_manager: SocketManager):
        """Initialize file transfer manager"""
        self.socket_manager = socket_manager
    
    async def send_file_with_progress(
        self, 
        file_path: str, 
        chunk_size: int = 8192,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """Send a file with progress tracking"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = os.path.getsize(file_path)
        sent_bytes = 0
        
        # Send file info
        await self.socket_manager.send_message({
            "type": "file_transfer_start",
            "filename": os.path.basename(file_path),
            "size": file_size
        })
        
        # Send file in chunks with progress
        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                
                encrypted_chunk = self.socket_manager.encryption_manager.encrypt(chunk)
                length = len(encrypted_chunk).to_bytes(4, 'big')
                
                self.socket_manager.writer.write(length + encrypted_chunk)
                await self.socket_manager.writer.drain()
                
                sent_bytes += len(chunk)
                if progress_callback:
                    progress_callback(sent_bytes, file_size)
        
        # Send end marker
        await self.socket_manager.send_message({"type": "file_transfer_end"})
    
    async def receive_file_with_progress(
        self, 
        save_path: str, 
        chunk_size: int = 8192,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """Receive a file with progress tracking"""
        # Receive file info
        file_info = await self.socket_manager.receive_message()
        if file_info["type"] != "file_transfer_start":
            raise ValueError("Expected file transfer start message")
        
        file_size = file_info["size"]
        received_bytes = 0
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Receive file in chunks with progress
        async with aiofiles.open(save_path, 'wb') as f:
            while received_bytes < file_size:
                # Read chunk length
                length_data = await self.socket_manager.reader.readexactly(4)
                length = int.from_bytes(length_data, 'big')
                
                # Read encrypted chunk
                encrypted_chunk = await self.socket_manager.reader.readexactly(length)
                chunk = self.socket_manager.encryption_manager.decrypt(encrypted_chunk)
                
                await f.write(chunk)
                received_bytes += len(chunk)
                
                if progress_callback:
                    progress_callback(received_bytes, file_size)
        
        # Receive end marker
        end_msg = await self.socket_manager.receive_message()
        if end_msg["type"] != "file_transfer_end":
            raise ValueError("Expected file transfer end message")
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    @staticmethod
    def default_progress_callback(sent: int, total: int) -> None:
        """Default progress callback that prints progress"""
        percentage = (sent / total) * 100 if total > 0 else 0
        print(f"\rProgress: {percentage:.1f}% ({FileTransfer.format_size(sent)}/{FileTransfer.format_size(total)})", end="")
        if sent >= total:
            print()  # New line when complete 