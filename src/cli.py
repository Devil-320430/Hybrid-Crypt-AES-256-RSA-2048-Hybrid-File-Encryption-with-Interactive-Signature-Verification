"""
Command-Line Interface for Secure File Encryption Tool

Provides easy-to-use CLI commands for:
- Key generation
- File encryption
- File decryption
- Signature verification
"""

import argparse
import sys
from pathlib import Path
from .asymmetric import AsymmetricCrypto
from .hybrid import HybridEncryptor
from .signature import DigitalSignature


def init_keys(args):
    """Generate new RSA key pair."""
    print(f"Generating RSA-{AsymmetricCrypto.KEY_SIZE} key pair...")
    
    private_key, public_key = AsymmetricCrypto.generate_key_pair()
    
    # Save keys
    AsymmetricCrypto.save_private_key(private_key, args.private)
    AsymmetricCrypto.save_public_key(public_key, args.public)
    
    print(f"✓ Private key saved to: {args.private}")
    print(f"✓ Public key saved to: {args.public}")
    print(f"\nKeep your private key safe and never share it!")


def encrypt_file(args):
    """Encrypt a file using hybrid cryptosystem."""
    print(f"Encrypting file: {args.input}")
    
    # Load recipient's public key
    recipient_pub = AsymmetricCrypto.load_public_key(args.recipient_key)
    
    # Load sender's private key if signing is enabled
    sender_priv = None
    if args.sign:
        if args.sender_key is None:
            print("Error: --sender-key required when using --sign")
            sys.exit(1)
        sender_priv = AsymmetricCrypto.load_private_key(args.sender_key)
    
    # Encrypt
    output = HybridEncryptor.encrypt_file(
        args.input,
        recipient_pub,
        sender_private_key=sender_priv,
        output_file=args.output,
        sign=args.sign
    )
    
    print(f"✓ File encrypted successfully!")
    print(f"✓ Output saved to: {output}")
    
    # Get file info
    info = HybridEncryptor.get_encryption_info(output)
    print(f"  - Original: {info['original_filename']}")
    print(f"  - Ciphertext size: {info['ciphertext_size']} bytes")
    print(f"  - Encrypted key size: {info['encrypted_key_size']} bytes")
    if info['is_signed']:
        print(f"  - Digitally signed: Yes")


def decrypt_file(args):
    """Decrypt a file."""
    print(f"Decrypting file: {args.input}")
    
    # Load recipient's private key
    recipient_priv = AsymmetricCrypto.load_private_key(args.recipient_key)
    
    # Check if file is signed BEFORE decrypting
    try:
        file_info = HybridEncryptor.get_encryption_info(args.input)
        is_signed = file_info.get('is_signed', False)
    except Exception as e:
        print(f"✗ Error reading file info: {e}")
        sys.exit(1)
    
    # Load sender's public key if verification is enabled
    sender_pub = None
    verify_signature = args.verify
    
    if args.verify:
        if args.sender_key is None:
            print("Error: --sender-key required when using --verify")
            sys.exit(1)
        sender_pub = AsymmetricCrypto.load_public_key(args.sender_key)
    elif is_signed:
        # File is signed but user didn't specify --verify flag
        # Ask user if they want to verify the signature
        print(f"\n📋 File Information:")
        print(f"   ✓ This file is digitally signed")
        print(f"   ✓ Original filename: {file_info.get('original_filename', 'Unknown')}")
        
        response = input(f"\n🔐 Do you want to verify the sender's signature? (yes/no): ").strip().lower()
        
        if response in ['yes', 'y']:
            # Ask for sender's public key
            sender_key_path = input("📝 Enter the path to sender's public key file: ").strip()
            
            if not sender_key_path:
                print("✗ No public key file provided. Skipping verification.")
            elif not Path(sender_key_path).exists():
                print(f"✗ File not found: {sender_key_path}")
                sys.exit(1)
            else:
                try:
                    sender_pub = AsymmetricCrypto.load_public_key(sender_key_path)
                    verify_signature = True
                    print("✓ Sender's public key loaded successfully")
                except Exception as e:
                    print(f"✗ Error loading sender's public key: {e}")
                    sys.exit(1)
        else:
            print("⚠️  Skipping signature verification - file origin cannot be verified")
    
    try:
        # Decrypt
        output = HybridEncryptor.decrypt_file(
            args.input,
            recipient_priv,
            sender_public_key=sender_pub,
            output_file=args.output,
            verify_signature=verify_signature
        )
        
        print(f"\n✓ File decrypted successfully!")
        print(f"✓ Output saved to: {output}")
        
        if verify_signature and is_signed:
            print(f"✓ Signature verified - file is authentic and unmodified! ✅")
        elif is_signed and not verify_signature:
            print(f"⚠️  File is signed but signature was not verified")
    
    except ValueError as e:
        print(f"\n✗ Decryption failed: {e}")
        sys.exit(1)


def sign_file(args):
    """Sign a file."""
    print(f"Signing file: {args.input}")
    
    # Load private key
    private_key = AsymmetricCrypto.load_private_key(args.private)
    
    # Sign
    signature = DigitalSignature.sign_file(args.input, private_key)
    
    # Save signature
    with open(args.output, 'wb') as f:
        f.write(signature)
    
    print(f"✓ File signed successfully!")
    print(f"✓ Signature saved to: {args.output}")


def verify_signature(args):
    """Verify a file signature."""
    print(f"Verifying signature...")
    
    # Load public key and signature
    public_key = AsymmetricCrypto.load_public_key(args.public)
    with open(args.signature, 'rb') as f:
        signature = f.read()
    
    # Verify
    is_valid = DigitalSignature.verify_file_signature(args.input, signature, public_key)
    
    if is_valid:
        print(f"✓ Signature is VALID - file is authentic and unmodified!")
    else:
        print(f"✗ Signature is INVALID - file may have been tampered with!")
        sys.exit(1)


def info(args):
    """Display encryption information about a file."""
    info = HybridEncryptor.get_encryption_info(args.input)
    
    print(f"Encryption Information: {args.input}\n")
    print(f"  Version: {info['version']}")
    print(f"  Original Filename: {info['original_filename']}")
    print(f"  Digitally Signed: {'Yes' if info['is_signed'] else 'No'}")
    print(f"  Ciphertext Size: {info['ciphertext_size']:,} bytes")
    print(f"  Encrypted Key Size: {info['encrypted_key_size']} bytes")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Secure File Encryption Tool (Hybrid Cryptosystem)',
        formatter_class= argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate key pair
  python -m src.cli keygen --private <private_key_name>.pem --public <public_key_name>.pub
  
  # Encrypt only (no signature)
  python -m src.cli encrypt -i <your file location> -r mykey.pub -o <Give any name & where you want to put the Encrypted file>.              # mykey.pub is Public key

  # Encrypt and sign at the same time
  python -m src.cli encrypt -i <your file location> -r mykey.pub --sign --sender mykey.pem                                                   # mykey.pub is Public key & mykey.pem is private key
  
  # Decrypt only (no verification)
  python -m src.cli decrypt -i <your Encrypted file location> -r mykey.pem -o <Give any name & where you want to put the Encrypted file>.    # mykey.pem is Public key

  # Decrypt and verify a signature
  python -m src.cli decrypt -i <your Encrypted file location> -r mykey.pem --verify --sender sender.pub                                      # mykey.pub is Public key & mykey.pem is private key
  
  # Sign a file
  python -m src.cli sign -i <your file location> --private mykey.pem -o <Give any name & where you want to put the Encrypted file>           # mykey.pem is Public key
  
  # Verify signature
  python -m src.cli verify -i <your sined file location> --signature <output file of the signed file> --public mykey.pub                     # mykey.pub is Public key
  
  # Get encryption info
  python -m src.cli info -i <your Encrypted file location>
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Keygen command
    keygen_parser = subparsers.add_parser('keygen', help='Generate RSA key pair')
    keygen_parser.add_argument('--private', default='private.pem', 
                               help='Output path for private key (default: private.pem)')
    keygen_parser.add_argument('--public', default='public.pem',
                               help='Output path for public key (default: public.pem)')
    keygen_parser.set_defaults(func=init_keys)
    
    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a file')
    encrypt_parser.add_argument('-i', '--input', required=True, help='Input file to encrypt')
    encrypt_parser.add_argument('-r', '--recipient-key', required=True,
                                help='Recipient RSA public key file')
    encrypt_parser.add_argument('-o', '--output', help='Output file (default: input.encrypted)')
    encrypt_parser.add_argument('--sign', action='store_true',
                                help='Sign the file (requires --sender)')
    encrypt_parser.add_argument('--sender', dest='sender_key',
                                help='Sender RSA private key file (for signing)')
    encrypt_parser.set_defaults(func=encrypt_file)
    
    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt a file')
    decrypt_parser.add_argument('-i', '--input', required=True, help='Encrypted file')
    decrypt_parser.add_argument('-r', '--recipient-key', required=True,
                                help='Recipient RSA private key file')
    decrypt_parser.add_argument('-o', '--output', help='Output file')
    decrypt_parser.add_argument('--verify', action='store_true',
                                help='Verify digital signature (requires --sender)')
    decrypt_parser.add_argument('--sender', dest='sender_key',
                                help='Sender RSA public key file (for verification)')
    decrypt_parser.set_defaults(func=decrypt_file)
    
    # Sign command
    sign_parser = subparsers.add_parser('sign', help='Sign a file')
    sign_parser.add_argument('-i', '--input', required=True, help='File to sign')
    sign_parser.add_argument('--private', required=True, help='RSA private key file')
    sign_parser.add_argument('-o', '--output', default='signature.sig',
                             help='Output signature file (default: signature.sig)')
    sign_parser.set_defaults(func=sign_file)
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify file signature')
    verify_parser.add_argument('-i', '--input', required=True, help='File to verify')
    verify_parser.add_argument('--signature', required=True, help='Signature file')
    verify_parser.add_argument('--public', required=True, help='RSA public key file')
    verify_parser.set_defaults(func=verify_signature)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Display encryption info')
    info_parser.add_argument('-i', '--input', required=True, help='Encrypted file')
    info_parser.set_defaults(func=info)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
