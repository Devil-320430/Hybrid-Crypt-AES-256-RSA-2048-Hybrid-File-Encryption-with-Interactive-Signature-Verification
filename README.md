# Secure File Encryption Tool - Hybrid Cryptosystem

A production-grade hybrid cryptosystem implementation demonstrating real-world cryptographic principles used in TLS, PGP, and other secure systems.

## ✨ What's New - Interactive Signature Verification 🆕

> **Feb 2026**: The system now automatically detects digitally signed files and prompts you to verify them interactively!

### Key Improvements
- ✅ **Auto-Detection**: Automatically detects when a file is signed
- ✅ **Smart Prompts**: Asks if you want to verify the sender's signature  
- ✅ **Easy Workflow**: No more complex command-line flags needed
- ✅ **Clear Feedback**: Shows verification status with visual indicators (✅ ⚠️ ❌)
- ✅ **Backward Compatible**: Your existing scripts still work

### Example Usage (NEW)
```bash
$ python -m src.cli decrypt -i document.encrypted -p my_private.pem

📋 File Information:
   ✓ This file is digitally signed

🔐 Do you want to verify the sender's signature? (yes/no): yes
📝 Enter the path to sender's public key file: alice_public.pem

✓ File decrypted successfully!
✓ Signature verified - file is authentic and unmodified! ✅
```

👉 See [QUICK_START_VERIFICATION.md](QUICK_START_VERIFICATION.md) for complete examples.

## 🔐 Architecture Overview

### Hybrid Cryptosystem Design

The tool implements a **hybrid cryptosystem** that combines:

```
┌─────────────────────────────────────────────────────────┐
│                  HYBRID CRYPTOSYSTEM                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. AES-256-CBC          (Symmetric Encryption)        │
│     └─ Fast bulk encryption of file content            │
│                                                         │
│  2. RSA-2048 + OAEP      (Asymmetric Encryption)       │
│     └─ Encrypt AES key with recipient's public key     │
│                                                         │
│  3. HMAC-SHA256          (Integrity Protection)        │
│     └─ Verify data wasn't tampered with               │
│                                                         │
│  4. RSA-PSS Signatures   (Digital Signatures)          │
│     └─ Authenticate sender & prevent repudiation      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Encryption Flow

```
┌──────────────┐
│ Plaintext    │
│  (File)      │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│ 1. Generate Random AES-256 Key      │
│ 2. Generate Random IV (128-bit)     │
└──────────┬──────────────────────────┘
           │
           ▼
    ┌──────────────────┐
    │ AES-256-CBC      │
    │ Encryption       │
    └────┬─────────────┘
         │
         ▼
    ┌───────────────────────┐
    │ Compute HMAC-SHA256   │
    │ (IV + Ciphertext)     │
    └────┬──────────────────┘
         │
         ▼
    ┌───────────────────────────────────┐
    │ RSA-2048 Encrypt AES Key          │
    │ (With recipient's public key)     │
    └────┬──────────────────────────────┘
         │
         ▼
    ┌───────────────────────────────────┐
    │ RSA-PSS Optional Signing          │
    │ (With sender's private key)       │
    └────┬──────────────────────────────┘
         │
         ▼
    ┌────────────────────────────┐
┌──►│ Package JSON               │◄──┐
│   │ - IV (base64)              │   │
│   │ - Ciphertext (base64)      │   │ 
│   │ - Encrypted AES Key        │   │
│   │ - HMAC Signature           │   │
│   │ - File Signature (optional)│   │
│   │ - Metadata                 │   │
│   └────────────────────────────┘   │
│                                    │
└────────────────────────────────────┘
```

## 🔑 Cryptographic Components

### 1. **Symmetric Encryption (AES-256)**

- **Algorithm**: AES-256-CBC (128-bit blocks)
- **Key Size**: 256 bits (32 bytes)
- **IV Size**: 128 bits (16 bytes)
- **Padding**: PKCS7
- **Purpose**: Fast, secure encryption of file content

```python
from src.encryption import SymmetricCrypto

# Generate key
key = SymmetricCrypto.generate_random_key()  # 32 bytes

# Encrypt
iv, ciphertext, hmac = SymmetricCrypto.encrypt(key, plaintext)

# Decrypt
plaintext = SymmetricCrypto.decrypt(key, iv, ciphertext, hmac)
```

### 2. **Asymmetric Encryption (RSA)**

- **Algorithm**: RSA-2048 (can upgrade to 4096)
- **Padding**: OAEP with SHA-256
- **Purpose**: Encrypt AES key for secure key distribution

```python
from src.asymmetric import AsymmetricCrypto

# Generate key pair
private_pem, public_pem = AsymmetricCrypto.generate_key_pair()

# Encrypt AES key with recipient's public key
encrypted_key = AsymmetricCrypto.encrypt_aes_key(aes_key, public_pem)

# Decrypt with private key
aes_key = AsymmetricCrypto.decrypt_aes_key(encrypted_key, private_pem)
```

### 3. **Integrity Protection (HMAC-SHA256)**

- **Algorithm**: HMAC with SHA-256
- **Protected Data**: IV + Ciphertext
- **Verification**: Constant-time comparison
- **Purpose**: Detect any tampering or corruption

```python
from src.encryption import SymmetricCrypto

# Compute HMAC
hmac = SymmetricCrypto.compute_hmac(key, data)

# Verify (constant-time)
is_valid = SymmetricCrypto.verify_hmac(key, data, hmac)
```

### 4. **Digital Signatures (RSA-PSS)**

- **Algorithm**: RSA-PSS with SHA-256
- **Signature Size**: 256 bytes (for 2048-bit key)
- **Purpose**: Authenticate sender and provide non-repudiation

```python
from src.signature import DigitalSignature

# Sign
signature = DigitalSignature.sign_data(data, private_key)

# Verify
is_valid = DigitalSignature.verify_signature(data, signature, public_key)
```

## 📦 Installation

```bash
cd /home/deva/Project/CRYPTOGRAPHIC
pip install -r requirements.txt
```

## 🚀 Usage

### Command-Line Interface

#### 1. Generate Key Pair

```bash
python -m src.cli keygen --private alice_private.pem --public alice_public.pem
```

**Output**:
```
Generating RSA-2048 key pair...
✓ Private key saved to: alice_private.pem
✓ Public key saved to: alice_public.pem

Keep your private key safe and never share it!
```

> **New Feature**: Files encrypted with signatures now show interactive prompts during decryption. See Method 1 in "Decrypt a File" below.

#### 2. Encrypt a File (with signature)

```bash
python -m src.cli encrypt \
  -i document.txt \
  -r recipient_public.pem \
  -o encrypted.bin \
  --sign --sender alice_private.pem
```

**Output**:
```
Encrypting file: document.txt
✓ File encrypted successfully!
✓ Output saved to: encrypted.bin
  - Original: document.txt
  - Ciphertext size: 1024 bytes
  - Encrypted key size: 256 bytes
  - Digitally signed: Yes
```

#### 3. Decrypt a File (Interactive Signature Verification) ✨ NEW

**Method 1: Interactive Verification (Recommended)**

```bash
python -m src.cli decrypt -i encrypted.bin -r recipient_private.pem
```

**Output** (system detects file is signed and asks):
```
Decrypting file: encrypted.bin

📋 File Information:
   ✓ This file is digitally signed
   ✓ Original filename: document.txt

🔐 Do you want to verify the sender's signature? (yes/no): yes
📝 Enter the path to sender's public key file: alice_public.pem
✓ Sender's public key loaded successfully

✓ File decrypted successfully!
✓ Output saved to: decrypted.txt
✓ Signature verified - file is authentic and unmodified! ✅
```

**Method 2: Using --verify Flag (Skip Prompts)**

```bash
python -m src.cli decrypt \
  -i encrypted.bin \
  -r recipient_private.pem \
  --verify \
  --sender alice_public.pem
```

**Output**:
```
Decrypting file: encrypted.bin
✓ File decrypted successfully!
✓ Output saved to: decrypted.txt
✓ Signature verified - file is authentic and unmodified! ✅
```

#### 4. Sign a File (without encryption)

```bash
python -m src.cli sign -i contract.txt --private alice_private.pem
```

#### 5. Verify Signature

```bash
python -m src.cli verify -i contract.txt --signature contract.sig --public alice_public.pem
```

#### 6. View Encryption Information

```bash
python -m src.cli info -i encrypted.bin
```

### ✨ Interactive Signature Verification (CLI) - NEW FEATURE

When you decrypt a file that is **digitally signed**, the CLI now automatically detects it and prompts you to verify:

**Key Features:**
- 🔍 **Auto-Detection**: Automatically detects signed files before decryption
- ❓ **User Prompt**: Asks "Do you want to verify the sender's signature?"
- 🔑 **Dynamic Input**: If yes, asks you to provide the sender's public key path
- ✅ **Clear Status**: Shows verification results with visual indicators
- 🔄 **Backward Compatible**: Existing scripts with `--verify` flag still work

**Workflow Example:**
```bash
# Simple decrypt command (no flags needed!)
$ python -m src.cli decrypt -i document.encrypted -p bob_private.pem

# System automatically detects signature and prompts:
📋 File Information:
   ✓ This file is digitally signed
   ✓ Original filename: contract.pdf

🔐 Do you want to verify the sender's signature? (yes/no): yes

# System asks for sender's public key:
📝 Enter the path to sender's public key file: alice_public.pem
✓ Sender's public key loaded successfully

# System decrypts AND verifies:
✓ File decrypted successfully!
✓ Output saved to: contract.pdf.decrypted
✓ Signature verified - file is authentic and unmodified! ✅
```

**Alternative: Skip Prompts (Old Way)**
If you prefer to skip the interactive prompt and provide all parameters upfront:
```bash
python -m src.cli decrypt -i document.encrypted -p bob_private.pem --verify --sender alice_public.pem
```

👉 See [QUICK_START_VERIFICATION.md](QUICK_START_VERIFICATION.md) for more examples and troubleshooting.

### Programmatic API

```python
from src.asymmetric import AsymmetricCrypto
from src.hybrid import HybridEncryptor

# Generate keys
alice_private, alice_public = AsymmetricCrypto.generate_key_pair()
bob_private, bob_public = AsymmetricCrypto.generate_key_pair()

# Encrypt file for Bob, signed by Alice
encrypted = HybridEncryptor.encrypt_file(
    'message.txt',
    bob_public,
    sender_private_key=alice_private,
    sign=True
)

# Bob decrypts and verifies Alice's signature
decrypted = HybridEncryptor.decrypt_file(
    encrypted,
    bob_private,
    sender_public_key=alice_public,
    verify_signature=True
)
```

### GUI (Tkinter)

A simple desktop GUI is provided at `src/gui.py` to perform key generation, encryption, decryption, signing, and signature verification via a graphical interface.

Run the GUI from the project root:

```bash
python -m src.gui
# or
python src/gui.py
```

If `tkinter` is missing on your system, install the OS package (Debian/Ubuntu):

```bash
sudo apt-get install python3-tk
```

The GUI offers dialogs to select files and keys and displays operation status and results.

### Web Browser Interface (Flask)

A Flask-based web interface provides modern, browser-based access to all cryptographic operations.

Run the web server from the project root:

```bash
python -m src.web
```

By default the server binds to all interfaces (`0.0.0.0`), so it is reachable from this machine (localhost) and from other devices on your local network.

Open your browser at one of the addresses below (examples):

```
# from the same machine
http://127.0.0.1:5000

# from another device on your LAN (replace <HOST_IP> with your machine's IP)
http://<HOST_IP>:5000
```

To restrict the server to localhost-only (loopback) and disable the Flask auto-reloader, start with the `--localhost-only` flag:

```bash
python -m src.web --localhost-only
```

You can also override bind and port via environment variables:

```bash
WEB_BIND=0.0.0.0 WEB_PORT=5000 python -m src.web
```

**Web Interface Features:**
- 🔑 Generate RSA-2048 key pairs
- 🔒 Encrypt files with AES-256 + RSA
- 🔓 Decrypt files with signature verification
- ✍️ Sign any file (RSA-PSS)
- ✔️ Verify file signatures
- Download encrypted/signed files
- Copy/paste keys easily
- Real-time operation status
- Max file size: 100 MB

**Browser Support:**
- Chrome/Edge/Firefox (modern versions)
- Safari
- Any browser with JavaScript enabled

**Security Notes:**
- All cryptographic operations execute locally in your browser or on your machine
- No data is sent to external servers
- HTTPS recommended for production use
- Private keys are handled securely (not stored on server)

### ✨ Web API Enhancements (NEW)

The Flask web API now provides **enhanced signature verification support**:

**Automatic Signature Detection:**
When you decrypt a file that is signed, the API returns additional information:

```json
POST /api/decrypt (first request - no verification)
Response: HTTP 202 ACCEPTED
{
  "success": false,
  "requires_verification": true,
  "is_signed": true,
  "error": "This file is digitally signed. Verification required.",
  "message": "To verify the authenticity... please provide the sender's public key"
}
```

Your frontend can detect the `requires_verification` flag and prompt the user for the sender's public key.

**After User Provides Public Key:**
```json
POST /api/decrypt (second request - with verification)
{
  "verify": true,
  "sender_public_key": "-----BEGIN PUBLIC KEY-----..."
}

Response: HTTP 200 OK
{
  "success": true,
  "is_signed": true,
  "signature_verified": true,
  "verification_status": "✅ Signature verified - file is authentic and unmodified!",
  "message": "File decrypted successfully and signature verified! ✅",
  "decrypted_content_b64": "..."
}
```

👉 See the API response examples in [SIGNATURE_VERIFICATION_CHANGES.md](SIGNATURE_VERIFICATION_CHANGES.md) for complete technical details.

## 🔬 Security Analysis

### Threat Model Protection

| Threat | Mitigation | Mechanism |
|--------|-----------|-----------|
| **Eavesdropping** | Encrypt with AES-256 | Symmetric encryption |
| **Key Theft** | Encrypt AES key with RSA | Asymmetric encryption |
| **Tampering** | Detect with HMAC | Message authentication |
| **Impersonation** | Sign with private key | Digital signatures |
| **Repudiation** | Cryptographic proof | Non-repudiation via signatures |
| **Replay Attacks** | Random IVs & HMAC | Each message is unique |

### Security Parameters

```
AES Key Length:        256 bits (2^256 possible keys)
RSA Key Length:        2048 bits (≈112-bit symmetric equiv)
HMAC Hash:             SHA-256 (256-bit output)
Signature Algorithm:   RSA-PSS (probabilistic)
Random IV Size:        128 bits (never reused)
Block Size:            128 bits (AES standard)
```

## 🔍 Example Workflow

### Scenario: Alice sends confidential document to Bob

```
ALICE                                                   BOB
─────                                                   ───

1. Generates Bob's
   public key
   (already obtained)

2. Reads plaintext
   document

3. Generates random
   AES-256 key
   ↓
4. Encrypts document
   with AES-256
   ↓
5. Generates random IV
   ↓
6. Computes HMAC-SHA256
   over (IV + Ciphertext)
   ↓
7. Encrypts AES key
   with Bob's public RSA key
   ↓
8. Signs encrypted
   package with own
   private key
   ↓
9. Packages everything
   as JSON
   ↓
10. Sends over
    INSECURE CHANNEL
    ─────────────────────────────────────────────► Receives
                                                      encrypted
                                                      package
                                                      ↓
                                                   11. Decrypts
                                                       AES key with
                                                       own private key
                                                       ↓
                                                   12. Verifies HMAC
                                                       (detects tampering)
                                                       ↓
                                                   13. Decrypts
                                                       document with AES key
                                                       ↓
                                                   14. Verifies Alice's
                                                       digital signature
                                                       ↓
                                                   15. Reads plaintext
                                                       ✓ Authentic
                                                       ✓ Unmodified
                                                       ✓ Confidential
```

## 📊 File Format

The encrypted file is a JSON structure:

```json
{
  "version": "1.0",
  "iv": "base64_encoded_iv",
  "ciphertext": "base64_encoded_ciphertext",
  "encrypted_aes_key": "base64_encoded_rsa_encrypted_key",
  "hmac": "base64_encoded_hmac",
  "signature": "base64_encoded_digital_signature_or_null",
  "is_signed": true,
  "original_filename": "document.txt"
}
```

## 🧪 Testing

Run the comprehensive example:

```bash
python example.py
```

This demonstrates:
- ✓ Key generation (Alice & Bob)
- ✓ File encryption with signing
- ✓ Secure transmission simulation
- ✓ File decryption with verification
- ✓ Integrity verification
- ✓ Direct signatures
- ✓ Tampering detection

## 📚 Key Files

| File | Purpose |
|------|---------|
| `src/encryption.py` | AES-256 & HMAC-SHA256 |
| `src/asymmetric.py` | RSA key management & encryption |
| `src/signature.py` | Digital signatures (RSA-PSS) |
| `src/hybrid.py` | Complete hybrid system |
| `src/cli.py` | Command-line interface |
| `example.py` | Comprehensive demonstration |

## 🔒 Security Best Practices

1. **Key Storage**
   - Store private keys with restricted permissions (0o600)
   - Use password-protected key storage for sensitive keys
   - Never commit private keys to version control

2. **Key Rotation**
   - Generate new keys periodically
   - Archive old keys securely
   - Communicate key changes to trusted parties

3. **File Handling**
   - Securely delete sensitive plaintext files
   - Use temporary directories for intermediate files
   - Verify file integrity after transmission

4. **Cryptographic Practices**
   - Always verify signatures from trusted sources
   - Check HMAC before decryption
   - Use random IVs (automatic in this implementation)
   - Never reuse IV with same key

## 🏗️ Real-World Applications

This hybrid cryptosystem architecture is used in:

- **TLS/SSL** - HTTPS secure web communication
- **PGP/GPG** - Email encryption and signing
- **Signal/WhatsApp** - Secure messaging
- **Blockchain** - Transaction signing and validation
- **Digital Certificates** - Public key infrastructure (PKI)
- **Cloud Storage** - End-to-end encryption
- **VPN Systems** - Secure tunneling

## 📖 Further Reading

- [NIST SP 800-38A](https://nvlpubs.nist.gov/nistpubs/) - AES CBC Mode
- [RFC 3394](https://tools.ietf.org/html/rfc3394) - AES Key Wrap
- [RFC 2104](https://tools.ietf.org/html/rfc2104) - HMAC
- [RFC 8017](https://tools.ietf.org/html/rfc8017) - PKCS #1 RSA
- [RFC 2311](https://tools.ietf.org/html/rfc2311) - S/MIME

## License

This is educational software. Use responsibly and according to local laws.

## Support

For issues or questions, review the code comments and example.py for detailed usage patterns.

---

**Remember**: 🔐 Security is a process, not a product. Always keep your private keys safe and follow best practices!
