"""
Digital Signature Module

This module provides file signing and verification using RSA signatures
with SHA-256 hashing for authentication and non-repudiation.
"""

from typing import Tuple
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


class DigitalSignature:
    """
    Handles digital signatures for file authentication and non-repudiation.
    
    Uses:
    - RSA with PSS padding
    - SHA-256 hash algorithm
    - Provides sign and verify functionality
    """
    
    @staticmethod
    def sign_data(data: bytes, private_key_pem: bytes) -> bytes:
        """
        Sign data using RSA private key.
        
        Args:
            data: Data to sign
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Digital signature (bytes)
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    @staticmethod
    def verify_signature(data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
        """
        Verify digital signature.
        
        Args:
            data: Original data
            signature: Digital signature to verify
            public_key_pem: RSA public key in PEM format
            
        Returns:
            True if signature is valid, False otherwise
        """
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def sign_file(file_path: str, private_key_pem: bytes) -> bytes:
        """
        Sign a file.
        
        Args:
            file_path: Path to file to sign
            private_key_pem: RSA private key in PEM format
            
        Returns:
            Digital signature (bytes)
        """
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        return DigitalSignature.sign_data(file_data, private_key_pem)
    
    @staticmethod
    def verify_file_signature(file_path: str, signature: bytes, public_key_pem: bytes) -> bool:
        """
        Verify file signature.
        
        Args:
            file_path: Path to file to verify
            signature: Digital signature to verify
            public_key_pem: RSA public key in PEM format
            
        Returns:
            True if signature is valid, False otherwise
        """
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        return DigitalSignature.verify_signature(file_data, signature, public_key_pem)
