# Quick Start Guide - Secure File Encryption Tool

## ✨ What's New - Interactive Signature Verification

> **Feb 2026**: The CLI now automatically detects signed files and prompts for verification! No more complex command flags needed.

### Quick Feature Highlight
- ✅ Detects digitally signed files automatically
- ✅ Asks if you want to verify the sender's signature
- ✅ Prompts for sender's public key if verification needed
- ✅ Shows clear status: ✅ Verified, ⚠️ Unverified, or ❌ Tampered
- 🔄 Fully backward compatible with existing scripts

👉 **See Step 4 below for the new interactive workflow!**

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd /home/deva/Project/CRYPTOGRAPHIC
pip install -r requirements.txt
```

### 2. Generate Your First Key Pair

```bash
python -m src.cli keygen --private mykey.pem --public mykey.pub
```

Output:
```
Generating RSA-2048 key pair...
✓ Private key saved to: mykey.pem
✓ Public key saved to: mykey.pub
Keep your private key safe and never share it!
```

### 3. Encrypt a File

```bash
python -m src.cli encrypt -i secret.txt -r recipient.pub -o secret.encrypted
```

### 4. Decrypt a File

#### Option A: Interactive Verification (Recommended) ⭐

If the file is signed, the system will automatically ask if you want to verify it:

```bash
python -m src.cli decrypt -i secret.encrypted -r mykey.pem
```

**Output** (system detects signature and prompts you):
```
Decrypting file: secret.encrypted

📋 File Information:
   ✓ This file is digitally signed

🔐 Do you want to verify the sender's signature? (yes/no): yes
📝 Enter the path to sender's public key file: sender_public.pem
✓ Sender's public key loaded successfully

✓ File decrypted successfully!
✓ Output saved to: secret.decrypted
✓ Signature verified - file is authentic and unmodified! ✅
```

#### Option B: Skip Interactive Prompts (with --verify flag)

```bash
python -m src.cli decrypt -i secret.encrypted -r mykey.pem --verify --sender sender_public.pem
```

**Output**:
```
Decrypting file: secret.encrypted
✓ File decrypted successfully!
✓ Output saved to: secret.decrypted
✓ Signature verified - file is authentic and unmodified! ✅
```

### 5. Sign a Document (Optional)

```bash
python -m src.cli encrypt -i document.txt -r recipient.pub --sign --sender mykey.pem
```

When recipient decrypts with the **new interactive feature**, they'll be prompted to verify:
```bash
python -m src.cli decrypt -i document.encrypted -r theirkey.pem
```

**Output** (system detects signature and asks automatically):
```
📋 File Information:
   ✓ This file is digitally signed
   ✓ Original filename: document.txt

🔐 Do you want to verify the sender's signature? (yes/no): yes
📝 Enter the path to sender's public key file: yourkey.pub
✓ Sender's public key loaded successfully

✓ File decrypted successfully!
✓ Output saved to: document.decrypted
✓ Signature verified - file is authentic and unmodified! ✅
```

Or skip the interactive prompt by using the --verify flag (as shown in Step 4, Method 2 above).

## 📚 Project Structure

```
/home/deva/Project/CRYPTOGRAPHIC/
├── src/
│   ├── __init__.py                      # Package initialization
│   ├── encryption.py                    # AES-256 encryption & HMAC
│   ├── asymmetric.py                    # RSA key management
│   ├── signature.py                     # Digital signatures
│   ├── hybrid.py                        # Complete hybrid system
│   ├── cli.py                           # Command-line interface (with interactive verification)
│   ├── web.py                           # Flask web API
│   └── gui.py                           # Tkinter GUI (optional)
├── test_verification_demo.py            # Demo script for new verification feature
├── example.py                           # Comprehensive demo
├── README.md                            # Full documentation
├── QUICKSTART.md                        # This file
├── QUICK_START_VERIFICATION.md          # Quick start for signature verification ⭐ NEW
├── SIGNATURE_VERIFICATION_CHANGES.md    # Technical details of verification feature ⭐ NEW
├── __main__.py                          # CLI entry point
├── requirements.txt                     # Dependencies
└── test_cli.sh                          # CLI test script
```

## 🔐 Key Features

### ✅ Symmetric Encryption
- **Algorithm**: AES-256-CBC
- **Key Size**: 256 bits
- **Padding**: PKCS7
- Fast bulk encryption of file content

### ✅ Asymmetric Encryption
- **Algorithm**: RSA-2048 (upgradeable to RSA-4096)
- **Padding**: OAEP with SHA-256
- Secure key distribution without pre-shared secrets

### ✅ Integrity Protection
- **Algorithm**: HMAC-SHA256
- **Coverage**: IV + Ciphertext
- **Verification**: Constant-time comparison
- Detects any tampering or corruption

### ✅ Digital Signatures
- **Algorithm**: RSA-PSS with SHA-256
- **Signature Size**: 256 bytes (for 2048-bit key)
- **Features**: Authentication, non-repudiation, sender verification

### 🤖 Assistant / Chatbot Feature
- ~~Ask general questions or generate images directly from the web UI~~
- **Feature removed** to avoid API dependencies and billing concerns.
### ✨ Interactive Signature Verification (NEW) 🆕
- **Auto-Detection**: System automatically detects when a file is signed
- **Smart Prompts**: Asks if you want to verify the sender's signature
- **Easy Verification**: No need to use complex --verify flags
- **Clear Feedback**: Shows verification status with visual indicators
- **Backward Compatible**: Old --verify flag still works as before

**Example**:
```bash
$ python -m src.cli decrypt -i file.encrypted -p mykey.pem

📋 File Information:
   ✓ This file is digitally signed

🔐 Do you want to verify? (yes/no): yes
📝 Enter sender's public key: alice_public.pem

✓ Signature verified - file is authentic! ✅
```

## 🔒 Security Properties

| Property | Mechanism |
|----------|-----------|
| **Confidentiality** | AES-256 encryption |
| **Integrity** | HMAC-SHA256 verification |
| **Authentication** | RSA-PSS digital signatures |
| **Non-repudiation** | Sender cannot deny creating message |
| **Forward Secrecy** | New AES key for each encryption |
| **Secure Key Mgmt** | Private keys never transmitted |

## 🎯 Use Cases

1. **Email Encryption**: Like PGP/GPG
2. **Secure File Storage**: End-to-end encryption
3. **Sensitive Document Exchange**: Sign and encrypt
4. **Confidential Messages**: Authentication + encryption
5. **Digital Contracts**: Sign and archive

## 📋 CLI Commands

### Key Generation
```bash
python -m src.cli keygen [--private FILE] [--public FILE]
```

### Encryption
```bash
python -m src.cli encrypt -i INPUT -r RECIPIENT_PUB [-o OUTPUT] 
                          [--sign --sender YOUR_PRIVATE]
```

### Decryption
```bash
python -m src.cli decrypt -i INPUT -r YOUR_PRIVATE [-o OUTPUT]
                          [--verify --sender SENDER_PUB]
```

### Direct Signature
```bash
python -m src.cli sign -i FILE --private YOUR_PRIVATE [-o SIGNATURE]
python -m src.cli verify -i FILE --signature FILE --public SENDER_PUB
```

### View Info
```bash
python -m src.cli info -i ENCRYPTED_FILE
```

## 🧪 Run the Demo

The comprehensive example demonstrates all features:

```bash
python example.py
```

This will show:
- Key pair generation
- File encryption with signing
- Decryption with verification
- Integrity checking
- Tampering detection
- Direct signatures

## 🖥️ GUI (Tkinter)

A simple desktop GUI is included to perform common operations without the CLI.

Run the GUI from the project root:

```bash
python -m src.gui
# or
python src/gui.py
```

Notes:
- `tkinter` is part of the Python standard library on many platforms. On Debian/Ubuntu install with:
    ```bash
    sudo apt-get install python3-tk
    ```
- The GUI supports: key generation, encrypt, decrypt, sign, and verify via dialogs.

## 🌐 Web Browser Interface

A Flask-based web interface provides access to all cryptographic operations through your browser.

Run the web server from the project root:

```bash
python -m src.web
```

By default the server binds to all interfaces (`0.0.0.0`) so it is reachable from this machine (localhost) and from other devices on your local network.

Open your browser (examples):

```
# from the same machine
http://127.0.0.1:5000

# from another device on your LAN (replace <HOST_IP> with your machine's IP)
http://<HOST_IP>:5000
```

To restrict the server to localhost-only and disable the auto-reloader:

```bash
python -m src.web --localhost-only
```

You can also override bind and port via environment variables:

```bash
WEB_BIND=0.0.0.0 WEB_PORT=5000 python -m src.web
```

Features:
- 🔑 Generate RSA key pairs
- 🔒 Encrypt files with AES-256 + RSA
- 🔓 Decrypt files
- ✍️ Sign files (RSA-PSS)
- ✔️ Verify signatures
- Download encrypted/signed files
- Copy keys to clipboard

Notes:
- Requires Flask (installed via `pip install -r requirements.txt`)
- All operations are local (no data is sent to external servers)
- Max file size: 100 MB
- Works in any modern web browser

## 🔑 Key Management Best Practices

1. **Backup Keys**: Keep encrypted backups of private keys
2. **File Permissions**: Private keys stored with 0o600 permissions (read/write owner only)
3. **Secure Deletion**: Use secure deletion tools for sensitive plaintext
4. **Key Rotation**: Generate new keys periodically
5. **Distribution**: Share public keys through trusted channels

## 🛡️ Encryption Flow

```
Plaintext File
    ↓
Generate Random AES-256 Key
    ↓
AES-256-CBC Encryption (generates IV + Ciphertext)
    ↓
Compute HMAC-SHA256(IV + Ciphertext)
    ↓
RSA Encrypt AES Key (with recipient's public key)
    ↓
RSA Sign Package (optional, with your private key)
    ↓
Package as JSON with metadata
    ↓
Encrypted File (.encrypted)
```

## 🔓 Decryption Flow

```
Encrypted File (.encrypted)
    ↓
RSA Decrypt AES Key (with recipient's private key)
    ↓
Verify HMAC-SHA256 (detect tampering)
    ↓
AES-256-CBC Decryption (using IV from file)
    ↓
Verify Digital Signature (optional, with sender's public key)
    ↓
Plaintext File
```

## 📊 Example Encrypted File Format

```json
{
  "version": "1.0",
  "iv": "base64_encoded_initialization_vector",
  "ciphertext": "base64_encoded_encrypted_content",
  "encrypted_aes_key": "base64_encoded_rsa_encrypted_key",
  "hmac": "base64_encoded_hmac_signature",
  "signature": "base64_encoded_rsa_pss_signature_or_null",
  "is_signed": true,
  "original_filename": "document.txt"
}
```

## 🚨 Error Handling

The tool provides clear error messages:

- **HMAC verification failed**: File was tampered with - don't trust it!
- **Signature verification failed**: Sender's identity cannot be verified
- **Decryption failed**: Wrong key or corrupted ciphertext
- **Invalid padding**: File corruption detected

## ⚙️ Advanced Usage

### Programmatic API

```python
from src.asymmetric import AsymmetricCrypto
from src.hybrid import HybridEncryptor

# Generate keys
private, public = AsymmetricCrypto.generate_key_pair()

# Encrypt
encrypted = HybridEncryptor.encrypt_file('data.txt', public)

# Decrypt
decrypted = HybridEncryptor.decrypt_file(encrypted, private)
```

### Custom Key Storage

```python
from src.asymmetric import AsymmetricCrypto

# Save keys
AsymmetricCrypto.save_private_key(private_key, 'secure_key.pem')
AsymmetricCrypto.save_public_key(public_key, 'public.pem')

# Load keys
private = AsymmetricCrypto.load_private_key('secure_key.pem')
public = AsymmetricCrypto.load_public_key('public.pem')
```

## 🔗 Real-World Applications

This hybrid cryptosystem architecture is used in:
- TLS/SSL (HTTPS)
- PGP/GPG (Email encryption)
- Signal/WhatsApp (Secure messaging)
- Blockchain (Transaction signing)
- Digital Certificates (PKI)
- Secure file storage services

## 📖 Cryptographic Standards

- **AES**: NIST FIPS 197
- **RSA**: PKCS #1 v2.2 (RFC 8017)
- **HMAC**: RFC 2104
- **SHA-256**: NIST FIPS 180-4
- **OAEP**: PKCS #1 v2.2
- **PSS**: PKCS #1 v2.2

## � Documentation Files

- **[README.md](README.md)** - Complete technical documentation
- **[QUICK_START_VERIFICATION.md](QUICK_START_VERIFICATION.md)** ⭐ - **Start here for signature verification examples!**
- **[SIGNATURE_VERIFICATION_CHANGES.md](SIGNATURE_VERIFICATION_CHANGES.md)** - Technical details of the new interactive verification feature
- **[test_verification_demo.py](test_verification_demo.py)** - Working demo of the complete verification workflow

## �🐛 Troubleshooting

**Problem**: "ModuleNotFoundError: No module named 'src'"
- **Solution**: Make sure to run commands from the `/home/deva/Project/CRYPTOGRAPHIC` directory

**Problem**: Permission denied on key files
- **Solution**: This is expected for security! Keep permissions at 0o600 (owner read/write only)

**Problem**: Signature verification fails
- **Solution**: Make sure you're using the correct sender's public key that matches the private key used for signing

**Problem**: HMAC verification fails
- **Solution**: The encrypted file may be corrupted or tampered with. Do not trust the decrypted content

## 📞 Support

For more information, see the comprehensive README.md file or run the example.py demo to see all features in action.

---

**Remember: 🔐 Keep your private keys safe and never share them!**
