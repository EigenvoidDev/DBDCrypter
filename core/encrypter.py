import base64
import zlib

from Crypto.Cipher import AES

from config import DataPrefixes
from utils import decode_access_key


class DBDEncrypter:
    def __init__(self, access_keys):
        self.access_keys = access_keys

    def encrypt(self, plaintext, version_with_branch):
        if not plaintext:
            raise ValueError("Input data is empty.")

        aes_key = self._get_aes_key(version_with_branch)
        cipher = AES.new(aes_key, AES.MODE_ECB)

        utf16_bytes = plaintext.encode("utf-16-le")
        compressed_bytes = zlib.compress(utf16_bytes)
        size_header = len(utf16_bytes).to_bytes(4, "little")

        encoded_payload = self._prepare_zlib_payload(compressed_bytes, size_header)
        ciphertext = self._encrypt_with_aes(cipher, encoded_payload)
        key_id = self._derive_key_id(version_with_branch)

        return self._build_encrypted_payload(ciphertext, key_id)

    def _get_aes_key(self, version_with_branch):
        access_key = self.access_keys.get(version_with_branch)

        if not access_key:
            raise ValueError(f'Access key not found for "{version_with_branch}".')

        return decode_access_key(access_key)

    @staticmethod
    def _prepare_zlib_payload(compressed_bytes, size_header):
        combined_bytes = size_header + compressed_bytes
        prefixed_bytes = DataPrefixes.ZLIB.encode() + base64.b64encode(combined_bytes)

        shifted_bytes = bytearray((byte - 1) % 256 for byte in prefixed_bytes)

        while len(shifted_bytes) % 16 != 0:
            shifted_bytes.append(0)

        return bytes(shifted_bytes)

    @staticmethod
    def _encrypt_with_aes(cipher, data):
        return cipher.encrypt(data)

    @staticmethod
    def _derive_key_id(version_with_branch):
        return bytes((byte - 1) % 256 for byte in version_with_branch.encode())

    def _build_encrypted_payload(self, ciphertext, key_id):
        payload = key_id + b"\x00" + ciphertext
        encoded_payload = base64.b64encode(payload).decode("ascii")
        return DataPrefixes.CLIENT_DATA + encoded_payload
