import base64
import json
import zlib

from Crypto.Cipher import AES

from config import (
    ACCESS_KEYS,
    CLIENT_DATA_ENCRYPTION_PREFIX,
    FULL_PROFILE_AES_KEY,
    FULL_PROFILE_ENCRYPTION_PREFIX,
    ZLIB_COMPRESSION_PREFIX,
)


class DBDDecrypter:
    @staticmethod
    def decrypt(content, branch):
        if content.startswith(CLIENT_DATA_ENCRYPTION_PREFIX):
            return DBDDecrypter._decrypt_client_data(content, branch)

        if content.startswith(FULL_PROFILE_ENCRYPTION_PREFIX):
            return DBDDecrypter._decrypt_profile(content, branch)

        if content.startswith(ZLIB_COMPRESSION_PREFIX):
            return DBDDecrypter._decompress_zlib(content, branch)

        if content and not DBDDecrypter._is_valid_json(content):
            raise Exception(
                "Decrypted data is not valid JSON. The access key might be incorrect, or the data may be corrupted"
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
    def _decrypt_client_data(content, branch):
        if not content.startswith(CLIENT_DATA_ENCRYPTION_PREFIX):
            raise Exception(
                f"Content does not start with {CLIENT_DATA_ENCRYPTION_PREFIX}. Decryption cannot proceed"
            )

        payload = content[len(CLIENT_DATA_ENCRYPTION_PREFIX) :]
        raw_payload = base64.b64decode(payload)

        branch_len = len(branch)
        slice_len = 7 + branch_len
        key_id_buffer = raw_payload[:slice_len]
        key_id_buffer = bytes((b + 1) % 256 for b in key_id_buffer)

        cleaned_key_id = key_id_buffer.decode("ascii").replace("\u0001", "")
        access_key = ACCESS_KEYS.get(cleaned_key_id)
        if not access_key:
            raise Exception(f'Key ID "{cleaned_key_id}" not in available access keys')

        decrypted_key = base64.urlsafe_b64decode(access_key)
        decoded_buffer = raw_payload[slice_len:]
        return DBDDecrypter._process_decrypted_data(
            decoded_buffer, decrypted_key, branch
        )

    @staticmethod
    def _decrypt_profile(content, branch):
        if not content.startswith(FULL_PROFILE_ENCRYPTION_PREFIX):
            raise Exception(
                f"Content does not start with {FULL_PROFILE_ENCRYPTION_PREFIX}. Decryption cannot proceed"
            )

        payload = content[len(FULL_PROFILE_ENCRYPTION_PREFIX) :]
        raw_payload = base64.b64decode(payload)
        return DBDDecrypter._process_decrypted_data(
            raw_payload, FULL_PROFILE_AES_KEY, branch
        )

    @staticmethod
    def _process_decrypted_data(buffer, key, branch):
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_buffer = cipher.decrypt(buffer)

        mutable_buffer = bytearray(decrypted_buffer)

        valid_non_padding_bytes = 0
        for i in range(len(mutable_buffer)):
            raw_byte_value = mutable_buffer[i]
            if raw_byte_value != 0:
                offset_byte_value = (raw_byte_value + 1) % 256
                mutable_buffer[i] = offset_byte_value
                valid_non_padding_bytes += 1
            else:
                break

        result_text = bytes(mutable_buffer[:valid_non_padding_bytes]).decode("ascii")
        return DBDDecrypter.decrypt(result_text, branch)

    @staticmethod
    def _decompress_zlib(content, branch):
        if not content.startswith(ZLIB_COMPRESSION_PREFIX):
            raise Exception(
                f"Content does not start with {ZLIB_COMPRESSION_PREFIX}. Decryption cannot proceed"
            )

        payload = content[len(ZLIB_COMPRESSION_PREFIX) :]
        raw_payload = base64.b64decode(payload)

        if len(raw_payload) < 4:
            raise Exception("Raw payload too short for zlib data")

        expected_inflated_size = int.from_bytes(raw_payload[:4], "little")
        inflated_buffer = zlib.decompress(raw_payload[4:])

        if len(inflated_buffer) != expected_inflated_size:
            raise Exception(
                f"Inflated size mismatch: expected {expected_inflated_size} bytes, got {len(inflated_buffer)}"
            )

        result_text = inflated_buffer.decode("utf-16")
        return DBDDecrypter.decrypt(result_text, branch)