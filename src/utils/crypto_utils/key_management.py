# utils/crypto_utils/key_management.py
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

def generate_keys(name: str, key_dir="keys"):
    """Generates an X25519 key pair and saves them as PEM files based on satellite name."""
    os.makedirs(key_dir, exist_ok=True)  # Ensure directory exists
    
    private_key_path = os.path.join(key_dir, f"{name}_private_key.pem")
    public_key_path = os.path.join(key_dir, f"{name}_public_key.pem")

    # Check if either key file already exists
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        print(f"Keys for '{name}' already exist in '{key_dir}' directory")
        return private_key_path, public_key_path

    # Generate X25519 private key
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Save private key to a file
    with open(private_key_path, "wb") as private_file:
        private_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save public key to a file
    with open(public_key_path, "wb") as public_file:
        public_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    
    print(f"Keys for '{name}' generated and saved to '{key_dir}' directory as '{name}_private_key.pem' and '{name}_public_key.pem'")

def read_private_key(private_key_filename: str) -> x25519.X25519PrivateKey:
    """Reads the private key from the specified file."""
    with open(private_key_filename, "rb") as private_file:
        private_key = serialization.load_pem_private_key(
            private_file.read(),
            password=None
        )
    if not isinstance(private_key, x25519.X25519PrivateKey):
        raise ValueError("The private key is not of type X25519.")
    return private_key

def read_public_key(public_key_filename: str) -> x25519.X25519PublicKey:
    """Reads the public key from the specified file."""
    with open(public_key_filename, "rb") as public_file:
        public_key = serialization.load_pem_public_key(public_file.read())
    if not isinstance(public_key, x25519.X25519PublicKey):
        raise ValueError("The public key is not of type X25519.")
    return public_key
