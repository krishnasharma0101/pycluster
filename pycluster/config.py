"""
Configuration settings for PyCluster
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Configuration class for PyCluster settings"""
    
    # Network settings
    DEFAULT_HOST_PORT: int = 8888
    DEFAULT_WORKER_PORT: int = 8889
    HOST_ADDRESS: str = "0.0.0.0"
    
    # Security settings
    KEY_SIZE: int = 32  # bytes for Fernet key
    OTP_LENGTH: int = 8  # characters for one-time password
    
    # File transfer settings
    CHUNK_SIZE: int = 8192  # bytes per chunk
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB max file size
    
    # Timeout settings
    CONNECTION_TIMEOUT: float = 30.0  # seconds
    TASK_TIMEOUT: float = 300.0  # seconds
    HEARTBEAT_INTERVAL: float = 10.0  # seconds
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Worker settings
    MAX_WORKERS: int = 10
    WORKER_IDLE_TIMEOUT: float = 300.0  # seconds
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables"""
        return cls(
            DEFAULT_HOST_PORT=int(os.getenv("PYCLUSTER_HOST_PORT", cls.DEFAULT_HOST_PORT)),
            DEFAULT_WORKER_PORT=int(os.getenv("PYCLUSTER_WORKER_PORT", cls.DEFAULT_WORKER_PORT)),
            HOST_ADDRESS=os.getenv("PYCLUSTER_HOST_ADDRESS", cls.HOST_ADDRESS),
            KEY_SIZE=int(os.getenv("PYCLUSTER_KEY_SIZE", cls.KEY_SIZE)),
            OTP_LENGTH=int(os.getenv("PYCLUSTER_OTP_LENGTH", cls.OTP_LENGTH)),
            CHUNK_SIZE=int(os.getenv("PYCLUSTER_CHUNK_SIZE", cls.CHUNK_SIZE)),
            MAX_FILE_SIZE=int(os.getenv("PYCLUSTER_MAX_FILE_SIZE", cls.MAX_FILE_SIZE)),
            CONNECTION_TIMEOUT=float(os.getenv("PYCLUSTER_CONNECTION_TIMEOUT", cls.CONNECTION_TIMEOUT)),
            TASK_TIMEOUT=float(os.getenv("PYCLUSTER_TASK_TIMEOUT", cls.TASK_TIMEOUT)),
            HEARTBEAT_INTERVAL=float(os.getenv("PYCLUSTER_HEARTBEAT_INTERVAL", cls.HEARTBEAT_INTERVAL)),
            LOG_LEVEL=os.getenv("PYCLUSTER_LOG_LEVEL", cls.LOG_LEVEL),
            MAX_WORKERS=int(os.getenv("PYCLUSTER_MAX_WORKERS", cls.MAX_WORKERS)),
            WORKER_IDLE_TIMEOUT=float(os.getenv("PYCLUSTER_WORKER_IDLE_TIMEOUT", cls.WORKER_IDLE_TIMEOUT)),
        )

# Global config instance
config = Config.from_env() 