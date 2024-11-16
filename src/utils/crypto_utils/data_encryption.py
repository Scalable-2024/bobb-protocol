
# utils/crypto_utils/data_encryption.py
import os
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from src.utils.crypto_utils import read_private_key, read_public_key

# Default chunk size in bytes (configurable)
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 MB

# Derive shared key function
def derive_shared_key(private_key_filename: str, peer_public_key_filename: str) -> bytes:
    """Reads keys from files and creates a shared key."""
    # Read private and public keys using the functions from key_management.py
    private_key = read_private_key(private_key_filename)
    peer_public_key = read_public_key(peer_public_key_filename)

    # Create shared key using the private and public keys
    return create_shared_key(private_key, peer_public_key)
    
def create_shared_key(private_key: x25519.X25519PrivateKey, peer_public_key: x25519.X25519PublicKey) -> bytes:
    """Creates a shared key using ECDH and derives a symmetric AES key."""
    # Perform the key exchange using the private and public keys
    shared_secret = private_key.exchange(peer_public_key)

    # Use HKDF to derive a 256-bit AES key from the shared secret
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"handshake data",
    ).derive(shared_secret)

    return derived_key

# Encrypt data function
def encrypt_data(data: bytes, key: bytes) -> bytes:
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted_data = aesgcm.encrypt(iv, data, None)
    return iv + encrypted_data

# Decrypt data function
def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    iv = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ciphertext, None)

# Split file function
def split_file(file_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Splits a file into chunks of a given size."""
    with open(file_path, "rb") as file:
        chunk_id = 0
        while True:
            chunk_data = file.read(chunk_size)
            if not chunk_data:
                break
            yield chunk_id, chunk_data
            chunk_id += 1

# Encrypt a single chunk function
def encrypt_chunk(chunk_data, key):
    """Encrypts a file chunk using AES-GCM and returns encrypted data with IV."""
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted_chunk = aesgcm.encrypt(iv, chunk_data, None)
    return iv, encrypted_chunk  # Return iv and encrypted chunk as a tuple

def decrypt_chunk(iv, encrypted_chunk, key):
    """Decrypts a file chunk using AES-GCM and returns the decrypted data."""
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, encrypted_chunk, None)

# Encrypt and split large file
def encrypt_large_file(file_path, key, output_dir="encrypted_chunks", chunk_size=DEFAULT_CHUNK_SIZE):
    """Splits, encrypts, and saves a large file in chunks."""
    os.makedirs(output_dir, exist_ok=True)
    for chunk_id, chunk_data in split_file(file_path, chunk_size):
        iv, encrypted_chunk = encrypt_chunk(chunk_data, key)  # Unpack iv and encrypted_chunk from encrypt_chunk
        chunk_filename = os.path.join(output_dir, f"chunk_{chunk_id}.enc")
        with open(chunk_filename, "wb") as chunk_file:
            chunk_file.write(iv + encrypted_chunk)  # Combine iv and encrypted data as a byte sequence
        print(f"Chunk {chunk_id} encrypted and saved to {chunk_filename}.")
        
def reassemble_file_from_chunks(output_file, chunk_dir, key):
    """Takes an array of encrypted chunks and reconstructs the original file by decrypting each chunk, ordered by chunk_id."""
    # Sort encrypted_chunks by chunk_id to ensure correct order
    encrypted_chunks = sorted(os.listdir(chunk_dir), key=lambda x: int(x.split('_')[1].split('.')[0]))
    
    with open(output_file, "wb") as file:
        for chunk_file_name in encrypted_chunks:
            chunk_path = os.path.join(chunk_dir, chunk_file_name)
            with open(chunk_path, "rb") as chunk_file:
                iv = chunk_file.read(12)  # Read the IV first
                encrypted_chunk = chunk_file.read()  # Read the remaining encrypted data
                decrypted_chunk = decrypt_chunk(iv, encrypted_chunk, key)  # Pass both iv and encrypted_chunk
                file.write(decrypted_chunk)
    print(f"File successfully reconstructed and saved as {output_file}")

def encrypt_file_to_array(file_path, key, chunk_size=DEFAULT_CHUNK_SIZE):
    """Encrypts a file into chunks and returns an array with each chunk's encrypted data, IV, and chunk number."""
    encrypted_chunks = []
    with open(file_path, "rb") as file:
        chunk_id = 0
        while True:
            chunk_data = file.read(chunk_size)
            if not chunk_data:
                break
            iv, encrypted_chunk = encrypt_chunk(chunk_data, key)
            encrypted_chunks.append({"chunk_id": chunk_id, "iv": iv, "data": encrypted_chunk})
            chunk_id += 1
    return encrypted_chunks

def reconstruct_file_from_array(encrypted_chunks, output_file, key):
    """Takes an array of encrypted chunks and reconstructs the original file by decrypting each chunk, ordered by chunk_id."""
    # Sort encrypted_chunks by chunk_id to ensure correct order
    encrypted_chunks = sorted(encrypted_chunks, key=lambda x: x["chunk_id"])
    
    with open(output_file, "wb") as file:
        for chunk in encrypted_chunks:
            decrypted_chunk = decrypt_chunk(chunk["iv"], chunk["data"], key)
            file.write(decrypted_chunk)
    print(f"File successfully reconstructed and saved as {output_file}")
