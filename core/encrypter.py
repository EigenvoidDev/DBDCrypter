import base64
import zlib

from Crypto.Cipher import AES

from config import DataPrefixes


class DBDEncrypter:
    def __init__(self, access_keys):
        self.access_keys = access_keys

    def encrypt(self, data, branch):
        if not data:
            raise ValueError("Input data cannot be empty.")

        decrypted_key = self._get_decrypted_key(branch)
        cipher = AES.new(decrypted_key, AES.MODE_ECB)

        utf16_data = data.encode("utf-16-le")
        compressed = zlib.compress(utf16_data)
        size_header = len(utf16_data).to_bytes(4, "little")

        encoded_payload = self._encode_with_zlib_prefix(compressed, size_header)
        encrypted_payload = self._encrypt_with_aes(cipher, encoded_payload)
        key_id = self._generate_key_id(branch)

        return self._build_encrypted_payload(encrypted_payload, key_id)

    @staticmethod
    def _decode_access_key(access_key):
        if any(c in access_key for c in "-_"):
            return base64.urlsafe_b64decode(access_key)
        return base64.b64decode(access_key)

    def _get_decrypted_key(self, branch):
        access_key = self.access_keys.get(branch)

        if not access_key:
            raise ValueError(f'Access key not found for branch "{branch}".')

        return self._decode_access_key(access_key)

    def _encode_with_zlib_prefix(self, compressed, size_header):
        combined = size_header + compressed
        prefixed = DataPrefixes.ZLIB.encode() + base64.b64encode(combined)

        shifted_bytes = bytearray((byte - 1) % 256 for byte in prefixed)

        while len(shifted_bytes) % 16 != 0:
            shifted_bytes.append(0)

        return bytes(shifted_bytes)

    @staticmethod
    def _encrypt_with_aes(cipher, data):
        encrypted = cipher.encrypt(data)
        base64_raw = b"d\x00" + encrypted
        return base64.b64encode(base64_raw)

    @staticmethod
    def _generate_key_id(branch):
        key_id_buffer = bytes((byte - 1) % 256 for byte in branch.encode())
        key_id_buffer = key_id_buffer[:-1]
        return base64.b64encode(key_id_buffer).decode("ascii")

    def _build_encrypted_payload(self, encrypted, key_id):
        return DataPrefixes.CLIENT_DATA + key_id + encrypted.decode()
