#!/usr/bin/env python3
"""
Demo script showing the new interactive signature verification feature.

This script demonstrates:
1. Generating RSA key pairs for Alice (sender) and Bob (recipient)
2. Creating and encrypting a file with signature
3. Decrypting and verifying the signature with interactive prompts
"""

import os
import tempfile
import json
from pathlib import Path
from src.asymmetric import AsymmetricCrypto
from src.hybrid import HybridEncryptor

def setup_demo():
    """Setup demo files and keys."""
    demo_dir = Path("/tmp/crypto_demo")
    demo_dir.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("  Cryptographic Signature Verification Demo")
    print("=" * 70)
    print()
    
    # Generate keys for Alice (sender)
    print("📌 Step 1: Generating RSA keys for Alice (Sender)")
    print("-" * 70)
    alice_priv, alice_pub = AsymmetricCrypto.generate_key_pair()
    alice_priv_file = demo_dir / "alice_private.pem"
    alice_pub_file = demo_dir / "alice_public.pem"
    
    with open(alice_priv_file, 'wb') as f:
        f.write(alice_priv)
    with open(alice_pub_file, 'wb') as f:
        f.write(alice_pub)
    
    print(f"✓ Alice's private key: {alice_priv_file}")
    print(f"✓ Alice's public key: {alice_pub_file}")
    print()
    
    # Generate keys for Bob (recipient)
    print("📌 Step 2: Generating RSA keys for Bob (Recipient)")
    print("-" * 70)
    bob_priv, bob_pub = AsymmetricCrypto.generate_key_pair()
    bob_priv_file = demo_dir / "bob_private.pem"
    bob_pub_file = demo_dir / "bob_public.pem"
    
    with open(bob_priv_file, 'wb') as f:
        f.write(bob_priv)
    with open(bob_pub_file, 'wb') as f:
        f.write(bob_pub)
    
    print(f"✓ Bob's private key: {bob_priv_file}")
    print(f"✓ Bob's public key: {bob_pub_file}")
    print()
    
    # Create a test document
    print("📌 Step 3: Creating a test document")
    print("-" * 70)
    test_file = demo_dir / "secret_message.txt"
    with open(test_file, 'w') as f:
        f.write("This is a confidential message from Alice to Bob.\n")
        f.write("It is encrypted with AES-256 and signed with RSA digital signature.\n")
        f.write("Bob can verify authenticity by checking the signature with Alice's public key.")
    
    print(f"✓ Created test document: {test_file}")
    print(f"  Content preview:")
    with open(test_file, 'r') as f:
        for line in f:
            print(f"    → {line.rstrip()}")
    print()
    
    # Encrypt and sign the file
    print("📌 Step 4: Encrypting file with signature")
    print("-" * 70)
    encrypted_file = demo_dir / "secret_message.txt.encrypted"
    
    HybridEncryptor.encrypt_file(
        str(test_file),
        bob_pub,
        sender_private_key=alice_priv,
        output_file=str(encrypted_file),
        sign=True
    )
    
    print(f"✓ File encrypted with signature: {encrypted_file}")
    
    # Show encryption info
    info = HybridEncryptor.get_encryption_info(str(encrypted_file))
    print(f"  Encryption info:")
    print(f"    → Original filename: {info['original_filename']}")
    print(f"    → Version: {info['version']}")
    print(f"    → Digitally signed: {info['is_signed']}")
    print(f"    → Ciphertext size: {info['ciphertext_size']:,} bytes")
    print()
    
    # Decrypt and verify
    print("📌 Step 5: Decrypting and verifying signature")
    print("-" * 70)
    decrypted_file = demo_dir / "secret_message.txt.decrypted"
    
    try:
        output = HybridEncryptor.decrypt_file(
            str(encrypted_file),
            bob_priv,
            sender_public_key=alice_pub,
            output_file=str(decrypted_file),
            verify_signature=True
        )
        
        print(f"✓ File decrypted successfully: {output}")
        print(f"✓ Signature verified - file is authentic! ✅")
        print()
        
        # Show decrypted content
        print("📌 Step 6: Decrypted content")
        print("-" * 70)
        with open(decrypted_file, 'r') as f:
            for line in f:
                print(f"  {line.rstrip()}")
        print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Show verification matrix
    print("📌 Verification Results Summary")
    print("=" * 70)
    print("✅ File was decrypted successfully")
    print("✅ File integrity verified (HMAC check passed)")
    print("✅ Signature verified (authentic from Alice)")
    print()
    
    print("Files created in:", demo_dir)
    print("=" * 70)
    print()
    
    # Print instructions for CLI testing
    print("📋 To test with CLI interactive verification prompt:")
    print("-" * 70)
    print()
    print("1. Decrypt without verification flag (will ask you to verify):")
    print(f"   python -m src.cli decrypt \\")
    print(f"     -i {encrypted_file} \\")
    print(f"     -p {bob_priv_file}")
    print()
    print("2. It will ask: 'Do you want to verify the sender's signature?'")
    print("3. Answer 'yes' and provide Alice's public key path:")
    print(f"   {alice_pub_file}")
    print()
    print("=" * 70)

if __name__ == "__main__":
    setup_demo()
