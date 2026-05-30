"""
Secure File Encryption Tool - Hybrid Cryptosystem

A complete implementation of a hybrid cryptosystem demonstrating:
- AES-256 symmetric encryption
- RSA asymmetric encryption
- SHA-256 hashing and HMAC
- Digital signatures
- Secure key handling

This architecture is used in real-world systems like TLS, PGP, and more.
"""

from .encryption import SymmetricCrypto
from .asymmetric import AsymmetricCrypto
from .signature import DigitalSignature
from .hybrid import HybridEncryptor

__all__ = [
    'SymmetricCrypto',
    'AsymmetricCrypto',
    'DigitalSignature',
    'HybridEncryptor',
]

__version__ = '1.0.0'
