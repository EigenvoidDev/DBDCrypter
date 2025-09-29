import base64
import zlib

from Crypto.Cipher import AES

from config import ACCESS_KEYS, CLIENT_DATA_ENCRYPTION_PREFIX, ZLIB_COMPRESSION_PREFIX


class DBDEncrypter:
    @staticmethod
    def encrypt(data, branch):
        if not data:
            raise ValueError("Input data cannot be empty")

        decrypted_key = DBDEncrypter._get_decrypted_key(branch)
        cipher = AES.new(decrypted_key, AES.MODE_ECB)

        utf16_data = data.encode("utf-16-le")
        compressed = zlib.compress(utf16_data)
        size_header = len(utf16_data).to_bytes(4, "little")

        encoded = DBDEncrypter._encode_with_zlib_prefix(compressed, size_header)
        encrypted = DBDEncrypter._encrypt_with_aes(cipher, encoded)
        key_id = DBDEncrypter._make_key_id(branch)
        encrypted_content = DBDEncrypter._assemble_encrypted_content(encrypted, key_id)

        return encrypted_content

    @staticmethod
    def _get_decrypted_key(branch):
        access_key = ACCESS_KEYS.get(branch)
        if not access_key:
            raise Exception(f'Access key not found for branch "{branch}"')
        return base64.b64decode(access_key)

    @staticmethod
    def _encode_with_zlib_prefix(compressed, size_header):
        combined = size_header + compressed
        prefixed = ZLIB_COMPRESSION_PREFIX.encode() + base64.b64encode(combined)
        shifted_bytes = [(b - 1) for b in prefixed]
        while len(shifted_bytes) % 16 != 0:
            shifted_bytes.append(0)
        return bytes(shifted_bytes)

    @staticmethod
    def _encrypt_with_aes(cipher, data):
        encrypted = cipher.encrypt(data)
        base64_raw = b"d\x00" + encrypted
        return base64.b64encode(base64_raw)

    @staticmethod
    def _make_key_id(branch):
        key_id_buffer = bytes((b - 1) % 256 for b in branch.encode())
        key_id_buffer = key_id_buffer[:-1]
        return base64.b64encode(key_id_buffer).decode("ascii")

    @staticmethod
    def _assemble_encrypted_content(encrypted, key_id):
        return CLIENT_DATA_ENCRYPTION_PREFIX + key_id + encrypted.decode()