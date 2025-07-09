import base64
import json
import zlib
from Crypto.Cipher import AES

from config import (
    ASSET_ENCRYPTION_PREFIX,
    PROFILE_ENCRYPTION_PREFIX,
    PROFILE_ENCRYPTION_AES_KEY,
    ZLIB_COMPRESSION_PREFIX,
    ACCESS_KEYS,
)


class DBDDecryption:
    @staticmethod
    def decrypt_content(content, branch):
        if content.startswith(ASSET_ENCRYPTION_PREFIX):
            return DBDDecryption.decrypt_dbd_asset(content, branch)

        if content.startswith(PROFILE_ENCRYPTION_PREFIX):
            return DBDDecryption.decrypt_dbd_profile(content, branch)

        if content.startswith(ZLIB_COMPRESSION_PREFIX):
            return DBDDecryption.decompress_dbd_zlib(content, branch)

        if content and not DBDDecryption.is_valid_json(content):
            raise Exception(
                "Decrypted data is not valid JSON. The access key might be incorrect, or the data could be corrupted."
            )

        return content

    @staticmethod
    def is_valid_json(input_string):
        if not input_string.strip():
            return True
        try:
            json.loads(input_string)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def decrypt_dbd_asset(content, branch):
        if not content.startswith(ASSET_ENCRYPTION_PREFIX):
            raise Exception(
                f"Content does not start with {ASSET_ENCRYPTION_PREFIX}. Decryption cannot proceed."
            )

        payload = content[len(ASSET_ENCRYPTION_PREFIX) :]
        raw_payload = base64.b64decode(payload)

        branch_length = len(branch)
        slice_length = 7 + branch_length
        key_id_buffer = raw_payload[:slice_length]
        key_id_buffer = bytes((byte + 1) % 256 for byte in key_id_buffer)

        cleaned_key_id = key_id_buffer.decode("ascii").replace("\u0001", "")
        access_key = ACCESS_KEYS.get(cleaned_key_id)
        if not access_key:
            raise Exception(
                f'The key ID "{cleaned_key_id}" does not exist in the list of available access keys.'
            )

        decrypted_key = base64.b64decode(access_key)
        if not decrypted_key:
            raise Exception(f'Unknown AES key: "{cleaned_key_id}"')

        decoded_buffer = raw_payload[slice_length:]
        return DBDDecryption.process_decrypted_data(
            decoded_buffer, decrypted_key, branch
        )

    @staticmethod
    def decrypt_dbd_profile(content, branch):
        if not content.startswith(PROFILE_ENCRYPTION_PREFIX):
            raise Exception(
                f"Content does not start with {PROFILE_ENCRYPTION_PREFIX}. Decryption cannot proceed."
            )

        payload = content[len(PROFILE_ENCRYPTION_PREFIX) :]
        raw_payload = base64.b64decode(payload)
        return DBDDecryption.process_decrypted_data(
            raw_payload, PROFILE_ENCRYPTION_AES_KEY, branch
        )

    @staticmethod
    def process_decrypted_data(buffer, encryption_key, branch):
        cipher = AES.new(encryption_key, AES.MODE_ECB)
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
        return DBDDecryption.decrypt_content(result_text, branch)

    @staticmethod
    def decompress_dbd_zlib(content, branch):
        if not content.startswith(ZLIB_COMPRESSION_PREFIX):
            raise Exception(
                f"Content does not start with {ZLIB_COMPRESSION_PREFIX}. Decryption cannot proceed."
            )

        payload = content[len(ZLIB_COMPRESSION_PREFIX) :]
        raw_payload = base64.b64decode(payload)

        if len(raw_payload) < 4:
            raise Exception("Raw payload is too short to contain deflated data.")

        expected_inflated_size = int.from_bytes(raw_payload[:4], byteorder="little")
        inflated_buffer = zlib.decompress(raw_payload[4:])

        if len(inflated_buffer) != expected_inflated_size:
            raise Exception(
                f"Inflated data size mismatch: expected {expected_inflated_size} bytes, got {len(inflated_buffer)} bytes."
            )

        result_text = inflated_buffer.decode("utf-16")
        return DBDDecryption.decrypt_content(result_text, branch)