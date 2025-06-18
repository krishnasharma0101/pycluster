"""
Helper utility functions for PyCluster
"""

import socket
import uuid
import os
import random
import string
from typing import Optional

def get_local_ip() -> str:
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

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

def generate_worker_id() -> str:
    """Generate a unique worker ID"""
    hostname = socket.gethostname()
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{hostname}-{unique_suffix}"

def generate_otp(length: int = 8) -> str:
    """Generate a one-time password"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def ensure_directory(path: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    os.makedirs(path, exist_ok=True)

def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

def find_available_port(start_port: int = 8888, max_attempts: int = 100) -> Optional[int]:
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    return None 