from datetime import datetime
import json
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import (
    CLIENT_DATA_ENCRYPTION_PREFIX,
    DECRYPT_BRANCHES,
    DECRYPT_BRANCH_MAP,
    ENCRYPT_KEYS,
    FULL_PROFILE_ENCRYPTION_PREFIX,
    ZLIB_COMPRESSION_PREFIX,
)
from core.decrypter import DBDDecrypter
from core.encrypter import DBDEncrypter

# ---------------------- Utilities ----------------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_stylesheet(path):
    with open(resource_path(path), "r", encoding="utf-8") as file:
        stylesheet = file.read()

    image_path = resource_path("images/chevron-down.png").replace("\\", "/")
    stylesheet = stylesheet.replace(
        "url(images/chevron-down.png)", f"url({image_path})"
    )

    return stylesheet


def is_encrypted_or_compressed(text):
    return text.startswith(
        (
            CLIENT_DATA_ENCRYPTION_PREFIX,
            FULL_PROFILE_ENCRYPTION_PREFIX,
            ZLIB_COMPRESSION_PREFIX,
        )
    )


def format_json(text):
    try:
        return json.dumps(json.loads(text), indent=4)
    except json.JSONDecodeError:
        return text


# ---------------------- GUI ----------------------
def run_gui():
    icon_path = resource_path("icons/app_icon.ico")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))

    window = QWidget()
    window.setWindowTitle("DBD Crypter v2.1.0")
    window.setWindowIcon(QIcon(icon_path))

    window.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowMinimizeButtonHint
        | Qt.WindowType.WindowCloseButtonHint
        | Qt.WindowType.CustomizeWindowHint
    )

    window.setFixedSize(1000, 600)

    # ---------------- Internal State ----------------
    loaded_file_content = {"data": None}

    # ---------------- QSS Stylesheet ----------------
    qss = load_stylesheet("style/styles.qss")
    app.setStyleSheet(qss)

    # ---------------------- Layouts ----------------------
    main_layout = QVBoxLayout()

    columns_layout = QHBoxLayout()
    left_layout = QVBoxLayout()

    # Mode
    mode_group = QGroupBox("Mode")
    mode_layout = QHBoxLayout()
    mode_layout.addStretch()
    decrypt_radio = QRadioButton("Decrypt")
    encrypt_radio = QRadioButton("Encrypt")
    decrypt_radio.setChecked(True)
    mode_layout.addWidget(decrypt_radio)
    mode_layout.addWidget(encrypt_radio)
    mode_layout.setSpacing(60)
    mode_layout.addStretch()
    mode_group.setLayout(mode_layout)
    left_layout.addWidget(mode_group)

    # Input
    input_group = QGroupBox("Input")
    input_layout = QVBoxLayout()
    input_text = QTextEdit()
    input_layout.addWidget(input_text)

    # Input Buttons
    input_buttons_layout = QHBoxLayout()
    load_file_button = QPushButton("Load File")
    input_buttons_layout.addWidget(load_file_button)

    clear_file_button = QPushButton("Clear File")
    clear_file_button.setEnabled(False)
    input_buttons_layout.addWidget(clear_file_button)

    input_layout.addLayout(input_buttons_layout)
    input_group.setLayout(input_layout)
    left_layout.addWidget(input_group)

    # Target
    target_group = QGroupBox()
    target_layout = QVBoxLayout()
    target_combo = QComboBox()
    target_combo.setEnabled(False)
    target_layout.addWidget(target_combo)
    target_group.setLayout(target_layout)
    left_layout.addWidget(target_group)

    # Status
    status_group = QGroupBox("Status")
    status_layout = QVBoxLayout()
    status_log = QTextEdit()
    status_log.setReadOnly(True)
    status_log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    status_log.setObjectName("statusLog")
    status_layout.addWidget(status_log)
    status_group.setLayout(status_layout)
    left_layout.addWidget(status_group)

    # Run Button
    run_button = QPushButton("Run")
    run_button.setEnabled(False)
    run_button.setFixedWidth(306)

    run_row = QHBoxLayout()
    run_row.setContentsMargins(0, 0, 0, 9)
    run_row.addWidget(run_button)
    left_layout.addSpacing(-8)
    left_layout.addLayout(run_row)

    # Output
    output_group = QGroupBox("Output")
    output_layout = QVBoxLayout()
    output_text = QTextEdit()
    output_text.setReadOnly(True)
    output_layout.addWidget(output_text)

    # Output Buttons
    output_buttons_layout = QHBoxLayout()
    copy_output_button = QPushButton("Copy Output")
    copy_output_button.setEnabled(False)
    output_buttons_layout.addWidget(copy_output_button)

    save_output_button = QPushButton("Save Output")
    save_output_button.setEnabled(False)
    output_buttons_layout.addWidget(save_output_button)

    output_layout.addLayout(output_buttons_layout)
    output_group.setLayout(output_layout)

    columns_layout.addLayout(left_layout, 1)
    columns_layout.addWidget(output_group, 2)

    main_layout.addLayout(columns_layout)

    window.setLayout(main_layout)

    # ---------------- Handlers ----------------
    def append_status(message, color):
        message = str(message).rstrip("\n")
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] "

        cursor = status_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        timestamp_format = QTextCharFormat()
        timestamp_format.setForeground(QColor("#e0e0e0"))
        cursor.insertText(timestamp, timestamp_format)

        message_format = QTextCharFormat()
        message_format.setForeground(color)
        cursor.insertText(message + "\n", message_format)

        status_log.setTextCursor(cursor)
        status_log.ensureCursorVisible()

    def update_ui_state():
        # Block textChanged signals to prevent recursion
        input_text.blockSignals(True)

        # Manage input section
        if loaded_file_content["data"]:
            input_text.clear()
            input_text.setEnabled(False)
            input_text.setPlaceholderText("Input disabled: file already loaded")
        elif decrypt_radio.isChecked():
            input_text.setEnabled(True)
            input_text.setPlaceholderText("Enter text to decrypt")
        else:
            input_text.clear()
            input_text.setEnabled(False)
            input_text.setPlaceholderText("Input disabled: encryption requires a file")

        # Manage target and run buttons
        has_text = bool(input_text.toPlainText().strip())
        has_file = bool(loaded_file_content["data"])
        ready = (has_text or has_file) if decrypt_radio.isChecked() else has_file
        target_combo.setEnabled(ready)
        run_button.setEnabled(ready)

        # Manage clear file button
        clear_file_button.setEnabled(has_file)

        # Re-enable textChanged signals
        input_text.blockSignals(False)

    def update_target_combo():
        target_combo.clear()

        if decrypt_radio.isChecked():
            target_group.setTitle("Branch")
            target_combo.addItems(DECRYPT_BRANCHES)
        else:
            target_group.setTitle("Key ID")
            target_combo.addItems(ENCRYPT_KEYS)

    def load_file():
        file_path, _ = QFileDialog.getOpenFileName(
            window, "Load File", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                loaded_file_content["data"] = content
                loaded_file_content["file_path"] = file_path
                append_status(f"File loaded: {file_path}", QColor("#4caf50"))
            except json.JSONDecodeError:
                append_status(f"Invalid JSON file: {file_path}", QColor("#ff5555"))
                loaded_file_content["data"] = None
                loaded_file_content["file_path"] = None
            except Exception as e:
                append_status(f"Failed to load file: {str(e)}.", QColor("#ff5555"))
                loaded_file_content["data"] = None
                loaded_file_content["file_path"] = None
        update_ui_state()

    def clear_file():
        if loaded_file_content["data"]:
            loaded_file_content["data"] = None
            loaded_file_content["file_path"] = None
            append_status("File cleared, input re-enabled.", QColor("#ffa500"))
        update_ui_state()

    def run_crypto():
        selected_branch_or_key_id = target_combo.currentText()
        is_decrypt = decrypt_radio.isChecked()

        input_data = (
            loaded_file_content["data"]
            if loaded_file_content["data"]
            else input_text.toPlainText().strip()
        )

        if not is_decrypt and not loaded_file_content["data"]:
            append_status("Error: No file loaded for encryption.", QColor("#ff5555"))
            return

        try:
            if is_decrypt:
                # Prevent double decryption or bad input
                if not is_encrypted_or_compressed(input_data):
                    append_status(
                        "Input is already decrypted or in an invalid format.",
                        QColor("#ff5555"),
                    )
                    return

                if selected_branch_or_key_id not in DECRYPT_BRANCH_MAP:
                    append_status(
                        "Invalid branch selected for decryption.", QColor("#ff5555")
                    )
                    return

                branch_code = DECRYPT_BRANCH_MAP[selected_branch_or_key_id]
                result = DBDDecrypter.decrypt(input_data, branch_code)
                append_status("Decryption successful!", QColor("#4caf50"))

            else:
                # Prevent double encryption or bad input
                if is_encrypted_or_compressed(input_data):
                    append_status(
                        "Input is already encrypted or in an invalid format.",
                        QColor("#ff5555"),
                    )
                    return

                result = DBDEncrypter.encrypt(input_data, selected_branch_or_key_id)
                append_status("Encryption successful!", QColor("#4caf50"))

            # Pretty-print JSON if possible
            output_text.setPlainText(format_json(result))

            copy_output_button.setEnabled(True)
            save_output_button.setEnabled(True)

        except Exception as e:
            append_status(f"Error: {str(e)}.", QColor("#ff5555"))

    def copy_output():
        output = output_text.toPlainText().strip()
        if output:
            QApplication.clipboard().setText(output)
            append_status("Output copied to clipboard.", QColor("#4caf50"))

    def save_output():
        output = output_text.toPlainText().strip()
        if not output:
            append_status("No output to save.", QColor("#ff5555"))
            return

        # Determine output folder based on mode
        if decrypt_radio.isChecked():
            folder = os.path.join(os.getcwd(), "Output", "Decrypted")
        else:
            folder = os.path.join(os.getcwd(), "Output", "Encrypted")

        os.makedirs(folder, exist_ok=True)

        # Determine filename
        if loaded_file_content.get("file_path"):
            filename = os.path.basename(loaded_file_content["file_path"])
        else:
            filename = datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + ".json"

        save_path = os.path.join(folder, filename)

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(output)

            append_status(f"Output saved to {save_path}", QColor("#4caf50"))
        except Exception as e:
            append_status(f"Error saving file: {str(e)}.", QColor("#ff5555"))

    # ---------------- Connect Signals ----------------
    load_file_button.clicked.connect(load_file)
    clear_file_button.clicked.connect(clear_file)
    decrypt_radio.toggled.connect(lambda: (update_ui_state(), update_target_combo()))
    encrypt_radio.toggled.connect(lambda: (update_ui_state(), update_target_combo()))
    input_text.textChanged.connect(update_ui_state)
    run_button.clicked.connect(run_crypto)
    copy_output_button.clicked.connect(copy_output)
    save_output_button.clicked.connect(save_output)

    # Initial UI State
    update_ui_state()
    update_target_combo()

    window.show()
    sys.exit(app.exec())