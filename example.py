"""
Complete Example and Demonstration of the Hybrid Cryptosystem

This example demonstrates:
1. Key pair generation (Alice and Bob)
2. File encryption with signing
3. File decryption with signature verification
4. All cryptographic operations
"""

import os
import tempfile
from pathlib import Path
from src.asymmetric import AsymmetricCrypto
from src.hybrid import HybridEncryptor
from src.signature import DigitalSignature
from src.encryption import SymmetricCrypto


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def example_complete_workflow():
    """Run complete example workflow."""
    
    print_header("SECURE FILE ENCRYPTION - HYBRID CRYPTOSYSTEM DEMO")
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    print(f"Demo directory: {temp_dir}\n")
    
    try:
        # ============================================================
        # STEP 1: Key Generation
        # ============================================================
        print_header("STEP 1: Key Generation")
        print("Scenario: Alice and Bob exchange messages securely\n")
        
        # Alice generates her key pair
        print("Generating Alice's RSA-2048 key pair...")
        alice_private, alice_public = AsymmetricCrypto.generate_key_pair()
        alice_priv_path = os.path.join(temp_dir, 'alice_private.pem')
        alice_pub_path = os.path.join(temp_dir, 'alice_public.pem')
        AsymmetricCrypto.save_private_key(alice_private, alice_priv_path)
        AsymmetricCrypto.save_public_key(alice_public, alice_pub_path)
        print(f"✓ Alice's private key: {alice_priv_path} ({len(alice_private)} bytes)")
        print(f"✓ Alice's public key:  {alice_pub_path} ({len(alice_public)} bytes)")
        
        # Bob generates his key pair
        print("\nGenerating Bob's RSA-2048 key pair...")
        bob_private, bob_public = AsymmetricCrypto.generate_key_pair()
        bob_priv_path = os.path.join(temp_dir, 'bob_private.pem')
        bob_pub_path = os.path.join(temp_dir, 'bob_public.pem')
        AsymmetricCrypto.save_private_key(bob_private, bob_priv_path)
        AsymmetricCrypto.save_public_key(bob_public, bob_pub_path)
        print(f"✓ Bob's private key:   {bob_priv_path} ({len(bob_private)} bytes)")
        print(f"✓ Bob's public key:    {bob_pub_path} ({len(bob_public)} bytes)")
        
        # ============================================================
        # STEP 2: Create a Document to Encrypt
        # ============================================================
        print_header("STEP 2: Document Creation")
        
        message = """
        CONFIDENTIAL DOCUMENT
        =====================
        
        From: Alice
        To: Bob
        Date: 2026-02-15
        
        This is a highly sensitive message that requires:
        1. Confidentiality (encryption)
        2. Integrity protection (HMAC)
        3. Authentication (digital signature)
        4. Non-repudiation (digital signature)
        
        The hybrid cryptosystem ensures all these properties!
        
        Best regards,
        Alice
        """
        
        message_file = os.path.join(temp_dir, 'message.txt')
        with open(message_file, 'w') as f:
            f.write(message)
        
        file_hash = SymmetricCrypto.compute_file_hash(message_file)
        print(f"Document created: {Path(message_file).name}")
        print(f"File size: {os.path.getsize(message_file)} bytes")
        print(f"SHA-256 hash: {file_hash}")
        
        # ============================================================
        # STEP 3: Encryption (Alice encrypts for Bob)
        # ============================================================
        print_header("STEP 3: File Encryption (Alice→Bob)")
        print("Alice encrypts the message for Bob and signs it\n")
        
        encrypted_file = os.path.join(temp_dir, 'message.txt.encrypted')
        encrypted_path = HybridEncryptor.encrypt_file(
            message_file,
            bob_public,
            sender_private_key=alice_private,
            output_file=encrypted_file,
            sign=True
        )
        
        print(f"✓ File encrypted successfully!")
        print(f"✓ Encrypted file: {Path(encrypted_path).name}")
        print(f"✓ File size: {os.path.getsize(encrypted_path)} bytes")
        
        # Show encryption info
        info = HybridEncryptor.get_encryption_info(encrypted_path)
        print(f"\nEncryption Details:")
        print(f"  - Algorithm: AES-256-CBC + RSA-2048 + SHA-256")
        print(f"  - Original filename: {info['original_filename']}")
        print(f"  - Ciphertext size: {info['ciphertext_size']} bytes")
        print(f"  - Encrypted AES key size: {info['encrypted_key_size']} bytes")
        print(f"  - Digital signature: {'Yes (signed)' if info['is_signed'] else 'No'}")
        
        # ============================================================
        # STEP 4: Transmission (Simulated)
        # ============================================================
        print_header("STEP 4: Secure Transmission")
        print("Encrypted message transmitted over insecure channel")
        print("✓ Only ciphertext and encrypted key are visible")
        print("✓ Original message is completely hidden")
        print("✓ Integrity and authenticity are cryptographically verified")
        
        # ============================================================
        # STEP 5: Decryption (Bob decrypts and verifies)
        # ============================================================
        print_header("STEP 5: Decryption & Verification (Bob)")
        print("Bob decrypts the message and verifies Alice's signature\n")
        
        decrypted_file = os.path.join(temp_dir, 'message_decrypted.txt')
        decrypted_path = HybridEncryptor.decrypt_file(
            encrypted_path,
            bob_private,
            sender_public_key=alice_public,
            output_file=decrypted_file,
            verify_signature=True
        )
        
        print(f"✓ File decrypted successfully!")
        print(f"✓ Signature verified - message is authentic!")
        print(f"✓ Decrypted file: {Path(decrypted_path).name}")
        
        # ============================================================
        # STEP 6: Verification
        # ============================================================
        print_header("STEP 6: Integrity Verification")
        
        # Compare original and decrypted
        original_hash = SymmetricCrypto.compute_file_hash(message_file)
        decrypted_hash = SymmetricCrypto.compute_file_hash(decrypted_path)
        
        print(f"Original file hash:  {original_hash}")
        print(f"Decrypted file hash: {decrypted_hash}")
        print(f"Hashes match: {'✓ YES' if original_hash == decrypted_hash else '✗ NO'}")
        
        # Show decrypted content
        print("\nDecrypted Message:")
        print("-" * 60)
        with open(decrypted_path, 'r') as f:
            print(f.read())
        print("-" * 60)
        
        # ============================================================
        # STEP 7: Direct File Signing (Without Encryption)
        # ============================================================
        print_header("STEP 7: Direct Digital Signatures")
        print("Scenario: Sign a document without encryption\n")
        
        document_file = os.path.join(temp_dir, 'contract.txt')
        with open(document_file, 'w') as f:
            f.write("This is a legally binding contract.\nBob agrees to the terms.")
        
        signature_file = os.path.join(temp_dir, 'contract.sig')
        signature = DigitalSignature.sign_file(document_file, bob_private)
        with open(signature_file, 'wb') as f:
            f.write(signature)
        
        print(f"✓ Document signed: {Path(document_file).name}")
        print(f"✓ Signature saved: {Path(signature_file).name}")
        print(f"✓ Signature size: {len(signature)} bytes")
        
        # Verify signature
        is_valid = DigitalSignature.verify_file_signature(
            document_file,
            signature,
            bob_public
        )
        print(f"✓ Signature verification: {'VALID' if is_valid else 'INVALID'}")
        
        # ============================================================
        # STEP 8: Tampering Detection
        # ============================================================
        print_header("STEP 8: Tampering Detection")
        print("Demonstrating how tampering is detected\n")
        
        # Create a tampered version
        tampered_file = os.path.join(temp_dir, 'message_tampered.txt.encrypted')
        with open(encrypted_path, 'r') as f:
            content = f.read()
        
        # Tamper with the ciphertext
        import json
        package = json.loads(content)
        # Flip a bit in the ciphertext
        ciphertext_b64 = package['ciphertext']
        ctxt = bytearray(__import__('base64').b64decode(ciphertext_b64))
        ctxt[0] ^= 0xFF  # Flip all bits in first byte
        package['ciphertext'] = __import__('base64').b64encode(ctxt).decode('utf-8')
        
        with open(tampered_file, 'w') as f:
            json.dump(package, f)
        
        print("Created tampered encrypted file...")
        
        try:
            tampered_decrypted = os.path.join(temp_dir, 'tampered_decrypted.txt')
            HybridEncryptor.decrypt_file(
                tampered_file,
                bob_private,
                output_file=tampered_decrypted
            )
            print("✗ Decryption succeeded (unexpected!)")
        except ValueError as e:
            print(f"✓ Tampering detected: {e}")
            print("✓ HMAC verification prevented data corruption!")
        
        # ============================================================
        # Summary
        # ============================================================
        print_header("Summary & Security Properties")
        
        summary = """
HYBRID CRYPTOSYSTEM ARCHITECTURE:
==================================

1. SYMMETRIC ENCRYPTION (AES-256)
   ✓ Fast encryption/decryption
   ✓ Large file support
   ✓ 256-bit security level

2. ASYMMETRIC ENCRYPTION (RSA-2048)
   ✓ Secure key distribution
   ✓ Each recipient has unique key
   ✓ No pre-shared secrets needed

3. INTEGRITY (HMAC-SHA256)
   ✓ Detects any tampering
   ✓ Constant-time verification
   ✓ Protects both IV and ciphertext

4. AUTHENTICATION (RSA Signatures)
   ✓ Sender authentication
   ✓ Non-repudiation
   ✓ Message origin verification

SECURITY PROPERTIES ACHIEVED:
=================================
☑ Confidentiality    - Only recipient can decrypt
☑ Integrity         - Tampering is immediately detected
☑ Authentication    - Sender is verified via signature
☑ Non-repudiation   - Sender cannot deny creating message
☑ Forward secrecy   - New AES key generated each time
☑ Secure key mgmt   - Private keys never transmitted

REAL-WORLD APPLICATIONS:
==========================
- TLS/SSL protocols (HTTPS)
- PGP/GPG email encryption
- Signal/WhatsApp messaging
- Blockchain transactions
- Digital certificates
- Secure file storage systems
        """
        
        print(summary)
        
    finally:
        # Cleanup
        import shutil
        print(f"\nNote: Demo files saved to: {temp_dir}")
        print("(Files remain for inspection, delete manually if needed)")


def example_programmatic_usage():
    """Example of using the library programmatically."""
    
    print_header("PROGRAMMATIC USAGE EXAMPLE")
    
    from src import HybridEncryptor, AsymmetricCrypto
    
    # Generate keys
    private_key, public_key = AsymmetricCrypto.generate_key_pair()
    
    # Create sample data
    sample_data = b"Secret message"
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    sample_file = os.path.join(temp_dir, 'sample.txt')
    with open(sample_file, 'wb') as f:
        f.write(sample_data)
    
    # Encrypt
    encrypted_file = HybridEncryptor.encrypt_file(
        sample_file,
        public_key
    )
    
    # Decrypt
    decrypted_file = HybridEncryptor.decrypt_file(
        encrypted_file,
        private_key
    )
    
    # Verify
    with open(decrypted_file, 'rb') as f:
        recovered_data = f.read()
    
    print(f"Original:  {sample_data}")
    print(f"Recovered: {recovered_data}")
    print(f"Match: {sample_data == recovered_data}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


if __name__ == '__main__':
    example_complete_workflow()
    # Uncomment to see programmatic API usage:
    # example_programmatic_usage()
