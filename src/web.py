#!/usr/bin/env python3
"""
Flask Web Interface for Hybrid Cryptosystem

Run with:
    python -m src.web

Provides a web UI at http://localhost:5000 for:
- Key generation
- File encryption/decryption
- File signing/verification
"""

import os
import sys
import json
import base64
import argparse
import socket
from pathlib import Path
from pathlib import Path as PathlibPath
from flask import Flask, render_template, request, jsonify, send_file
import tempfile
import traceback

try:
    from src.asymmetric import AsymmetricCrypto
    from src.hybrid import HybridEncryptor
    from src.signature import DigitalSignature
except Exception:
    project_root = PathlibPath(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    from src.asymmetric import AsymmetricCrypto
    from src.hybrid import HybridEncryptor
    from src.signature import DigitalSignature


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024 * 1024  # 3 GB max file size


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/keygen', methods=['POST'])
def keygen():
    """Generate RSA key pair."""
    try:
        private_key, public_key = AsymmetricCrypto.generate_key_pair()
        return jsonify({
            'success': True,
            'private_key': private_key.decode('utf-8'),
            'public_key': public_key.decode('utf-8')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/encrypt', methods=['POST'])
def encrypt_file():
    """Encrypt a file."""
    try:
        # Check required fields
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        if 'recipient_public_key' not in request.form:
            return jsonify({'success': False, 'error': 'No recipient public key provided'}), 400
        
        file = request.files['file']
        recipient_pub_key = request.form['recipient_public_key'].encode('utf-8')
        sender_priv_key = request.form.get('sender_private_key')
        sign = request.form.get('sign') == 'true'
        
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_in:
            file.save(tmp_in.name)
            input_file = tmp_in.name
        
        try:
            # Prepare sender key if signing
            sender_priv = None
            if sign:
                if not sender_priv_key:
                    return jsonify({'success': False, 'error': 'Sender private key required for signing'}), 400
                sender_priv = sender_priv_key.encode('utf-8')
            
            # Encrypt
            with tempfile.NamedTemporaryFile(delete=False, suffix='.encrypted') as tmp_out:
                output_file = tmp_out.name
            
            HybridEncryptor.encrypt_file(
                input_file,
                recipient_pub_key,
                sender_private_key=sender_priv,
                output_file=output_file,
                sign=sign
            )
            
            # Read encrypted file
            with open(output_file, 'r') as f:
                encrypted_content = f.read()
            
            # Cleanup
            os.unlink(input_file)
            os.unlink(output_file)
            
            return jsonify({
                'success': True,
                'encrypted_file': encrypted_content,
                'filename': file.filename + '.encrypted'
            })
        
        except Exception as e:
            if os.path.exists(input_file):
                os.unlink(input_file)
            raise e
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/decrypt', methods=['POST'])
def decrypt_file():
    """Decrypt a file."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        if 'recipient_private_key' not in request.form:
            return jsonify({'success': False, 'error': 'No recipient private key provided'}), 400
        
        file = request.files['file']
        recipient_priv_key = request.form['recipient_private_key'].encode('utf-8')
        sender_pub_key = request.form.get('sender_public_key')
        verify = request.form.get('verify') == 'true'
        
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Create temp input file for encrypted data
        input_file = None
        output_file = None
        
        try:
            # Read and validate file content
            file_content = file.read()
            if not file_content:
                return jsonify({'success': False, 'error': 'File is empty'}), 400
            
            # Determine original filename
            original_filename = Path(file.filename).stem  # Remove extension
            if original_filename.endswith('.enc'):
                original_filename = original_filename[:-4]  # Remove .enc if present
            
            # Validate file is valid JSON (encrypted format)
            try:
                encrypted_data = json.loads(file_content.decode('utf-8'))
            except json.JSONDecodeError as e:
                return jsonify({
                    'success': False, 
                    'error': f'Invalid encrypted file format. File must be JSON encrypted format. Error: {str(e)}'
                }), 400
            
            # Check required fields in encrypted data
            required_fields = ['version', 'iv', 'ciphertext', 'encrypted_aes_key', 'hmac']
            missing_fields = [f for f in required_fields if f not in encrypted_data]
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': f'Encrypted file is corrupted. Missing fields: {", ".join(missing_fields)}'
                }), 400
            
            # Check if file is digitally signed
            is_signed = encrypted_data.get('is_signed', False)
            has_signature = encrypted_data.get('signature') is not None
            
            # If file is signed but user didn't provide verification, ask for it
            if is_signed and has_signature and not verify:
                return jsonify({
                    'success': False,
                    'requires_verification': True,
                    'is_signed': is_signed,
                    'error': 'This file is digitally signed. Verification information needed.',
                    'message': 'To verify the authenticity of this signed file, please provide the sender\'s public key and check the "Verify signature" option.'
                }), 202  # 202 Accepted - indicating further action needed
            
            # Create temp file for encrypted data
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as tmp_in:
                tmp_in.write(file_content.decode('utf-8'))
                input_file = tmp_in.name
            
            # Validate private key format
            try:
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.backends import default_backend
                priv = serialization.load_pem_private_key(
                    recipient_priv_key,
                    password=None,
                    backend=default_backend()
                )
            except Exception as key_err:
                return jsonify({
                    'success': False,
                    'error': f'Invalid private key format: {str(key_err)}'
                }), 400
            
            # Prepare sender key if verifying
            sender_pub = None
            if verify:
                if not sender_pub_key:
                    return jsonify({'success': False, 'error': 'Sender public key required for verification'}), 400
                try:
                    sender_pub = sender_pub_key.encode('utf-8')
                    # Validate format
                    serialization.load_pem_public_key(
                        sender_pub,
                        backend=default_backend()
                    )
                except Exception as key_err:
                    return jsonify({
                        'success': False,
                        'error': f'Invalid sender public key format: {str(key_err)}'
                    }), 400
            
            # Create temp file for decrypted output
            output_file = tempfile.NamedTemporaryFile(delete=False).name
            
            # Attempt decryption
            try:
                HybridEncryptor.decrypt_file(
                    input_file,
                    recipient_priv_key,
                    sender_public_key=sender_pub,
                    output_file=output_file,
                    verify_signature=verify
                )
            except Exception as decrypt_err:
                error_msg = str(decrypt_err)
                # Provide helpful error messages for common issues
                if 'could not deserialize' in error_msg or 'Invalid cipher' in error_msg:
                    return jsonify({
                        'success': False,
                        'error': 'Decryption failed: Private key does not match the public key used for encryption'
                    }), 400
                elif 'Signature verification failed' in error_msg:
                    return jsonify({
                        'success': False,
                        'error': 'Signature verification failed: File may have been tampered with or wrong public key provided'
                    }), 400
                elif 'HMAC verification failed' in error_msg:
                    return jsonify({
                        'success': False,
                        'error': 'File integrity check failed: File may have been corrupted or tampered with'
                    }), 400
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Decryption error: {error_msg}'
                    }), 400
            
            # Read the DECRYPTED content
            try:
                with open(output_file, 'rb') as f:
                    decrypted_content = f.read()
            except Exception as read_err:
                return jsonify({
                    'success': False,
                    'error': f'Failed to read decrypted file: {str(read_err)}'
                }), 400
            
            # Verify we have decrypted content
            if not decrypted_content:
                return jsonify({
                    'success': False, 
                    'error': 'Decryption resulted in empty content. The encrypted file may be invalid.'
                }), 400
            
            # Use base64 encoding to preserve binary files (PDFs, images, etc.)
            decrypted_b64 = base64.b64encode(decrypted_content).decode('utf-8')
            
            response = {
                'success': True,
                'decrypted_content_b64': decrypted_b64,  # Base64 encoded binary
                'is_binary': True,
                'original_filename': original_filename,
                'is_signed': is_signed,
                'signature_verified': verify and is_signed,
            }
            
            if verify and is_signed:
                response['message'] = 'File decrypted successfully and signature verified! ✅'
                response['verification_status'] = '✅ Signature verified - file is authentic and unmodified!'
            elif is_signed:
                response['message'] = 'File decrypted successfully (signature not verified)'
                response['warning'] = 'This file is signed but verification was not performed'
            else:
                response['message'] = 'File decrypted successfully'
            
            return jsonify(response)
        
        except Exception as e:
            return jsonify({
                'success': False, 
                'error': f'Unexpected error during decryption: {str(e)}'
            }), 400
        finally:
            # Cleanup temp files
            if input_file and os.path.exists(input_file):
                try:
                    os.unlink(input_file)
                except:
                    pass
            if output_file and os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except:
                    pass
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing request: {str(e)}'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/sign', methods=['POST'])
def sign_file():
    """Sign a file."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        if 'private_key' not in request.form:
            return jsonify({'success': False, 'error': 'No private key provided'}), 400
        
        file = request.files['file']
        private_key = request.form['private_key'].encode('utf-8')
        
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            input_file = tmp.name
        
        try:
            # Sign
            signature = DigitalSignature.sign_file(input_file, private_key)
            signature_b64 = signature.hex()
            
            os.unlink(input_file)
            
            return jsonify({
                'success': True,
                'signature': signature_b64,
                'filename': file.filename + '.sig'
            })
        
        except Exception as e:
            if os.path.exists(input_file):
                os.unlink(input_file)
            raise e
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/verify', methods=['POST'])
def verify_file():
    """Verify a file signature."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        if 'signature' not in request.form:
            return jsonify({'success': False, 'error': 'No signature provided'}), 400
        if 'public_key' not in request.form:
            return jsonify({'success': False, 'error': 'No public key provided'}), 400
        
        file = request.files['file']
        signature_hex = request.form['signature']
        public_key = request.form['public_key'].encode('utf-8')
        
        if not file.filename:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        try:
            signature = bytes.fromhex(signature_hex)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid signature format'}), 400
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            input_file = tmp.name
        
        try:
            # Verify
            is_valid = DigitalSignature.verify_file_signature(input_file, signature, public_key)
            
            os.unlink(input_file)
            
            return jsonify({
                'success': True,
                'valid': is_valid,
                'message': 'Signature is VALID ✓' if is_valid else 'Signature is INVALID ✗'
            })
        
        except Exception as e:
            if os.path.exists(input_file):
                os.unlink(input_file)
            raise e
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/info', methods=['GET'])
def info():
    """Return app info."""
    return jsonify({
        'name': 'Hybrid Cryptosystem Web Interface',
        'version': '1.0',
        'algorithms': {
            'symmetric': 'AES-256-CBC',
            'asymmetric': 'RSA-2048 OAEP',
            'hash': 'SHA-256',
            'signature': 'RSA-PSS'
        }
    })


@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'File too large (max 3 GB)'}), 413


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


def main():
    """Start the Flask server."""
    parser = argparse.ArgumentParser(description='Run Hybrid Cryptosystem web UI')
    parser.add_argument('--host', '-H', default=os.environ.get('WEB_BIND', '0.0.0.0'),
                        help='Host to bind. Default 0.0.0.0 (accessible from localhost and network). Use 127.0.0.1 for localhost-only')
    parser.add_argument('--port', '-p', type=int, default=int(os.environ.get('WEB_PORT', 5000)),
                        help='Port to listen on')
    parser.add_argument('--debug', action='store_true', default=os.environ.get('WEB_DEBUG', '') == '1',
                        help='Enable Flask debug mode')
    parser.add_argument('--localhost-only', action='store_true',
                        help='Force binding to localhost (127.0.0.1) and disable the auto-reloader')
    args = parser.parse_args()

    bind_host = args.host
    bind_port = args.port
    debug = args.debug
    localhost_only = args.localhost_only

    print("=" * 60)
    print("  Hybrid Cryptosystem - Web Interface")
    print("=" * 60)
    print("\n🌐 Starting web server...")

    # Helpful guidance for where the server is reachable
    if bind_host in ('0.0.0.0', '::'):
        # Show both localhost and a likely LAN IP for convenience
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = None

        print('📍 Accessible on this machine (localhost):')
        print(f'   http://127.0.0.1:{bind_port}')
        if local_ip:
            print('📡 Accessible on the local network (other devices):')
            print(f'   http://{local_ip}:{bind_port}')
        else:
            print('📡 Bound to all interfaces (0.0.0.0). Use your machine IP on the network to connect.')
    else:
        print('📍 Open your browser and navigate to:')
        print(f'   http://{bind_host}:{bind_port}')

    print('\n💡 Features:')
    print('   ✓ Generate RSA key pairs')
    print('   ✓ Encrypt files with AES-256 + RSA')
    print('   ✓ Decrypt files')
    print('   ✓ Sign files (RSA-PSS)')
    print('   ✓ Verify signatures')
    print('\n⚠️  Press Ctrl+C to stop the server\n')
    print("=" * 60 + "\n")

    # When enforcing localhost-only, ensure we bind to 127.0.0.1 and disable the reloader
    if localhost_only:
        bind_host = '127.0.0.1'
        print('🔒 Localhost-only mode: binding to 127.0.0.1 and disabling the auto-reloader')
        use_reloader = False
    else:
        # By default, let the reloader follow the debug flag
        use_reloader = debug

    app.run(host=bind_host, port=bind_port, debug=debug, use_reloader=use_reloader)


if __name__ == '__main__':
    main()
