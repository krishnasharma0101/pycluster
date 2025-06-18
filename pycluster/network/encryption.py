"""
Encryption utilities for PyCluster
"""

import base64
import secrets
import string
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionManager:
    """Manages encryption and decryption of messages"""
    
    def __init__(self, key: Optional[bytes] = None):
        """Initialize encryption manager with optional key"""
        if key is None:
            key = Fernet.generate_key()
        self.key = key
        self.cipher = Fernet(key)
    
    @classmethod
    def from_password(cls, password: str, salt: Optional[bytes] = None) -> "EncryptionManager":
        """Create encryption manager from password"""
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return cls(key)
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data"""
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data)
    
    def get_key(self) -> bytes:
        """Get the encryption key"""
        return self.key
    
    @staticmethod
    def generate_otp(length: int = 8) -> str:
        """Generate a one-time password"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key"""
        return Fernet.generate_key() 