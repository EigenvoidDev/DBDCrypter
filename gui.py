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
    DataPrefixes,
    ENVIRONMENT_BRANCHES,
    ENVIRONMENT_BRANCH_MAP,
)
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


def is_encrypted_or_compressed(text):
    return text.startswith(
        (
            DataPrefixes.CLIENT_DATA,
            DataPrefixes.FULL_PROFILE,
            DataPrefixes.ZLIB,
        )
    )


def format_json(text):
    try:
        return json.dumps(json.loads(text), indent=4)
    except json.JSONDecodeError:
        return text


# ---------------------- GUI ----------------------
def run_gui(access_keys):
    icon_path = resource_path("icons/app_icon.ico")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))

    window = QWidget()
    window.setWindowTitle("DBD Crypter v2.2.0")
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

    # Input State
    loaded_file_content = {"data": None}

    # Output State
    output_metadata = {"mode": None}

    # Crypto
    decrypter = DBDDecrypter(access_keys)
    encrypter = DBDEncrypter(access_keys)

    # ---------------------- Layouts ----------------------
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

    # Selection Group
    selection_group = QGroupBox()
    selection_combo = QComboBox()
    selection_combo.setEnabled(False)
    selection_layout = QVBoxLayout()
    selection_layout.addWidget(selection_combo)
    selection_group.setLayout(selection_layout)
    control_panel_layout.addWidget(selection_group)

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

    # ---------------------- UI Utilities ----------------------
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

    # ---------------------- UI State Management ----------------------
    def update_ui_state():
        input_text_edit.blockSignals(True)

        has_file = bool(loaded_file_content["data"])
        has_text = bool(input_text_edit.toPlainText().strip())
        has_output = bool(output_text_edit.toPlainText().strip())

        if not has_output and output_metadata["mode"] is not None:
            output_metadata["mode"] = None

        if has_file:
            input_text_edit.clear()
            input_text_edit.setEnabled(False)
            input_text_edit.setPlaceholderText("Input disabled: file already loaded")

        elif decrypt_radio.isChecked():
            input_text_edit.setEnabled(True)
            input_text_edit.setPlaceholderText("Enter text to decrypt")

        else:
            input_text_edit.clear()
            input_text_edit.setEnabled(False)
            input_text_edit.setPlaceholderText(
                "Input disabled: encryption requires a file"
            )

        ready = (has_text or has_file) if decrypt_radio.isChecked() else has_file

        selection_combo.setEnabled(ready)
        run_button.setEnabled(ready)
        clear_file_button.setEnabled(has_file)

        copy_output_button.setEnabled(has_output)
        save_output_button.setEnabled(has_output)

        input_text_edit.blockSignals(False)

    def update_selection_options():
        selection_combo.blockSignals(True)
        try:
            selection_combo.clear()

            if decrypt_radio.isChecked():
                selection_group.setTitle("Branch")
                selection_combo.addItems(ENVIRONMENT_BRANCHES)

                index = selection_combo.findText("live", Qt.MatchFlag.MatchFixedString)
                if index >= 0:
                    selection_combo.setCurrentIndex(index)
                else:
                    selection_combo.setCurrentIndex(0)

            else:
                selection_group.setTitle("Key ID")
                keys = list(access_keys.keys())
                selection_combo.addItems(keys)

                live_keys = [key for key in keys if key.endswith("_live")]

                if live_keys:
                    latest_live_key = max(live_keys)
                    index = selection_combo.findText(latest_live_key)
                    if index >= 0:
                        selection_combo.setCurrentIndex(index)
                    else:
                        selection_combo.setCurrentIndex(0)
                else:
                    selection_combo.setCurrentIndex(0)

        finally:
            selection_combo.blockSignals(False)

    # ---------------------- Event Handlers ----------------------
    def on_mode_changed():
        update_ui_state()
        update_selection_options()

    def on_load_file():
        file_path, _ = QFileDialog.getOpenFileName(
            window, "Load File", "", "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            loaded_file_content["data"] = content
            loaded_file_content["file_path"] = file_path

            append_status(f"File loaded: {file_path}", QColor("#4caf50"))

        except json.JSONDecodeError:
            loaded_file_content["data"] = None
            loaded_file_content["file_path"] = None
            append_status(f"Invalid JSON file: {file_path}", QColor("#ff5555"))

        except Exception as e:
            loaded_file_content["data"] = None
            loaded_file_content["file_path"] = None
            append_status(f"Failed to load file: {str(e)}", QColor("#ff5555"))

        update_ui_state()

    def on_clear_file():
        if loaded_file_content["data"]:
            loaded_file_content["data"] = None
            loaded_file_content["file_path"] = None
            append_status("File cleared, input re-enabled.", QColor("#ffa500"))

        update_ui_state()

    def on_run_clicked():
        selection = selection_combo.currentText()
        is_decrypt = decrypt_radio.isChecked()

        file_data = loaded_file_content["data"]
        input_data = file_data if file_data else input_text_edit.toPlainText().strip()

        if not is_decrypt and not file_data:
            append_status(
                "No file loaded. Please load a file to encrypt.", QColor("#ff5555")
            )
            return

        try:
            if is_decrypt:
                if not is_encrypted_or_compressed(input_data):
                    append_status(
                        "Input is already decrypted or in an invalid format.",
                        QColor("#ff5555"),
                    )
                    return

                if selection not in ENVIRONMENT_BRANCH_MAP:
                    append_status("Invalid branch selected.", QColor("#ff5555"))
                    return

                branch = ENVIRONMENT_BRANCH_MAP[selection]
                result = decrypter.decrypt(input_data, branch)
                append_status("Decryption successful!", QColor("#4caf50"))

            else:
                if is_encrypted_or_compressed(input_data):
                    append_status(
                        "Input is already encrypted or in an invalid format.",
                        QColor("#ff5555"),
                    )
                    return

                try:
                    json.loads(input_data)
                except json.JSONDecodeError:
                    append_status(
                        "Encryption input must be valid JSON.",
                        QColor("#ff5555"),
                    )
                    return

                result = encrypter.encrypt(input_data, selection)
                append_status("Encryption successful!", QColor("#4caf50"))

            output_text_edit.setPlainText(format_json(result))

            output_metadata["mode"] = "decrypt" if is_decrypt else "encrypt"

            update_ui_state()

        except Exception as e:
            if is_decrypt:
                append_status(f"Decryption failed: {str(e)}", QColor("#ff5555"))
            else:
                append_status(f"Encryption failed: {str(e)}", QColor("#ff5555"))

    def on_copy_output():
        output = output_text_edit.toPlainText().strip()

        if output:
            QApplication.clipboard().setText(output)
            append_status("Output copied to clipboard.", QColor("#4caf50"))

    def on_save_output():
        output = output_text_edit.toPlainText().strip()

        if not output:
            append_status("No output to save.", QColor("#ff5555"))
            return

        mode = output_metadata.get("mode")

        if mode is None:
            append_status(
                'No output mode recorded. Click "Run" first.', QColor("#ff5555")
            )
            return

        folder = os.path.join(
            os.getcwd(), "Output", "Decrypted" if mode == "decrypt" else "Encrypted"
        )

        os.makedirs(folder, exist_ok=True)

        filename = (
            os.path.basename(loaded_file_content["file_path"])
            if loaded_file_content.get("file_path")
            else datetime.now().strftime("%Y-%m-%dT%H-%M-%S") + ".json"
        )

        save_path = os.path.join(folder, filename)

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(output)

            append_status(f"Output saved to {save_path}", QColor("#4caf50"))

        except Exception as e:
            append_status(f"Save error: {str(e)}", QColor("#ff5555"))

    # ---------------------- Signal Connections ----------------------
    load_file_button.clicked.connect(on_load_file)
    clear_file_button.clicked.connect(on_clear_file)

    decrypt_radio.toggled.connect(on_mode_changed)
    encrypt_radio.toggled.connect(on_mode_changed)

    input_text_edit.textChanged.connect(update_ui_state)

    run_button.clicked.connect(on_run_clicked)
    copy_output_button.clicked.connect(on_copy_output)
    save_output_button.clicked.connect(on_save_output)

    # ---------------------- Initial UI State ----------------------
    update_ui_state()
    update_selection_options()

    window.show()
    sys.exit(app.exec())
