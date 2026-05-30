"""
AES-256 Encryption and Integrity Verification Module

This module provides secure file encryption using AES-256 in CBC mode
with PKCS7 padding and SHA-256 based HMAC for integrity verification.
"""

import os
import hashlib
import hmac
from typing import Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class SymmetricCrypto:
    """
    Handles AES-256 symmetric encryption and integrity verification.
    
    Uses:
    - AES-256-CBC for encryption
    - PBKDF2 for key derivation (if needed)
    - HMAC-SHA256 for integrity
    """
    
    ALGORITHM = algorithms.AES
    KEY_SIZE = 32  # 256-bit key
    IV_SIZE = 16   # 128-bit IV
    BLOCK_SIZE = 16  # 128-bit blocks
    HASH_ALGORITHM = hashlib.sha256
    
    @staticmethod
    def generate_random_key(key_size: int = KEY_SIZE) -> bytes:
        """Generate a random cryptographic key."""
        return os.urandom(key_size)
    
    @staticmethod
    def generate_random_iv(iv_size: int = IV_SIZE) -> bytes:
        """Generate a random initialization vector."""
        return os.urandom(iv_size)
    
    @staticmethod
    def pad_data(data: bytes) -> bytes:
        """Apply PKCS7 padding to data."""
        padding_len = SymmetricCrypto.BLOCK_SIZE - (len(data) % SymmetricCrypto.BLOCK_SIZE)
        padding = bytes([padding_len] * padding_len)
        return data + padding
    
    @staticmethod
    def unpad_data(data: bytes) -> bytes:
        """Remove PKCS7 padding from data."""
        padding_len = data[-1]
        if padding_len < 1 or padding_len > SymmetricCrypto.BLOCK_SIZE:
            raise ValueError("Invalid padding")
        if data[-padding_len:] != bytes([padding_len] * padding_len):
            raise ValueError("Padding verification failed")
        return data[:-padding_len]
    
    @staticmethod
    def compute_hmac(key: bytes, data: bytes) -> bytes:
        """Compute HMAC-SHA256 for integrity verification."""
        return hmac.new(key, data, SymmetricCrypto.HASH_ALGORITHM).digest()
    
    @staticmethod
    def verify_hmac(key: bytes, data: bytes, signature: bytes) -> bool:
        """Verify HMAC-SHA256 signature."""
        expected_signature = SymmetricCrypto.compute_hmac(key, data)
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def encrypt(key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt plaintext using AES-256-CBC.
        
        Args:
            key: 32-byte AES key
            plaintext: Data to encrypt
            
        Returns:
            Tuple of (IV, ciphertext, HMAC)
        """
        if len(key) != SymmetricCrypto.KEY_SIZE:
            raise ValueError(f"Key must be {SymmetricCrypto.KEY_SIZE} bytes")
        
        # Generate random IV
        iv = SymmetricCrypto.generate_random_iv()
        
        # Pad plaintext
        padded_plaintext = SymmetricCrypto.pad_data(plaintext)
        
        # Create cipher
        cipher = Cipher(
            SymmetricCrypto.ALGORITHM(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        
        # Compute HMAC over IV + ciphertext for authenticity
        data_to_sign = iv + ciphertext
        hmac_sig = SymmetricCrypto.compute_hmac(key, data_to_sign)
        
        return iv, ciphertext, hmac_sig
    
    @staticmethod
    def decrypt(key: bytes, iv: bytes, ciphertext: bytes, hmac_sig: bytes) -> bytes:
        """
        Decrypt ciphertext using AES-256-CBC.
        
        Args:
            key: 32-byte AES key
            iv: Initialization vector
            ciphertext: Data to decrypt
            hmac_sig: HMAC signature for verification
            
        Returns:
            Decrypted plaintext
            
        Raises:
            ValueError: If HMAC verification fails
        """
        if len(key) != SymmetricCrypto.KEY_SIZE:
            raise ValueError(f"Key must be {SymmetricCrypto.KEY_SIZE} bytes")
        
        # Verify HMAC first (constant-time comparison)
        data_to_verify = iv + ciphertext
        if not SymmetricCrypto.verify_hmac(key, data_to_verify, hmac_sig):
            raise ValueError("HMAC verification failed - data may have been tampered with")
        
        # Create cipher
        cipher = Cipher(
            SymmetricCrypto.ALGORITHM(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        plaintext = SymmetricCrypto.unpad_data(padded_plaintext)
        
        return plaintext
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """
        Compute SHA-256 hash of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex string of hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
