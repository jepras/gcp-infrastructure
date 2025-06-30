import os
import pytest
from app.services.encryption import generate_key, encrypt_data, decrypt_data

def test_generate_key():
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) > 0

def test_encrypt_decrypt_data():
    key = generate_key()
    original_data = "This is a test string for encryption."
    encrypted_data = encrypt_data(original_data, key)
    decrypted_data = decrypt_data(encrypted_data, key)

    assert encrypted_data != original_data
    assert decrypted_data == original_data

def test_decrypt_invalid_data_raises_error():
    key = generate_key()
    invalid_encrypted_data = "not-a-valid-encrypted-string"
    with pytest.raises(Exception):
        decrypt_data(invalid_encrypted_data, key)
