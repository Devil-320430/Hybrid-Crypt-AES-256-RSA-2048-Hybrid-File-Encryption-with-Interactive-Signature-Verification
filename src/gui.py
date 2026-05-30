#!/usr/bin/env python3
"""Simple Tkinter GUI for the Hybrid Cryptosystem

Run with:
    python -m src.gui

Provides buttons to generate keys, encrypt/decrypt files, sign/verify.

Features:
- Interactive signature verification (auto-detects signed files)
- Shows file signature status
- Prompts for verification when needed
- Clear error messages for tampering and verification failures
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import sys
from pathlib import Path as _Path

try:
    from src.asymmetric import AsymmetricCrypto
    from src.hybrid import HybridEncryptor
    from src.signature import DigitalSignature
except Exception:
    # Support running as a script (python src/gui.py) where 'src' is not a package on sys.path
    project_root = _Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    from src.asymmetric import AsymmetricCrypto
    from src.hybrid import HybridEncryptor
    from src.signature import DigitalSignature


class CryptoGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hybrid Cryptosystem - GUI (with Interactive Signature Verification)")
        self.geometry("1500x900")

        # --- Key generation ---
        key_frame = tk.LabelFrame(self, text="Key Management", padx=8, pady=8)
        key_frame.pack(fill="x", padx=10, pady=6)

        tk.Button(key_frame, text="Generate RSA Key Pair", command=self.generate_keys).pack(side="left")

        # --- Encrypt / Decrypt ---
        io_frame = tk.LabelFrame(self, text="Encryption / Decryption", padx=8, pady=8)
        io_frame.pack(fill="both", expand=True, padx=10, pady=6)

        # Encrypt widgets
        enc_sub = tk.LabelFrame(io_frame, text="Encrypt", padx=6, pady=6)
        enc_sub.pack(fill="x", padx=6, pady=4)

        self.enc_input_var = tk.StringVar()
        tk.Entry(enc_sub, textvariable=self.enc_input_var, width=60).pack(side="left", padx=4)
        tk.Button(enc_sub, text="Select File", command=self.select_enc_file).pack(side="left")
        tk.Button(enc_sub, text="Select Recipient Public Key", command=self.select_recipient_pub).pack(side="left", padx=6)
        self.recipient_pub_path = None

        enc_opts = tk.Frame(enc_sub)
        enc_opts.pack(fill="x", pady=6)
        self.sign_var = tk.BooleanVar(value=False)
        tk.Checkbutton(enc_opts, text="Sign with sender private key", variable=self.sign_var).pack(side="left")
        tk.Button(enc_opts, text="Select Sender Private Key", command=self.select_sender_priv).pack(side="left", padx=6)
        self.sender_priv_path = None
        tk.Button(enc_opts, text="Encrypt", command=self.encrypt_action).pack(side="right")

        # Decrypt widgets
        dec_sub = tk.LabelFrame(io_frame, text="Decrypt", padx=6, pady=6)
        dec_sub.pack(fill="x", padx=6, pady=4)

        self.dec_input_var = tk.StringVar()
        tk.Entry(dec_sub, textvariable=self.dec_input_var, width=60).pack(side="left", padx=4)
        tk.Button(dec_sub, text="Select Encrypted File", command=self.select_dec_file).pack(side="left")
        tk.Button(dec_sub, text="Select Recipient Private Key", command=self.select_recipient_priv).pack(side="left", padx=6)
        self.recipient_priv_path = None

        dec_opts = tk.Frame(dec_sub)
        dec_opts.pack(fill="x", pady=6)
        self.verify_var = tk.BooleanVar(value=False)
        tk.Checkbutton(dec_opts, text="Verify sender signature (auto-detects if file is signed)", variable=self.verify_var).pack(side="left")
        tk.Button(dec_opts, text="Select Sender Public Key", command=self.select_sender_pub).pack(side="left", padx=6)
        self.sender_pub_path = None
        
        # Status label for signed files
        self.file_signed_label = tk.Label(dec_opts, text="", fg="blue")
        self.file_signed_label.pack(side="left", padx=10)
        
        tk.Button(dec_opts, text="Decrypt", command=self.decrypt_action).pack(side="right")

        # --- Sign / Verify ---
        sig_frame = tk.LabelFrame(self, text="Sign / Verify", padx=8, pady=8)
        sig_frame.pack(fill="x", padx=10, pady=6)

        sign_row = tk.Frame(sig_frame)
        sign_row.pack(fill="x", pady=4)
        tk.Button(sign_row, text="Select File to Sign", command=self.select_sign_file).pack(side="left")
        self.sign_file_var = tk.StringVar()
        tk.Entry(sign_row, textvariable=self.sign_file_var, width=50).pack(side="left", padx=6)
        tk.Button(sign_row, text="Select Private Key", command=self.select_sign_priv).pack(side="left")
        self.sign_priv_path = None
        tk.Button(sign_row, text="Sign", command=self.sign_action).pack(side="right")

        verify_row = tk.Frame(sig_frame)
        verify_row.pack(fill="x", pady=4)
        tk.Button(verify_row, text="Select File to Verify", command=self.select_verify_file).pack(side="left")
        self.verify_file_var = tk.StringVar()
        tk.Entry(verify_row, textvariable=self.verify_file_var, width=40).pack(side="left", padx=6)
        tk.Button(verify_row, text="Select Signature", command=self.select_signature_file).pack(side="left")
        self.signature_path = None
        tk.Button(verify_row, text="Select Public Key", command=self.select_verify_pub).pack(side="left", padx=6)
        self.verify_pub_path = None
        tk.Button(verify_row, text="Verify", command=self.verify_action).pack(side="right")

        # Status
        self.status_var = tk.StringVar(value="Ready ✓")
        status_frame = tk.Frame(self)
        status_frame.pack(fill="x", padx=10, pady=6)
        tk.Label(status_frame, textvariable=self.status_var, anchor="w", font=("Arial", 10)).pack(side="left", fill="x", expand=True)
        tk.Label(status_frame, text="✨ With interactive signature verification", font=("Arial", 9), fg="green").pack(side="right")

    def set_status(self, text: str):
        self.status_var.set(text)
        self.update_idletasks()

    def generate_keys(self):
        def _gen():
            self.set_status("Generating RSA-2048 key pair...")
            priv, pub = AsymmetricCrypto.generate_key_pair()
            # ask where to save
            p = filedialog.asksaveasfilename(title="Save Private Key", defaultextension=".pem")
            if not p:
                self.set_status("Key generation cancelled")
                return
            AsymmetricCrypto.save_private_key(priv, p)
            pubp = filedialog.asksaveasfilename(title="Save Public Key", defaultextension=".pem")
            if not pubp:
                self.set_status("Key generation cancelled")
                return
            AsymmetricCrypto.save_public_key(pub, pubp)
            self.set_status(f"Keys saved: {p}, {pubp}")

        threading.Thread(target=_gen, daemon=True).start()

    # --- file selection helpers ---
    def select_enc_file(self):
        p = filedialog.askopenfilename(title="Select file to encrypt")
        if p:
            self.enc_input_var.set(p)

    def select_recipient_pub(self):
        p = filedialog.askopenfilename(title="Select recipient public key (.pem)")
        if p:
            self.recipient_pub_path = p
            self.set_status(f"Recipient pub: {p}")

    def select_sender_priv(self):
        p = filedialog.askopenfilename(title="Select sender private key (.pem)")
        if p:
            self.sender_priv_path = p
            self.set_status(f"Sender priv: {p}")

    def select_dec_file(self):
        p = filedialog.askopenfilename(title="Select encrypted file")
        if p:
            self.dec_input_var.set(p)
            # Check if file is signed and show status
            try:
                file_info = HybridEncryptor.get_encryption_info(p)
                if file_info.get('is_signed'):
                    self.file_signed_label.config(text="✓ File is digitally signed", fg="green")
                else:
                    self.file_signed_label.config(text="", fg="blue")
            except Exception:
                self.file_signed_label.config(text="")
            self.set_status(f"Selected: {Path(p).name}")

    def select_recipient_priv(self):
        p = filedialog.askopenfilename(title="Select recipient private key (.pem)")
        if p:
            self.recipient_priv_path = p
            self.set_status(f"Recipient priv: {p}")

    def select_sender_pub(self):
        p = filedialog.askopenfilename(title="Select sender public key (.pem)")
        if p:
            self.sender_pub_path = p
            self.set_status(f"Sender pub: {p}")

    def select_sign_file(self):
        p = filedialog.askopenfilename(title="Select file to sign")
        if p:
            self.sign_file_var.set(p)

    def select_sign_priv(self):
        p = filedialog.askopenfilename(title="Select private key (.pem)")
        if p:
            self.sign_priv_path = p
            self.set_status(f"Signing priv: {p}")

    def select_verify_file(self):
        p = filedialog.askopenfilename(title="Select file to verify")
        if p:
            self.verify_file_var.set(p)

    def select_signature_file(self):
        p = filedialog.askopenfilename(title="Select signature file")
        if p:
            self.signature_path = p
            self.set_status(f"Signature: {p}")

    def select_verify_pub(self):
        p = filedialog.askopenfilename(title="Select public key (.pem)")
        if p:
            self.verify_pub_path = p
            self.set_status(f"Verify pub: {p}")

    # --- actions ---
    def encrypt_action(self):
        infile = self.enc_input_var.get()
        if not infile:
            messagebox.showwarning("Input required", "Select a file to encrypt")
            return
        if not self.recipient_pub_path:
            messagebox.showwarning("Recipient key", "Select recipient public key")
            return

        out = filedialog.asksaveasfilename(title="Save encrypted file", defaultextension=".encrypted")
        if not out:
            return

        def _enc():
            try:
                self.set_status("Encrypting...")
                recipient_pub = AsymmetricCrypto.load_public_key(self.recipient_pub_path)
                sender_priv = None
                if self.sign_var.get():
                    if not self.sender_priv_path:
                        messagebox.showwarning("Missing key", "Select sender private key to sign")
                        self.set_status("Ready")
                        return
                    sender_priv = AsymmetricCrypto.load_private_key(self.sender_priv_path)

                HybridEncryptor.encrypt_file(infile, recipient_pub, sender_private_key=sender_priv, output_file=out, sign=self.sign_var.get())
                self.set_status(f"Encrypted → {out}")
                messagebox.showinfo("Success", f"File encrypted to:\n{out}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.set_status("Error")

        threading.Thread(target=_enc, daemon=True).start()

    def decrypt_action(self):
        infile = self.dec_input_var.get()
        if not infile:
            messagebox.showwarning("Input required", "Select an encrypted file to decrypt")
            return
        if not self.recipient_priv_path:
            messagebox.showwarning("Recipient key", "Select recipient private key")
            return

        # Check if file is signed and ask for verification
        try:
            file_info = HybridEncryptor.get_encryption_info(infile)
            is_signed = file_info.get('is_signed', False)
            
            # If file is signed but user hasn't selected verify or public key, offer to verify
            if is_signed and not self.verify_var.get() and not self.sender_pub_path:
                response = messagebox.askyesno(
                    "Signature Detection",
                    f"This file is digitally signed.\n\n" 
                    f"Original filename: {file_info.get('original_filename', 'Unknown')}\n\n"
                    f"Do you want to verify the sender's signature?"
                )
                if response:
                    # Ask user to select public key
                    pub_key = filedialog.askopenfilename(
                        title="Select sender's public key to verify signature",
                        filetypes=[("PEM files", "*.pem"), ("All files", "*")]
                    )
                    if pub_key:
                        self.sender_pub_path = pub_key
                        self.verify_var.set(True)
        except Exception:
            pass  # File info read error, continue

        out = filedialog.asksaveasfilename(title="Save decrypted file", defaultextension=".dec")
        if not out:
            return

        def _dec():
            try:
                self.set_status("Decrypting...")
                recipient_priv = AsymmetricCrypto.load_private_key(self.recipient_priv_path)
                sender_pub = None
                verify_sig = self.verify_var.get()
                
                if verify_sig:
                    if not self.sender_pub_path:
                        messagebox.showwarning("Missing key", "Select sender public key to verify")
                        self.set_status("Ready")
                        return
                    sender_pub = AsymmetricCrypto.load_public_key(self.sender_pub_path)

                HybridEncryptor.decrypt_file(infile, recipient_priv, sender_public_key=sender_pub, output_file=out, verify_signature=verify_sig)
                
                # Show appropriate success message
                if verify_sig:
                    msg = f"File decrypted to:\n{out}\n\n✅ Signature verified - file is authentic!"
                    self.set_status(f"Decrypted & verified → {out}")
                else:
                    msg = f"File decrypted to:\n{out}"
                    try:
                        if file_info.get('is_signed', False):
                            msg += "\n\n⚠️ Note: This file is signed but signature was not verified"
                    except:
                        pass
                    self.set_status(f"Decrypted → {out}")
                
                messagebox.showinfo("Success", msg)
            except Exception as e:
                error_msg = str(e)
                if "Signature verification failed" in error_msg:
                    messagebox.showerror("Verification Failed", "Signature verification failed!\nFile may be tampered with or wrong public key provided.")
                elif "HMAC verification failed" in error_msg:
                    messagebox.showerror("Integrity Error", "File integrity check failed!\nFile may be corrupted or tampered.")
                else:
                    messagebox.showerror("Error", error_msg)
                self.set_status("Error")

        threading.Thread(target=_dec, daemon=True).start()

    def sign_action(self):
        f = self.sign_file_var.get()
        if not f:
            messagebox.showwarning("Input required", "Select a file to sign")
            return
        if not self.sign_priv_path:
            messagebox.showwarning("Key required", "Select private key to sign with")
            return

        out = filedialog.asksaveasfilename(title="Save signature to", defaultextension=".sig")
        if not out:
            return

        try:
            priv = AsymmetricCrypto.load_private_key(self.sign_priv_path)
            sig = DigitalSignature.sign_file(f, priv)
            with open(out, 'wb') as fh:
                fh.write(sig)
            self.set_status(f"Signature saved → {out}")
            messagebox.showinfo("Signed", f"Signature saved to:\n{out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error")

    def verify_action(self):
        f = self.verify_file_var.get()
        if not f:
            messagebox.showwarning("Input required", "Select a file to verify")
            return
        if not self.signature_path:
            messagebox.showwarning("Signature", "Select signature file")
            return
        if not self.verify_pub_path:
            messagebox.showwarning("Key", "Select public key to verify with")
            return

        try:
            pub = AsymmetricCrypto.load_public_key(self.verify_pub_path)
            with open(self.signature_path, 'rb') as fh:
                sig = fh.read()
            valid = DigitalSignature.verify_signature(f, sig, pub)
            if valid:
                messagebox.showinfo("Valid", "Signature is VALID")
                self.set_status("Signature valid")
            else:
                messagebox.showwarning("Invalid", "Signature is INVALID")
                self.set_status("Signature invalid")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error")


def main():
    app = CryptoGUI()
    app.mainloop()


if __name__ == '__main__':
    main()
