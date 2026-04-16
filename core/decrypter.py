import base64
import json
import zlib

from Crypto.Cipher import AES

from config import DataPrefixes, EncryptionKeys


class DBDDecrypter:
    def __init__(self, access_keys):
        self.access_keys = access_keys

    def decrypt(self, content, branch):
        if content.startswith(DataPrefixes.CLIENT_DATA):
            return self._decrypt_client_data(content, branch)

        if content.startswith(DataPrefixes.FULL_PROFILE):
            return self._decrypt_profile(content, branch)

        if content.startswith(DataPrefixes.ZLIB):
            return self._decompress_zlib(content, branch)

        if content and not self._is_valid_json(content):
            raise ValueError(
                "Decrypted data is not valid JSON. The access key may be incorrect or the data may be corrupted."
            )

        return content

    @staticmethod
    def _is_valid_json(string):
        if not string.strip():
            return True
        try:
            json.loads(string)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def _decode_access_key(access_key):
        if any(c in access_key for c in "-_"):
            return base64.urlsafe_b64decode(access_key)
        return base64.b64decode(access_key)

    def _decrypt_client_data(self, content, branch):
        payload = content[len(DataPrefixes.CLIENT_DATA) :]
        raw_payload = base64.b64decode(payload)

        branch_len = len(branch)
        slice_len = 7 + branch_len

        key_id_buffer = raw_payload[:slice_len]
        key_id_buffer = bytes((byte + 1) % 256 for byte in key_id_buffer)

        cleaned_key_id = key_id_buffer.decode("ascii").replace("\u0001", "")
        access_key = self.access_keys.get(cleaned_key_id)

        if not access_key:
            raise ValueError(f'Key ID "{cleaned_key_id}" not found in access keys.')

        decrypted_key = self._decode_access_key(access_key)
        decoded_buffer = raw_payload[slice_len:]

        return self._decode_aes_payload(decoded_buffer, decrypted_key, branch)

    def _decrypt_profile(self, content, branch):
        payload = content[len(DataPrefixes.FULL_PROFILE) :]
        raw_payload = base64.b64decode(payload)

        return self._decode_aes_payload(
            raw_payload, EncryptionKeys.FULL_PROFILE_AES, branch
        )

    def _decode_aes_payload(self, buffer, key, branch):
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(buffer)

        result = bytearray()

        for byte in decrypted:
            if byte == 0:
                break
            result.append((byte + 1) % 256)

        text = result.decode("ascii")
        return self.decrypt(text, branch)

    def _decompress_zlib(self, content, branch):
        payload = content[len(DataPrefixes.ZLIB) :]
        raw_payload = base64.b64decode(payload)

        if len(raw_payload) < 4:
            raise ValueError("Raw payload too short for zlib data.")

        expected_size = int.from_bytes(raw_payload[:4], "little")
        inflated_buffer = zlib.decompress(raw_payload[4:])

        if len(inflated_buffer) != expected_size:
            raise ValueError(
                f"Inflated size mismatch: expected {expected_size}, got {len(inflated_buffer)}."
            )

        text = inflated_buffer.decode("utf-16")
        return self.decrypt(text, branch)
