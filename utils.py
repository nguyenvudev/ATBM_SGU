

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import os
from typing import Optional

def generate_keys() -> tuple:
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def serialize_keys(private_key: bytes, public_key: bytes) -> tuple:
    return private_key.decode('utf-8'), public_key.decode('utf-8')

def rsa_encrypt(data: str, public_key: bytes) -> str:
    public_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_data = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_data).decode('utf-8')

def rsa_decrypt(encrypted_data: str, private_key: bytes) -> str:
    private_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))
    return decrypted_data.decode('utf-8')

def generate_aes_key() -> bytes:
    return os.urandom(32)  # Generate a 256-bit AES key

def aes_encrypt(data: bytes, aes_key: bytes) -> bytes:
    cipher = AES.new(aes_key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext  # Return nonce, tag, and ciphertext

def encrypt_file(file_path: str, public_key: bytes) -> Optional[bytes]:
    aes_key = generate_aes_key()
    try:
        with open(file_path, 'rb') as file:
            file_data = file.read()

        encrypted_data = aes_encrypt(file_data, aes_key)

        # Encrypt AES key
        encrypted_aes_key = rsa_encrypt(base64.b64encode(aes_key).decode('utf-8'), public_key)

        # Save both encrypted AES key and encrypted data to file
        with open(file_path + '.enc', 'wb') as encrypted_file:
            encrypted_file.write(encrypted_aes_key.encode('utf-8') + b'\n')  # Save AES key
            encrypted_file.write(encrypted_data)  # Save encrypted data

        return encrypted_data
    except Exception as e:
        print(f"An error occurred during encryption: {e}")
        return None


def aes_decrypt(encrypted_data: bytes, aes_key: bytes) -> bytes:  # Return bytes instead of str
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)  # Return decrypted data as bytes

def decrypt_file(encrypted_file_path: str, private_key: bytes) -> Optional[bytes]:
    try:
        with open(encrypted_file_path, 'rb') as encrypted_file:
            # Read the first line for encrypted AES key
            encrypted_aes_key = encrypted_file.readline().decode('utf-8').strip()
            encrypted_data = encrypted_file.read()

        # Decrypt AES key
        aes_key = base64.b64decode(rsa_decrypt(encrypted_aes_key, private_key))

        # Decrypt data
        return aes_decrypt(encrypted_data, aes_key)
    except Exception as e:
        print(f"An error occurred during decryption: {e}")
        return None

def create_signature(data: str, private_key: bytes) -> str:
    private_key = RSA.import_key(private_key)
    h = SHA256.new(data.encode('utf-8'))
    signature = pkcs1_15.new(private_key).sign(h)
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(data: str, signature: str, public_key: bytes) -> bool:
    public_key = RSA.import_key(public_key)
    h = SHA256.new(data.encode('utf-8'))
    try:
        pkcs1_15.new(public_key).verify(h, base64.b64decode(signature))
        return True
    except (ValueError, TypeError):
        return False
