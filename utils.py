import os
import base64
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Signature import pkcs1_15
from typing import Optional

def generate_aes_key_from_password(password, salt):
    return PBKDF2(password, salt, dkLen=32, count=1000000)  # Tạo khóa AES từ mật khẩu người dùng

def encrypt_with_password(password, plaintext):
    salt = get_random_bytes(16)  # Tạo salt ngẫu nhiên
    key = generate_aes_key_from_password(password, salt) # Tạo khóa AES từ mật khẩu
    iv = get_random_bytes(16)  # Tạo IV ngẫu nhiên
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_text = plaintext + (16 - len(plaintext) % 16) * chr(16 - len(plaintext) % 16)
    ciphertext = cipher.encrypt(padded_text.encode())
    return base64.b64encode(salt + iv + ciphertext).decode() # Mã hóa Base64 cho salt, iv, và ciphertext để dễ lưu trữ

# Hàm giải mã AES (chế độ CBC) sử dụng mật khẩu người dùng
def decrypt_with_password(password, encrypted_data):
    data = base64.b64decode(encrypted_data)
    salt = data[:16]  # Lấy salt
    iv = data[16:32]  # Lấy IV
    ciphertext = data[32:]  # Lấy ciphertext
    key = generate_aes_key_from_password(password, salt)  # Tạo khóa AES từ mật khẩu
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_text = cipher.decrypt(ciphertext).decode()
    padding_length = ord(decrypted_text[-1])
    return decrypted_text[:-padding_length]  # Loại bỏ padding

def generate_keys() -> tuple:
    key = RSA.generate(2048)  # Tạo cặp khóa RSA (khóa riêng và khóa công khai) với kích thước 2048-bit
    private_key = key.export_key()  # Xuất khóa riêng ở định dạng PEM (bytes)
    public_key = key.publickey().export_key()  # Xuất khóa công khai ở định dạng PEM (bytes)
    return private_key, public_key  # Trả về cả hai khóa dưới dạng một tuple

# Chuyển đổi định dạng nhị phân (byte) của các khóa thành dạng có thể đọc được (chuỗi) bằng mã hóa UTF-8.
def serialize_keys(private_key: bytes, public_key: bytes) -> tuple:
    return private_key.decode('utf-8'), public_key.decode('utf-8')

def rsa_encrypt(data: str, public_key: bytes) -> str:
    public_key = RSA.import_key(public_key)  # Chuyển đổi khóa công khai từ định dạng PEM (chuỗi/byte) sang đối tượng khóa RSA
    cipher = PKCS1_OAEP.new(public_key)  # Khởi tạo mã hóa RSA sử dụng đệm OAEP
    encrypted_data = cipher.encrypt(data.encode('utf-8'))  # Mã hóa dữ liệu (chuyển sang bytes)
    return base64.b64encode(encrypted_data).decode('utf-8')  # Mã hóa kết quả dưới dạng base64 và chuyển sang chuỗi

def rsa_decrypt(encrypted_data: str, private_key: bytes) -> str:
    private_key = RSA.import_key(private_key)  # Chuyển đổi khóa riêng sang đối tượng khóa RSA
    cipher = PKCS1_OAEP.new(private_key)  # Khởi tạo mã hóa RSA sử dụng đệm OAEP
    decrypted_data = cipher.decrypt(base64.b64decode(encrypted_data))  # Giải mã base64 và giải mã dữ liệu
    return decrypted_data.decode('utf-8')  # Chuyển đổi dữ liệu đã giải mã từ bytes sang chuỗi

def generate_aes_key() -> bytes:
    return os.urandom(32)  # Generate a 256-bit AES key

def aes_encrypt(data: bytes, aes_key: bytes) -> bytes:
    cipher = AES.new(aes_key, AES.MODE_GCM)  # Tạo mã hóa AES mới ở chế độ GCM (an toàn với xác thực)
    ciphertext, tag = cipher.encrypt_and_digest(data)  # Mã hóa dữ liệu và nhận ciphertext và thẻ xác thực
    return cipher.nonce + tag + ciphertext  # Trả về sự kết hợp của nonce, thẻ xác thực và ciphertext

def encrypt_file(file_path: str, public_key: bytes) -> Optional[bytes]:
    aes_key = generate_aes_key()  # Tạo khóa AES ngẫu nhiên
    try:
        with open(file_path, 'rb') as file:  # Mở tệp tin ở chế độ đọc nhị phân
            file_data = file.read()  # Đọc nội dung của tệp tin

        encrypted_data = aes_encrypt(file_data, aes_key)  # Mã hóa dữ liệu tệp tin sử dụng AES

        # Mã hóa khóa AES sử dụng RSA
        encrypted_aes_key = rsa_encrypt(base64.b64encode(aes_key).decode('utf-8'), public_key)

        # Lưu cả khóa AES mã hóa và dữ liệu mã hóa vào một tệp mới
        with open(file_path + '.enc', 'wb') as encrypted_file:
            encrypted_file.write(encrypted_aes_key.encode('utf-8') + b'\n')  # Lưu khóa AES đã mã hóa
            encrypted_file.write(encrypted_data)  # Lưu dữ liệu tệp tin đã mã hóa

        return encrypted_data
    except Exception as e:
        print(f"Xảy ra lỗi khi mã hóa: {e}")
        return None

def aes_decrypt(encrypted_data: bytes, aes_key: bytes) -> bytes:
    nonce = encrypted_data[:16]  # Trích xuất nonce từ dữ liệu mã hóa
    tag = encrypted_data[16:32]  # Trích xuất thẻ xác thực
    ciphertext = encrypted_data[32:]  # Trích xuất ciphertext thực
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)  # Tạo lại mã hóa AES sử dụng cùng nonce
    return cipher.decrypt_and_verify(ciphertext, tag)  # Giải mã và xác thực dữ liệu

def decrypt_file(encrypted_file_path: str, private_key: bytes) -> Optional[bytes]:
    try:
        with open(encrypted_file_path, 'rb') as encrypted_file:
            encrypted_aes_key = encrypted_file.readline().decode('utf-8').strip()  # Đọc khóa AES đã mã hóa
            encrypted_data = encrypted_file.read()  # Đọc phần còn lại của tệp (dữ liệu mã hóa)

        # Giải mã khóa AES sử dụng RSA
        aes_key = base64.b64decode(rsa_decrypt(encrypted_aes_key, private_key))

        # Giải mã dữ liệu tệp tin sử dụng khóa AES đã giải mã
        return aes_decrypt(encrypted_data, aes_key)
    except Exception as e:
        print(f"Xảy ra lỗi khi giải mã: {e}")
        return None

def create_signature(data: str, private_key: bytes) -> str:
    private_key = RSA.import_key(private_key)
    h = SHA256.new(data.encode('utf-8'))
    signature = pkcs1_15.new(private_key).sign(h)
    return base64.b64encode(signature).decode('utf-8')