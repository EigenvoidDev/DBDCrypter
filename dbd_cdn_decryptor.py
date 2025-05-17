# Copyright 2025 Eigenvoid
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import base64
import json
import zlib

import tkinter as tk
from tkinter import filedialog
from Crypto.Cipher import AES


class DBDDecryption:
    ASSET_ENCRYPTION_PREFIX = "DbdDAwAC"
    PROFILE_ENCRYPTION_PREFIX = "DbdDAgAC"
    PROFILE_ENCRYPTION_AES_KEY = b"5BCC2D6A95D4DF04A005504E59A9B36E"
    ZLIB_COMPRESSION_PREFIX = "DbdDAQEB"

    ACCESS_KEYS = {
        "8.7.1_qa": "X5RxT0nMZVsIics+QbGFKsDoaCG1UhR7uz9sNGnR3Lk=",
        "8.7.1_stage": "lMRrOn3ZdHj+xTVfdyIsZreKpfyZo4jcj2hvmxI+r+0=",
        "8.7.1_cert": "XzO7cQEHx26OhJR4fj1YBavZMvmXfb6arau64S9L+Fg=",
        "8.7.1_ptb": "qarb+XXU3j2inyfAEEfyY2s9KZop8ngh2+ddrljrQfY=",
        "8.7.1_live": "N+r8gZ47S2ZDQ2nurlp7FbCwe+gB6OtpAftTK9Zf5Cs=",
    }

    @staticmethod
    def decrypt_content(content, branch):
        if content.startswith(DBDDecryption.ASSET_ENCRYPTION_PREFIX):
            return DBDDecryption.decrypt_dbd_asset(content, branch)

        if content.startswith(DBDDecryption.PROFILE_ENCRYPTION_PREFIX):
            return DBDDecryption.decrypt_dbd_profile(content, branch)

        if content.startswith(DBDDecryption.ZLIB_COMPRESSION_PREFIX):
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
        if not content.startswith(DBDDecryption.ASSET_ENCRYPTION_PREFIX):
            raise Exception(
                f"Content does not start with {DBDDecryption.ASSET_ENCRYPTION_PREFIX}. Decryption cannot proceed."
            )

        payload = content[len(DBDDecryption.ASSET_ENCRYPTION_PREFIX) :]
        raw_payload = base64.b64decode(payload)

        branch_length = len(branch)
        slice_length = 7 + branch_length
        key_id_buffer = raw_payload[:slice_length]
        key_id_buffer = bytes((byte + 1) % 256 for byte in key_id_buffer)

        cleaned_key_id = key_id_buffer.decode("ascii").replace("\u0001", "")
        access_key = DBDDecryption.ACCESS_KEYS.get(cleaned_key_id)
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
        if not content.startswith(DBDDecryption.PROFILE_ENCRYPTION_PREFIX):
            raise Exception(
                f"Content does not start with {DBDDecryption.PROFILE_ENCRYPTION_PREFIX}. Decryption cannot proceed."
            )

        payload = content[len(DBDDecryption.PROFILE_ENCRYPTION_PREFIX) :]
        raw_payload = base64.b64decode(payload)
        return DBDDecryption.process_decrypted_data(
            raw_payload, DBDDecryption.PROFILE_ENCRYPTION_AES_KEY, branch
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
        if not content.startswith(DBDDecryption.ZLIB_COMPRESSION_PREFIX):
            raise Exception(
                f"Content does not start with {DBDDecryption.ZLIB_COMPRESSION_PREFIX}. Decryption cannot proceed."
            )

        payload = content[len(DBDDecryption.ZLIB_COMPRESSION_PREFIX) :]
        raw_payload = base64.b64decode(payload)

        if len(raw_payload) < 4:
            raise Exception("Raw payload is too short to contain deflated data.")

        expected_inflated_size = int.from_bytes(raw_payload[:4], byteorder="little")
        inflated_buffer = zlib.decompress(raw_payload[4:])

        if len(inflated_buffer) != expected_inflated_size:
            raise Exception(
                f"Inflated data size mismatch for content: expected {expected_inflated_size} bytes, but received {len(inflated_buffer)} bytes."
            )

        result_text = inflated_buffer.decode("utf-16")
        return DBDDecryption.decrypt_content(result_text, branch)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    while True:
        input_method = input(
            "1: Enter encrypted data manually\n2: Load encrypted data from a file\n\nSelect an input method: "
        ).strip()

        if input_method == "1":
            encrypted_data = input("Enter the encrypted data: ")
            break

        elif input_method == "2":
            file_path = filedialog.askopenfilename(
                title="Select File", filetypes=(("JSON files", "*.json"),)
            )

            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        encrypted_data = f.read()
                    print(f"{file_path} successfully loaded.")
                    break
                except Exception as e:
                    print("Error occurred while trying to open the file:", e)
            else:
                print("No file selected.")

        else:
            print(
                'Invalid file selection. Enter "1" to manually input encrypted data or "2" to load it from a file.'
            )

    branch_input = (
        input("Select a branch (q: QA, s: Stage, c: Cert, p: PTB, l: Live): ")
        .strip()
        .lower()
    )

    branch_map = {"q": "qa", "s": "stage", "c": "cert", "p": "ptb", "l": "live"}

    branch = branch_map.get(branch_input)
    if not branch:
        print("Invalid branch selection.")
    else:
        try:
            decrypted_data = DBDDecryption.decrypt_content(encrypted_data, branch)

            if input_method == "1":
                print(decrypted_data)
            else:
                file_name = os.path.basename(file_path)
                base_name = os.path.splitext(file_name)[0]

                output_dir = os.path.join(os.getcwd(), "Output")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                output_file_path = os.path.join(output_dir, f"{base_name}.json")

                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(decrypted_data)

                print(f"Decrypted data has been saved to {output_file_path}")

        except Exception as e:
            print("Error occurred during decryption:", e)