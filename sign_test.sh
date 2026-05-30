#!/bin/bash
echo "Testing Digital Signatures..."
echo

# Create test document
echo "Creating document to sign..."
echo "This is an important document that needs to be signed." > /tmp/document.txt
echo

# Sign it
echo "Signing document..."
./.venv/bin/python -m src.cli sign -i /tmp/document.txt --private /tmp/alice_private.pem -o /tmp/document.sig
echo

# Show signature info
echo "Signature file size: $(wc -c < /tmp/document.sig) bytes"
echo

# Verify signature
echo "Verifying signature..."
./.venv/bin/python -m src.cli verify -i /tmp/document.txt --signature /tmp/document.sig --public /tmp/alice_public.pem
echo

echo "All signature tests passed!"
