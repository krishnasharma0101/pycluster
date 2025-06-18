"""
Async socket communication manager for PyCluster
"""

import asyncio
import json
import struct
import base64
from typing import Optional, Dict, Any, Callable
from .encryption import EncryptionManager

class SocketManager:
    """Manages encrypted async socket communication"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        """Initialize socket manager with encryption"""
        self.encryption_manager = encryption_manager
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
    
    async def connect(self, host: str, port: int) -> None:
        """Connect to a remote host"""
        self.reader, self.writer = await asyncio.open_connection(host, port)
    
    async def accept_connection(self, server: asyncio.Server) -> tuple:
        """Accept a connection from a client"""
        self.reader, self.writer = await server.accept()
        return self.reader, self.writer
    
    def _encode_message(self, message: Dict[str, Any]) -> str:
        """Encode message for JSON serialization, handling binary data"""
        def encode_binary(obj):
            if isinstance(obj, bytes):
                return {"__binary__": base64.b64encode(obj).decode('utf-8')}
            elif isinstance(obj, dict):
                return {k: encode_binary(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [encode_binary(item) for item in obj]
            else:
                return obj
        
        encoded_message = encode_binary(message)
        return json.dumps(encoded_message)
    
    def _decode_message(self, data: str) -> Dict[str, Any]:
        """Decode message from JSON, handling binary data"""
        def decode_binary(obj):
            if isinstance(obj, dict):
                if "__binary__" in obj:
                    return base64.b64decode(obj["__binary__"].encode('utf-8'))
                else:
                    return {k: decode_binary(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decode_binary(item) for item in obj]
            else:
                return obj
        
        decoded_data = json.loads(data)
        return decode_binary(decoded_data)
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send an encrypted message"""
        if not self.writer:
            raise ConnectionError("Not connected")
        
        # Serialize and encrypt message
        data = self._encode_message(message).encode('utf-8')
        encrypted_data = self.encryption_manager.encrypt(data)
        
        # Send length prefix and data
        length = struct.pack('!I', len(encrypted_data))
        self.writer.write(length + encrypted_data)
        await self.writer.drain()
    
    async def receive_message(self) -> Dict[str, Any]:
        """Receive and decrypt a message"""
        if not self.reader:
            raise ConnectionError("Not connected")
        
        # Read length prefix
        length_data = await self.reader.readexactly(4)
        length = struct.unpack('!I', length_data)[0]
        
        # Read encrypted data
        encrypted_data = await self.reader.readexactly(length)
        
        # Decrypt and deserialize
        data = self.encryption_manager.decrypt(encrypted_data)
        return self._decode_message(data.decode('utf-8'))
    
    async def send_file(self, file_path: str, chunk_size: int = 8192) -> None:
        """Send a file in chunks"""
        if not self.writer:
            raise ConnectionError("Not connected")
        
        import os
        file_size = os.path.getsize(file_path)
        
        # Send file info
        await self.send_message({
            "type": "file_transfer_start",
            "filename": os.path.basename(file_path),
            "size": file_size
        })
        
        # Send file in chunks
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                encrypted_chunk = self.encryption_manager.encrypt(chunk)
                length = struct.pack('!I', len(encrypted_chunk))
                self.writer.write(length + encrypted_chunk)
                await self.writer.drain()
        
        # Send end marker
        await self.send_message({"type": "file_transfer_end"})
    
    async def receive_file(self, save_path: str, chunk_size: int = 8192) -> None:
        """Receive a file in chunks"""
        if not self.reader:
            raise ConnectionError("Not connected")
        
        # Receive file info
        file_info = await self.receive_message()
        if file_info["type"] != "file_transfer_start":
            raise ValueError("Expected file transfer start message")
        
        # Receive file in chunks
        with open(save_path, 'wb') as f:
            while True:
                # Read chunk length
                length_data = await self.reader.readexactly(4)
                length = struct.unpack('!I', length_data)[0]
                
                # Read encrypted chunk
                encrypted_chunk = await self.reader.readexactly(length)
                chunk = self.encryption_manager.decrypt(encrypted_chunk)
                f.write(chunk)
        
        # Receive end marker
        end_msg = await self.receive_message()
        if end_msg["type"] != "file_transfer_end":
            raise ValueError("Expected file transfer end message")
    
    def close(self) -> None:
        """Close the connection"""
        if self.writer:
            self.writer.close()
    
    async def wait_closed(self) -> None:
        """Wait for the connection to close"""
        if self.writer:
            await self.writer.wait_closed() 