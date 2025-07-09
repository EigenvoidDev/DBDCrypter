import base64
import zlib
from Crypto.Cipher import AES

from config import ASSET_ENCRYPTION_PREFIX, ZLIB_COMPRESSION_PREFIX, ACCESS_KEYS


class DBDEncryption:
    @staticmethod
    def encrypt_data(data, branch):
        if not data:
            raise ValueError("Input data cannot be empty.")

        decrypted_key = DBDEncryption.get_decrypted_key(branch)
        cipher = AES.new(decrypted_key, AES.MODE_ECB)

        utf16_le_data = data.encode("utf-16-le")
        compressed_data = zlib.compress(utf16_le_data)
        data_length_le_bytes = len(utf16_le_data).to_bytes(4, byteorder="little")

        encoded_data = DBDEncryption.encode_with_zlib_prefix(
            compressed_data, data_length_le_bytes
        )
        encrypted_data = DBDEncryption.encrypt_with_aes(cipher, encoded_data)

        base64_key_id = DBDEncryption.get_base64_key_id(branch)
        encrypted_content = DBDEncryption.construct_encrypted_content(
            encrypted_data, base64_key_id
        )

        return encrypted_content

    @staticmethod
    def get_decrypted_key(branch):
        access_key = ACCESS_KEYS.get(branch)
        if not access_key:
            raise Exception(f'Access key not found in config for "{branch}" branch.')
        return base64.b64decode(access_key)

    @staticmethod
    def encode_with_zlib_prefix(compressed_data, data_length_le_bytes):
        zlib_compressed_data_with_size_header = data_length_le_bytes + compressed_data
        prefixed_base64_zlib_compressed_data = (
            ZLIB_COMPRESSION_PREFIX.encode()
            + base64.b64encode(zlib_compressed_data_with_size_header)
        )
        padded_encoded_bytes = [
            (byte - 1) for byte in prefixed_base64_zlib_compressed_data
        ]
        while len(padded_encoded_bytes) % 16 != 0:
            padded_encoded_bytes.append(0)
        return bytes(padded_encoded_bytes)

    @staticmethod
    def encrypt_with_aes(cipher, data):
        encrypted_data = cipher.encrypt(data)
        prefixed_encrypted_bytes = b"d\x00" + encrypted_data
        return base64.b64encode(prefixed_encrypted_bytes)

    @staticmethod
    def get_base64_key_id(branch):
        key_id_buffer = bytes((byte - 1) % 256 for byte in branch.encode())
        key_id_buffer = key_id_buffer[:-1]
        return base64.b64encode(key_id_buffer).decode("ascii")

    @staticmethod
    def construct_encrypted_content(encrypted_data, base64_key_id):
        return ASSET_ENCRYPTION_PREFIX + base64_key_id + encrypted_data.decode()