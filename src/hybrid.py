"""
Hybrid Cryptosystem - Complete Encryption Solution

This module integrates AES-256 symmetric encryption with RSA asymmetric encryption
to create a hybrid cryptosystem similar to PGP/TLS architectures.

Workflow:
1. Generate RSA key pair for recipient
2. Generate random AES-256 key
3. Encrypt file content with AES-256
4. Encrypt AES key with recipient's RSA public key
5. Optionally sign with sender's private key
6. Package everything together

Usage:
    encryptor = HybridEncryptor()
    encrypted_file = encryptor.encrypt_file(
        'plaintext.txt',
        sender_private_key,
        recipient_public_key,
        sign=True
    )
"""

import os
import json
import base64
from typing import Optional, Dict, Any
from pathlib import Path
from .encryption import SymmetricCrypto
from .asymmetric import AsymmetricCrypto
from .signature import DigitalSignature


class HybridEncryptor:
    """Complete hybrid encryption system."""
    
    HEADER_VERSION = "1.0"
    
    @staticmethod
    def encrypt_file(
        input_file: str,
        recipient_public_key: bytes,
        sender_private_key: Optional[bytes] = None,
        output_file: Optional[str] = None,
        sign: bool = False
    ) -> str:
        """
        Encrypt file using hybrid cryptosystem.
        
        Args:
            input_file: Path to file to encrypt
            recipient_public_key: Recipient's RSA public key (PEM format)
            sender_private_key: Sender's RSA private key (PEM format, needed for signing)
            output_file: Output file path (default: input_file + '.encrypted')
            sign: Whether to sign the file (requires sender_private_key)
            
        Returns:
            Path to encrypted file
            
        Raises:
            ValueError: If signing requested without sender_private_key
        """
        if sign and sender_private_key is None:
            raise ValueError("sender_private_key required for signing")
        
        # Read input file
        with open(input_file, 'rb') as f:
            plaintext = f.read()
        
        # Generate random AES-256 key
        aes_key = SymmetricCrypto.generate_random_key()
        
        # Encrypt plaintext with AES-256
        iv, ciphertext, hmac_sig = SymmetricCrypto.encrypt(aes_key, plaintext)
        
        # Encrypt AES key with recipient's public key
        encrypted_aes_key = AsymmetricCrypto.encrypt_aes_key(
            aes_key,
            recipient_public_key
        )
        
        # Optional: Sign the plaintext
        file_signature = None
        if sign and sender_private_key:
            file_signature = DigitalSignature.sign_data(plaintext, sender_private_key)
        
        # Create encrypted package
        package = {
            'version': HybridEncryptor.HEADER_VERSION,
            'iv': base64.b64encode(iv).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
            'hmac': base64.b64encode(hmac_sig).decode('utf-8'),
            'signature': base64.b64encode(file_signature).decode('utf-8') if file_signature else None,
            'is_signed': sign,
            'original_filename': Path(input_file).name
        }
        
        # Determine output file
        if output_file is None:
            output_file = input_file + '.encrypted'
        
        # Write encrypted package as JSON
        with open(output_file, 'w') as f:
            json.dump(package, f, indent=2)
        
        return output_file
    
    @staticmethod
    def decrypt_file(
        encrypted_file: str,
        recipient_private_key: bytes,
        sender_public_key: Optional[bytes] = None,
        output_file: Optional[str] = None,
        verify_signature: bool = False
    ) -> str:
        """
        Decrypt file using hybrid cryptosystem.
        
        Args:
            encrypted_file: Path to encrypted file
            recipient_private_key: Recipient's RSA private key (PEM format)
            sender_public_key: Sender's RSA public key (PEM format, needed for verification)
            output_file: Output file path (default: original filename or input + '.decrypted')
            verify_signature: Whether to verify digital signature
            
        Returns:
            Path to decrypted file
            
        Raises:
            ValueError: If signature verification fails or file is tampered
        """
        # Load encrypted package
        with open(encrypted_file, 'r') as f:
            package = json.load(f)
        
        # Validate version
        if package['version'] != HybridEncryptor.HEADER_VERSION:
            raise ValueError(f"Unsupported encryption version: {package['version']}")
        
        # Decode components
        iv = base64.b64decode(package['iv'])
        ciphertext = base64.b64decode(package['ciphertext'])
        encrypted_aes_key = base64.b64decode(package['encrypted_aes_key'])
        hmac_sig = base64.b64decode(package['hmac'])
        signature_data = base64.b64decode(package['signature']) if package['signature'] else None
        
        # Decrypt AES key with recipient's private key
        aes_key = AsymmetricCrypto.decrypt_aes_key(
            encrypted_aes_key,
            recipient_private_key
        )
        
        # Decrypt plaintext with AES-256
        plaintext = SymmetricCrypto.decrypt(aes_key, iv, ciphertext, hmac_sig)
        
        # Verify signature if present
        if package['is_signed'] and verify_signature:
            if sender_public_key is None:
                raise ValueError("sender_public_key required to verify signature")
            
            if signature_data is None:
                raise ValueError("File claims to be signed but no signature found")
            
            if not DigitalSignature.verify_signature(plaintext, signature_data, sender_public_key):
                raise ValueError("Signature verification failed - file may be tampered with")
        
        # Determine output file
        if output_file is None:
            original_filename = package.get('original_filename', 'decrypted_file')
            output_file = original_filename + '.decrypted'
        
        # Write decrypted content
        with open(output_file, 'wb') as f:
            f.write(plaintext)
        
        return output_file
    
    @staticmethod
    def get_encryption_info(encrypted_file: str) -> Dict[str, Any]:
        """
        Get information about an encrypted file without decrypting it.
        
        Args:
            encrypted_file: Path to encrypted file
            
        Returns:
            Dictionary with encryption metadata
        """
        with open(encrypted_file, 'r') as f:
            package = json.load(f)
        
        return {
            'version': package['version'],
            'original_filename': package.get('original_filename', 'unknown'),
            'is_signed': package['is_signed'],
            'ciphertext_size': len(base64.b64decode(package['ciphertext'])),
            'encrypted_key_size': len(base64.b64decode(package['encrypted_aes_key']))
        }
