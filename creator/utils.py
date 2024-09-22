from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import base64


key_password = os.getenv("ENCRYPTION_SECRET", "default_password")

# Constants for encryption
SALT = os.urandom(16)  # Generate a random salt
IV = os.urandom(16)  # Initialization vector for AES

# Key derivation function (KDF) for creating a symmetric key
def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Function to encrypt the data
def encrypt_data(creator_signing_key, stash_id, dweller_id, key_password):
    # Create the plaintext by combining keys and ids
    data_to_encrypt = f'{creator_signing_key}:{stash_id}:{dweller_id}'.encode()

    # Pad the data to make it compatible with block cipher requirements
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data_to_encrypt) + padder.finalize()

    # Derive a key using a password (or you can use any shared secret)
    key = derive_key(key_password, SALT)

    # Initialize AES cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(IV), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Encode the encrypted data as base64 (to store it as a string)
    return base64.b64encode(IV + SALT + encrypted_data).decode()

# Function to decrypt the data
def decrypt_data(encrypted_decryption_key, key_password):
    # Decode the base64 string
    encrypted_data = base64.b64decode(encrypted_decryption_key.encode())

    # Extract the IV, salt, and actual encrypted data
    iv = encrypted_data[:16]
    salt = encrypted_data[16:32]
    encrypted_data = encrypted_data[32:]

    # Derive the key again
    key = derive_key(key_password, salt)

    # Initialize AES cipher for decryption
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt and unpad the data
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    # Decode the decrypted data
    return decrypted_data.decode()

# # Example usage
# creator_signing_key = "creator_signing_key_123"
# stash_id = "stash_id_123"
# dweller_id = "dweller_id_123"
# key_password = "secure_shared_password"

# # Encrypt the data
# encrypted_decryption_key = encrypt_data(creator_signing_key, stash_id, dweller_id, key_password)
# print(f"Encrypted Decryption Key: {encrypted_decryption_key}")

# # Decrypt the data
# decrypted_data = decrypt_data(encrypted_decryption_key, key_password)
# print(f"Decrypted Data: {decrypted_data}")
