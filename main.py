import os
import tkinter as tk
from tkinter import filedialog

from crypter.decryption import DBDDecryption
from crypter.encryption import DBDEncryption


def get_encrypted_data():
    root = tk.Tk()
    root.withdraw()

    while True:
        input_method = input(
            "\nSelect an input method:\n1: Enter encrypted data manually\n2: Load encrypted data from a file\n\n"
        ).strip()

        if input_method == "1":
            encrypted_data = input("\nEnter the encrypted data: ")
            return encrypted_data, None

        elif input_method == "2":
            file_path = filedialog.askopenfilename(
                title="Select File", filetypes=(("JSON files", "*.json"),)
            )

            if file_path:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        encrypted_data = f.read()
                    print(f"{file_path} successfully loaded.")
                    return encrypted_data, file_path
                except Exception as e:
                    print("Error opening file:", e)
            else:
                print("No file selected.")

        else:
            print('\nInvalid selection. Enter "1" or "2".')


def get_decrypted_data():
    root = tk.Tk()
    root.withdraw()

    while True:
        file_path = filedialog.askopenfilename(
            title="Select File", filetypes=(("JSON files", "*.json"),)
        )

        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    decrypted_data = f.read()
                    print(f"{file_path} successfully loaded.")
                    return decrypted_data, file_path
            except Exception as e:
                print("Error opening file:", e)
        else:
            print("No file selected.")


def get_branch():
    branch_map = {"q": "qa", "s": "stage", "c": "cert", "p": "ptb", "l": "live"}

    while True:
        branch_input = (
            input("Select a branch (q: QA, s: Stage, c: Cert, p: PTB, l: Live): ")
            .strip()
            .lower()
        )

        branch = branch_map.get(branch_input)
        if branch:
            return branch
        else:
            print('\nInvalid branch selection. Enter "q", "s", "c", "p", or "l".')


def get_versioned_branch():
    while True:
        versioned_branch = input(
            "Enter the versioned branch (e.g., 9.0.2_live): "
        ).strip()
        if versioned_branch:
            return versioned_branch
        else:
            print("Invalid input. Enter the versioned branch.")


def save_output(data, file_path, mode):
    file_name = os.path.basename(file_path)
    base_name = os.path.splitext(file_name)[0]

    output_dir = os.path.join(os.getcwd(), "Output", mode.capitalize())
    os.makedirs(output_dir, exist_ok=True)

    output_file_path = os.path.join(output_dir, f"{base_name}.json")
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(data)

    print(f"Output saved to {output_file_path}")


def main():
    while True:
        mode = input("Select mode:\n1: Decrypt\n2: Encrypt\n\n")
        if mode in ("1", "2"):
            break
        else:
            print('Invalid selection. Enter "1" or "2".')

    if mode == "1":
        encrypted_data, file_path = get_encrypted_data()
        branch = get_branch()
        try:
            decrypted_data = DBDDecryption.decrypt_content(encrypted_data, branch)
            if file_path:
                save_output(decrypted_data, file_path, mode="decrypted")
            else:
                print("\n--- Decrypted Output ---\n")
                print(decrypted_data)
        except Exception as e:
            print("Error occurred during decryption:", e)

    else:
        decrypted_data, file_path = get_decrypted_data()
        versioned_branch = get_versioned_branch()
        try:
            encrypted_content = DBDEncryption.encrypt_data(
                decrypted_data, versioned_branch
            )
            save_output(encrypted_content, file_path, mode="encrypted")
        except Exception as e:
            print("Error occurred during encryption:", e)


if __name__ == "__main__":
    main()