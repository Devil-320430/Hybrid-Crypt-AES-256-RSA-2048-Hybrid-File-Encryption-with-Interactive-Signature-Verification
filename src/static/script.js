
// Tab switching
function showTab(tabName, evt) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    if (evt && evt.currentTarget) {
        evt.currentTarget.classList.add('active');
    }
}

// updated onclick attributes in HTML should pass 'event'

// Checkbox event listeners
document.getElementById('encrypt-sign').addEventListener('change', (e) => {
    document.getElementById('encrypt-sender-section').style.display = e.target.checked ? 'block' : 'none';
});

document.getElementById('decrypt-verify').addEventListener('change', (e) => {
    document.getElementById('decrypt-sender-section').style.display = e.target.checked ? 'block' : 'none';
});

// API calls
async function generateKeys() {
    const loader = document.getElementById('keygen-loader');
    const result = document.getElementById('keygen-result');
    
    loader.style.display = 'block';
    result.style.display = 'none';
    
    try {
        const response = await fetch('/api/keygen', {method: 'POST'});
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('private-key-output').value = data.private_key;
            document.getElementById('public-key-output').value = data.public_key;
            result.classList.remove('error');
            result.classList.add('success');
            result.style.display = 'block';
        } else {
            showError('keygen-result', data.error);
        }
    } catch (err) {
        showError('keygen-result', err.message);
    } finally {
        loader.style.display = 'none';
    }
}

async function encryptFile() {
    const file = document.getElementById('encrypt-file').files[0];
    const recipientPub = document.getElementById('encrypt-recipient-pub').value;
    const sign = document.getElementById('encrypt-sign').checked;
    const senderPriv = document.getElementById('encrypt-sender-priv').value;
    
    if (!file) {
        showError('encrypt-result', 'Please select a file');
        return;
    }
    if (!recipientPub.trim()) {
        showError('encrypt-result', 'Please provide recipient public key');
        return;
    }
    if (sign && !senderPriv.trim()) {
        showError('encrypt-result', 'Please provide your private key for signing');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('recipient_public_key', recipientPub);
    formData.append('sign', sign.toString());
    if (sign) formData.append('sender_private_key', senderPriv);
    
    const loader = document.getElementById('encrypt-loader');
    const result = document.getElementById('encrypt-result');
    
    loader.style.display = 'block';
    result.style.display = 'none';
    
    try {
        const response = await fetch('/api/encrypt', {method: 'POST', body: formData});
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('encrypt-output').value = data.encrypted_file;
            result.classList.remove('error');
            result.classList.add('success');
            result.style.display = 'block';
        } else {
            showError('encrypt-result', data.error);
        }
    } catch (err) {
        showError('encrypt-result', err.message);
    } finally {
        loader.style.display = 'none';
    }
}

async function decryptFile() {
    const file = document.getElementById('decrypt-file').files[0];
    const recipientPriv = document.getElementById('decrypt-recipient-priv').value;
    const verify = document.getElementById('decrypt-verify').checked;
    const senderPub = document.getElementById('decrypt-sender-pub').value;
    
    if (!file) {
        showError('decrypt-result', 'Please select a file');
        return;
    }
    if (!recipientPriv.trim()) {
        showError('decrypt-result', 'Please provide your private key');
        return;
    }
    if (verify && !senderPub.trim()) {
        showError('decrypt-result', 'Please provide sender public key for verification');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('recipient_private_key', recipientPriv);
    formData.append('verify', verify.toString());
    if (verify) formData.append('sender_public_key', senderPub);
    
    const loader = document.getElementById('decrypt-loader');
    const result = document.getElementById('decrypt-result');
    
    loader.style.display = 'block';
    result.style.display = 'none';
    
    try {
        const response = await fetch('/api/decrypt', {method: 'POST', body: formData});
        const data = await response.json();
        
        if (data.success) {
            // Store original filename for download
            window.decryptedFilename = data.original_filename || file.name.replace(/\.enc$/, '');
            
            // Handle base64-encoded binary content (for PDFs, images, etc.)
            if (data.decrypted_content_b64) {
                // Decode base64 to binary data
                const binaryString = atob(data.decrypted_content_b64);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                window.decryptedContent = bytes;  // Store binary data
                window.isDecryptedBinary = true;
            } else {
                // Text content (fallback for older API)
                window.decryptedContent = data.decrypted_content;
                window.isDecryptedBinary = false;
            }
            
            result.classList.remove('error');
            result.classList.add('success');
            result.innerHTML = '<strong>✓ Decrypted Successfully</strong>';
            if (data.message) {
                result.innerHTML += '<p><strong>' + data.message + '</strong></p>';
            }
            result.innerHTML += '<div style="display: flex; gap: 10px; margin-top: 10px;">';
            result.innerHTML += '<button id="decrypt-download-btn" class="download-btn" onclick="downloadDecryptedFile()">📥 Download File</button>';
            
            // Only show copy button for text files
            if (!window.isDecryptedBinary) {
                result.innerHTML += '<button class="copy-btn" onclick="copyToClipboard(\'decrypt-output\')">📋 Copy Content</button>';
            }
            result.innerHTML += '</div>';
            
            // Show textarea only for text files
            if (!window.isDecryptedBinary) {
                result.innerHTML += '<textarea id="decrypt-output" readonly style="margin-top: 10px;"></textarea>';
                document.getElementById('decrypt-output').value = window.decryptedContent;
            } else {
                result.innerHTML += '<p style="margin-top: 10px; color: #666;">📄 Binary file decrypted. Click "📥 Download File" to save.</p>';
            }
            result.style.display = 'block';
        } else {
            showError('decrypt-result', data.error);
        }
    } catch (err) {
        showError('decrypt-result', err.message);
    } finally {
        loader.style.display = 'none';
    }
}

async function signFile() {
    const file = document.getElementById('sign-file').files[0];
    const privateKey = document.getElementById('sign-private-key').value;
    
    if (!file) {
        showError('sign-result', 'Please select a file');
        return;
    }
    if (!privateKey.trim()) {
        showError('sign-result', 'Please provide your private key');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('private_key', privateKey);
    
    const loader = document.getElementById('sign-loader');
    const result = document.getElementById('sign-result');
    
    loader.style.display = 'block';
    result.style.display = 'none';
    
    try {
        const response = await fetch('/api/sign', {method: 'POST', body: formData});
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('sign-output').value = data.signature;
            result.classList.remove('error');
            result.classList.add('success');
            result.style.display = 'block';
        } else {
            showError('sign-result', data.error);
        }
    } catch (err) {
        showError('sign-result', err.message);
    } finally {
        loader.style.display = 'none';
    }
}

async function verifyFile() {
    const file = document.getElementById('verify-file').files[0];
    const signature = document.getElementById('verify-signature').value;
    const publicKey = document.getElementById('verify-public-key').value;
    
    if (!file) {
        showError('verify-result', 'Please select a file');
        return;
    }
    if (!signature.trim()) {
        showError('verify-result', 'Please provide the signature');
        return;
    }
    if (!publicKey.trim()) {
        showError('verify-result', 'Please provide sender public key');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('signature', signature);
    formData.append('public_key', publicKey);
    
    const loader = document.getElementById('verify-loader');
    const result = document.getElementById('verify-result');
    
    loader.style.display = 'block';
    result.style.display = 'none';
    
    try {
        const response = await fetch('/api/verify', {method: 'POST', body: formData});
        const data = await response.json();
        
        if (data.success) {
            const msgEl = document.getElementById('verify-message');
            msgEl.textContent = data.message;
            msgEl.style.color = data.valid ? '#155724' : '#721c24';
            result.classList.remove('error');
            result.classList.add(data.valid ? 'success' : 'error');
            result.style.display = 'block';
        } else {
            showError('verify-result', data.error);
        }
    } catch (err) {
        showError('verify-result', err.message);
    } finally {
        loader.style.display = 'none';
    }
}

// Utility functions
function showError(resultId, message) {
    const result = document.getElementById(resultId);
    result.innerHTML = '<strong style="color: #721c24;">Error: ' + message + '</strong>';
    result.classList.remove('success');
    result.classList.add('error');
    result.style.display = 'block';
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    document.execCommand('copy');
    alert('Copied to clipboard!');
}

function downloadKey(elementId, filename) {
    const element = document.getElementById(elementId);
    const content = element.value;
    const blob = new Blob([content], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadDecryptedFile() {
    if (!window.decryptedContent) {
        alert('No decrypted content available. Please decrypt a file first.');
        return;
    }
    const filename = window.decryptedFilename || 'decrypted.txt';
    
    // Handle both text and binary content
    let blob;
    if (window.isDecryptedBinary) {
        // Binary file - create blob from Uint8Array
        blob = new Blob([window.decryptedContent], {type: 'application/octet-stream'});
    } else {
        // Text file - create blob from string
        blob = new Blob([window.decryptedContent], {type: 'text/plain'});
    }
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}