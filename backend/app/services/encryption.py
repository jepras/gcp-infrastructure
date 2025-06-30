from cryptography.fernet import Fernet
import os

def generate_key():
    """Generates a Fernet key."""
    return Fernet.generate_key().decode()

def encrypt_data(data: str, key: str) -> str:
    """Encrypts a string using Fernet encryption."""
    f = Fernet(key.encode())
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_data: str, key: str) -> str:
    """Decrypts a string using Fernet encryption."""
    f = Fernet(key.encode())
    decrypted_data = f.decrypt(encrypted_data.encode())
    return decrypted_data.decode()
