from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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

from config import DataPrefixes
from utils import version_to_tuple
from core.decrypter import DBDDecrypter
from core.encrypter import DBDEncrypter

# ----------------- Utilities -----------------
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_stylesheet(path):
    with open(resource_path(path), "r", encoding="utf-8") as f:
        stylesheet = f.read()

    image_path = resource_path("images/chevron-down.png").replace("\\", "/")
    stylesheet = stylesheet.replace(
        "url(images/chevron-down.png)", f"url({image_path})"
    )

    return stylesheet


PAYLOAD_PREFIXES = (
    DataPrefixes.CLIENT_DATA,
    DataPrefixes.FULL_PROFILE,
    DataPrefixes.ZLIB,
)


def is_dbd_payload(text):
    return text.startswith(PAYLOAD_PREFIXES)


def extract_dbd_payload(text):
    if not text:
        return text

    payload_start = None

    for prefix in PAYLOAD_PREFIXES:
        index = text.find(prefix)
        if index == -1:
            continue
        payload_start = index if payload_start is None else min(payload_start, index)

    return text[payload_start:] if payload_start is not None else text


def pretty_print_json(text):
    try:
        return json.dumps(json.loads(text), indent=4)
    except json.JSONDecodeError:
        return text


def key_id_to_version_tuple(key_id):
    try:
        version = key_id.split("_", 1)[0]
        return version_to_tuple(version)
    except ValueError:
        return (0, 0, 0)


# ----------------- Enums / State -----------------
class Mode(Enum):
    DECRYPT = "decrypt"
    ENCRYPT = "encrypt"


@dataclass
class LoadedFileState:
    data: str | None = None
    file_path: str | None = None


# ----------------- GUI -----------------
def run_gui(access_keys):
    icon_path = resource_path("icons/app_icon.ico")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))

    window = QWidget()
    window.setWindowTitle("DBD Crypter v3.1.0")
    window.setWindowIcon(QIcon(icon_path))
    window.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowMinimizeButtonHint
        | Qt.WindowType.WindowCloseButtonHint
        | Qt.WindowType.CustomizeWindowHint
    )
    window.setFixedSize(1000, 600)

    # Load QSS Stylesheet
    qss = load_stylesheet("style/styles.qss")
    app.setStyleSheet(qss)

    # State
    loaded_file = LoadedFileState()
    last_run_mode: Mode | None = None
    last_run_input_path: str | None = None
    last_result: str | None = None

    # Crypto
    decrypter = DBDDecrypter(access_keys)
    encrypter = DBDEncrypter(access_keys)

    # ----------------- Layouts -----------------
    main_layout = QHBoxLayout()

    # Control Panel Layout
    control_panel_layout = QVBoxLayout()

    # Mode Group
    mode_group = QGroupBox("Mode")
    decrypt_radio = QRadioButton("Decrypt")
    encrypt_radio = QRadioButton("Encrypt")
    decrypt_radio.setChecked(True)
    mode_layout = QHBoxLayout()
    mode_layout.setSpacing(60)
    mode_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    mode_layout.addWidget(decrypt_radio)
    mode_layout.addWidget(encrypt_radio)
    mode_group.setLayout(mode_layout)
    control_panel_layout.addWidget(mode_group)

    # Input Group
    input_group = QGroupBox("Input")
    input_text_edit = QTextEdit()
    input_layout = QVBoxLayout()
    input_layout.addWidget(input_text_edit)

    # Input Buttons Layout
    load_file_button = QPushButton("Load File")
    clear_file_button = QPushButton("Clear File")
    clear_file_button.setEnabled(False)
    input_buttons_layout = QHBoxLayout()
    input_buttons_layout.addWidget(load_file_button)
    input_buttons_layout.addWidget(clear_file_button)
    input_layout.addLayout(input_buttons_layout)
    input_group.setLayout(input_layout)
    control_panel_layout.addWidget(input_group)

    # Key ID Selection Group
    key_id_selection_group = QGroupBox("Key ID")
    key_id_selection_combo = QComboBox()
    key_id_selection_combo.setEnabled(False)
    key_id_selection_layout = QVBoxLayout()
    key_id_selection_layout.addWidget(key_id_selection_combo)
    key_id_selection_group.setLayout(key_id_selection_layout)
    control_panel_layout.addWidget(key_id_selection_group)

    # Status Group
    status_group = QGroupBox("Status")
    status_log = QTextEdit()
    status_log.setReadOnly(True)
    status_log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    status_log.setObjectName("statusLog")
    status_layout = QVBoxLayout()
    status_layout.addWidget(status_log)
    status_group.setLayout(status_layout)
    control_panel_layout.addWidget(status_group)

    # Run Button Layout
    run_button = QPushButton("Run")
    run_button.setEnabled(False)
    run_button.setFixedWidth(306)
    run_button_layout = QHBoxLayout()
    run_button_layout.setContentsMargins(0, 0, 0, 9)
    run_button_layout.addWidget(run_button)
    control_panel_layout.addSpacing(-8)
    control_panel_layout.addLayout(run_button_layout)

    # Output Group
    output_group = QGroupBox("Output")
    output_text_edit = QTextEdit()
    output_text_edit.setReadOnly(True)
    output_layout = QVBoxLayout()
    output_layout.addWidget(output_text_edit)

    # Output Buttons Layout
    copy_output_button = QPushButton("Copy Output")
    save_output_button = QPushButton("Save Output")
    copy_output_button.setEnabled(False)
    save_output_button.setEnabled(False)
    output_buttons_layout = QHBoxLayout()
    output_buttons_layout.addWidget(copy_output_button)
    output_buttons_layout.addWidget(save_output_button)
    output_layout.addLayout(output_buttons_layout)
    output_group.setLayout(output_layout)

    main_layout.addLayout(control_panel_layout, 1)
    main_layout.addWidget(output_group, 2)

    window.setLayout(main_layout)

    # ----------------- Helpers -----------------
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

    def current_mode():
        return Mode.DECRYPT if decrypt_radio.isChecked() else Mode.ENCRYPT

    def get_input_data():
        if loaded_file.data is not None:
            return loaded_file.data
        return input_text_edit.toPlainText().strip()

    def populate_key_ids():
        key_id_selection_combo.blockSignals(True)

        try:
            key_id_selection_combo.clear()

            key_ids = list(access_keys.keys())
            key_id_selection_combo.addItems(key_ids)

            live_key_ids = [key_id for key_id in key_ids if key_id.endswith("_live")]
            if live_key_ids:
                latest_live_key_id = max(live_key_ids, key=key_id_to_version_tuple)
                index = key_id_selection_combo.findText(latest_live_key_id)
                key_id_selection_combo.setCurrentIndex(index if index >= 0 else 0)
            else:
                key_id_selection_combo.setCurrentIndex(0)

        finally:
            key_id_selection_combo.blockSignals(False)

    def update_ui():
        has_file = loaded_file.data is not None
        has_text = bool(input_text_edit.toPlainText().strip())
        has_output = bool(output_text_edit.toPlainText().strip())
        mode = current_mode()

        input_text_edit.blockSignals(True)
        try:
            if has_file:
                input_text_edit.clear()
                input_text_edit.setEnabled(False)
                input_text_edit.setPlaceholderText(
                    "Input disabled: file already loaded"
                )
            elif mode is Mode.DECRYPT:
                input_text_edit.setEnabled(True)
                input_text_edit.setPlaceholderText("Enter text to decrypt")
            else:  # Mode.ENCRYPT
                input_text_edit.clear()
                input_text_edit.setEnabled(False)
                input_text_edit.setPlaceholderText(
                    "Input disabled: encryption requires a file"
                )
        finally:
            input_text_edit.blockSignals(False)

        ready_to_run = (mode is Mode.DECRYPT and (has_file or has_text)) or (
            mode is Mode.ENCRYPT and has_file
        )

        key_id_selection_combo.setEnabled(ready_to_run)
        run_button.setEnabled(ready_to_run)
        clear_file_button.setEnabled(has_file)

        copy_output_button.setEnabled(has_output)
        save_output_button.setEnabled(has_output)

    # ----------------- Event Handlers -----------------
    def on_load_file():
        file_path, _ = QFileDialog.getOpenFileName(
            window, "Load File", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        mode = current_mode()

        try:
            if mode is Mode.DECRYPT:
                with open(file_path, "rb") as f:
                    raw_bytes = f.read()
                content = raw_bytes.decode("utf-8", errors="replace")

            else:  # Mode.ENCRYPT
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            loaded_file.data = content
            loaded_file.file_path = file_path
            append_status(f"File loaded: {file_path}", QColor("#4caf50"))

        except Exception as e:
            loaded_file.data = None
            loaded_file.file_path = None
            append_status(f"Failed to load file: {e}", QColor("#ff5555"))

        update_ui()

    def on_clear_file():
        loaded_file.data = None
        loaded_file.file_path = None
        append_status("File cleared. Input re-enabled.", QColor("#ffa500"))
        update_ui()

    def on_run_clicked():
        nonlocal last_run_mode, last_run_input_path, last_result

        mode = current_mode()

        key_id = key_id_selection_combo.currentText().strip()
        if not key_id:
            append_status("No key ID selected.", QColor("#ff5555"))
            return

        data = get_input_data()
        action = "Decryption" if mode is Mode.DECRYPT else "Encryption"

        if mode is Mode.ENCRYPT and loaded_file.data is None:
            append_status("Encryption requires a loaded file.", QColor("#ff5555"))
            return

        try:
            if mode is Mode.DECRYPT:
                data = extract_dbd_payload(data)

                if not is_dbd_payload(data):
                    append_status(
                        "Input is already decrypted or is in an invalid format.",
                        QColor("#ff5555"),
                    )
                    return

                result = decrypter.decrypt(data, key_id)

            else:  # Mode.ENCRYPT
                if is_dbd_payload(data):
                    append_status(
                        "Input is already encrypted or is in an invalid format.",
                        QColor("#ff5555"),
                    )
                    return

                try:
                    json.loads(data)
                except json.JSONDecodeError:
                    append_status(
                        "Encryption input must be valid JSON.",
                        QColor("#ff5555"),
                    )
                    return

                result = encrypter.encrypt(data, key_id)

        except Exception as e:
            append_status(f"{action} failed: {e}", QColor("#ff5555"))
            return

        last_result = pretty_print_json(result)
        last_run_mode = mode
        last_run_input_path = loaded_file.file_path

        output_text_edit.setPlainText(last_result)

        append_status(f"{action} completed successfully.", QColor("#4caf50"))

        update_ui()

    def on_copy_output():
        if last_result is None:
            append_status("No output to copy.", QColor("#ff5555"))
            return

        QApplication.clipboard().setText(last_result)
        append_status("Output copied to clipboard.", QColor("#4caf50"))

    def on_save_output():
        if last_run_mode is None or last_result is None:
            append_status("No output to save.", QColor("#ff5555"))
            return

        folder = os.path.join(
            os.getcwd(),
            "Output",
            "Decrypted" if last_run_mode is Mode.DECRYPT else "Encrypted",
        )

        os.makedirs(folder, exist_ok=True)

        filename = (
            os.path.basename(last_run_input_path)
            if last_run_input_path
            else datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + ".json"
        )

        save_path = os.path.join(folder, filename)

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(last_result)

            append_status(f"Output saved: {save_path}", QColor("#4caf50"))

        except Exception as e:
            append_status(f"Save failed: {e}", QColor("#ff5555"))

    # ----------------- Signals -----------------
    load_file_button.clicked.connect(on_load_file)
    clear_file_button.clicked.connect(on_clear_file)

    decrypt_radio.toggled.connect(update_ui)
    encrypt_radio.toggled.connect(update_ui)

    input_text_edit.textChanged.connect(update_ui)

    run_button.clicked.connect(on_run_clicked)
    copy_output_button.clicked.connect(on_copy_output)
    save_output_button.clicked.connect(on_save_output)

    # ----------------- Initial UI State  -----------------
    populate_key_ids()
    update_ui()

    window.show()
    sys.exit(app.exec())
