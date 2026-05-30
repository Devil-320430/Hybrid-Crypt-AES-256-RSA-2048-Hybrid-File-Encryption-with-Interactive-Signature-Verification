"""
RSA Asymmetric Encryption and Key Management Module

This module provides secure RSA encryption for protecting AES keys
and key pair generation and management.
"""

import os
from typing import Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class AsymmetricCrypto:
    """
    Handles RSA asymmetric encryption for secure key distribution.
    
    Uses:
    - RSA-2048 for key encryption (can be upgraded to RSA-4096)
    - OAEP padding with SHA-256
    - PKCS8 for private key serialization
    """
    
    KEY_SIZE = 2048  # RSA key size in bits (can upgrade to 4096)
    PUBLIC_EXPONENT = 65537
    
    @staticmethod
    def generate_key_pair() -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair.
        
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=AsymmetricCrypto.PUBLIC_EXPONENT,
            key_size=AsymmetricCrypto.KEY_SIZE,
            backend=default_backend()
        )
        
        # Serialize private key (encrypted with password is recommended)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def encrypt_aes_key(aes_key: bytes, public_key_pem: bytes) -> bytes:
        """
        Encrypt AES key using RSA public key.
        
        Args:
            aes_key: The AES-256 key to encrypt (32 bytes)
            public_key_pem: RSA public key in PEM format
            
        Returns:
            Encrypted AES key
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return encrypted_key
    
    @staticmethod
    def decrypt_aes_key(encrypted_aes_key: bytes, private_key_pem: bytes) -> bytes:
        """
        Decrypt AES key using RSA private key.
        
        Args:
            encrypted_aes_key: The encrypted AES key
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Decrypted AES key
            
        Raises:
            ValueError: If decryption fails
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        try:
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return aes_key
        except Exception as e:
            raise ValueError(f"Failed to decrypt AES key: {str(e)}")
    
    @staticmethod
    def save_private_key(private_key_pem: bytes, file_path: str, mode: int = 0o600):
        """
        Save private key to file with restricted permissions.
        
        Args:
            private_key_pem: Private key in PEM format
            file_path: Destination file path
            mode: File permissions (default: 0o600 - read/write for owner only)
        """
        with open(file_path, 'wb') as f:
            f.write(private_key_pem)
        os.chmod(file_path, mode)
    
    @staticmethod
    def load_private_key(file_path: str) -> bytes:
        """
        Load private key from file.
        
        Args:
            file_path: Path to private key file
            
        Returns:
            Private key in PEM format
        """
        with open(file_path, 'rb') as f:
            return f.read()
    
    @staticmethod
    def save_public_key(public_key_pem: bytes, file_path: str):
        """
        Save public key to file.
        
        Args:
            public_key_pem: Public key in PEM format
            file_path: Destination file path
        """
        with open(file_path, 'wb') as f:
            f.write(public_key_pem)
    
    @staticmethod
    def load_public_key(file_path: str) -> bytes:
        """
        Load public key from file.
        
        Args:
            file_path: Path to public key file
            
        Returns:
            Public key in PEM format
        """
        with open(file_path, 'rb') as f:
            return f.read()
