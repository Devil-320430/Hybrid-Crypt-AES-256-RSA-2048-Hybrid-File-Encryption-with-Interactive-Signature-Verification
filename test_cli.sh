#!/usr/bin/env bash
# Test CLI functionality

echo "Testing keygen..."
./.venv/bin/python -m src.cli keygen --private /tmp/alice_private.pem --public /tmp/alice_public.pem
echo "Keygen completed"
echo

# Create test file
echo "Creating test file..."
echo "This is a secret message!" > /tmp/secret.txt
echo

# Test encrypt
echo "Testing encrypt..."
./.venv/bin/python -m src.cli encrypt -i /tmp/secret.txt -r /tmp/alice_public.pem -o /tmp/secret.encrypted
echo "Encrypt completed"
echo

# Test info
echo "Testing info..."
./.venv/bin/python -m src.cli info -i /tmp/secret.encrypted
echo

# Test decrypt
echo "Testing decrypt..."
./.venv/bin/python -m src.cli decrypt -i /tmp/secret.encrypted -r /tmp/alice_private.pem -o /tmp/secret_decrypted.txt
echo "Decrypt completed"
echo

# Verify
echo "Verifying decryption..."
echo "Original:"
cat /tmp/secret.txt
echo
echo "Decrypted:"
cat /tmp/secret_decrypted.txt
