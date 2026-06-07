import base64
import json
import zlib

from Crypto.Cipher import AES

from config import DataPrefixes, EncryptionKeys
from utils import decode_access_key


class DBDDecrypter:
    def __init__(self, access_keys):
        self.access_keys = access_keys

    def decrypt(self, content, version_with_branch):
        if content.startswith(DataPrefixes.CLIENT_DATA):
            return self._decrypt_client_data(content, version_with_branch)

        if content.startswith(DataPrefixes.FULL_PROFILE):
            return self._decrypt_profile(content, version_with_branch)

        if content.startswith(DataPrefixes.ZLIB):
            return self._decompress_zlib(content, version_with_branch)

        if content and not self._is_valid_json(content):
            raise ValueError(
                "Invalid JSON output. Access key may be incorrect or data may be corrupted."
            )

        return content

    @staticmethod
    def _is_valid_json(text):
        if not text.strip():
            return True
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False

    def _decrypt_client_data(self, content, version_with_branch):
        encoded_payload = content[len(DataPrefixes.CLIENT_DATA) :]
        raw_payload = base64.b64decode(encoded_payload)

        slice_length = len(version_with_branch) + 1

        key_id_bytes = raw_payload[:slice_length]
        key_id_bytes = bytes((byte + 1) % 256 for byte in key_id_bytes)

        key_id = key_id_bytes.decode("ascii").replace("\u0001", "")

        access_key = self.access_keys.get(key_id)
        if not access_key:
            raise ValueError(f'Key ID "{key_id}" was not found in access keys.')

        if key_id != version_with_branch:
            raise ValueError(
                f'Expected "{version_with_branch}" but payload was encrypted with "{key_id}".'
            )

        aes_key = decode_access_key(access_key)

        ciphertext = raw_payload[slice_length:]

        return self._decode_aes_payload(ciphertext, aes_key, version_with_branch)

    def _decrypt_profile(self, content, version_with_branch):
        encoded_payload = content[len(DataPrefixes.FULL_PROFILE) :]
        raw_payload = base64.b64decode(encoded_payload)

        return self._decode_aes_payload(
            raw_payload, EncryptionKeys.FULL_PROFILE_AES, version_with_branch
        )

    def _decode_aes_payload(self, ciphertext, aes_key, version_with_branch):
        cipher = AES.new(aes_key, AES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(ciphertext)

        result_bytes = bytearray()

        for byte in decrypted_bytes:
            if byte == 0:
                break
            result_bytes.append((byte + 1) % 256)

        plaintext = result_bytes.decode("ascii")
        return self.decrypt(plaintext, version_with_branch)

    def _decompress_zlib(self, content, version_with_branch):
        encoded_payload = content[len(DataPrefixes.ZLIB) :]
        raw_payload = base64.b64decode(encoded_payload)

        if len(raw_payload) < 4:
            raise ValueError("Invalid zlib payload.")

        size_header = raw_payload[:4]
        expected_size = int.from_bytes(size_header, "little")

        compressed_data = raw_payload[4:]
        inflated_bytes = zlib.decompress(compressed_data)

        if len(inflated_bytes) != expected_size:
            raise ValueError(
                f"Zlib size mismatch. Expected {expected_size}, got {len(inflated_bytes)}."
            )

        plaintext = inflated_bytes.decode("utf-16")
        return self.decrypt(plaintext, version_with_branch)
