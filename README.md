# DBDCrypter

[Dead by Daylight](https://deadbydaylight.com/) is an online asymmetric multiplayer survival horror video game developed and published by Canadian studio [Behaviour Interactive](https://www.bhvr.com/).

**DBDCrypter** is a desktop GUI tool for decrypting and re-encrypting data from Dead by Daylight's private API. It supports both client and full-profile data formats, with branch-specific keys for QA, Stage, Cert, PTB, and Live environments.

## Installation

### Option 1: Run from Source

If you are running the application from source (e.g., cloned from GitHub), ensure you have [Python 3.9 or later](https://www.python.org/downloads/) installed. Then install the required dependencies with pip:
```
pip install PyQt6 pycryptodome requests
```
After installation, open a terminal, navigate to the project's root directory, and start the application with:
```
python main.py
```

### Option 2: Download Prebuilt Release

If you are on **Windows**, download the prebuilt release from the [Releases page](https://github.com/EigenvoidDev/DBDCrypter/releases). Once downloaded, simply double-click the file to launch the application.

#### Windows Security Warnings

On **Windows 8 and later**, you may see a security warning when launching the application. This occurs because the application is not digitally signed, and Windows relies on code-signing to verify the identity of software publishers. Since obtaining a code-signing certificate requires a paid license, unsigned applications are labeled as coming from an "unknown publisher".

Some antivirus software may also flag the application as suspicious or block the download. These detections are **false positives**. If the application is blocked from running, you may need to add it to your allowlist or exclusions.

## Usage

At the top of the interface, select whether you want to **decrypt** or **encrypt** data:
- **Decrypt:** Enter the encrypted data manually or load it from a file, then select the appropriate branch and click the **Run** button.
- **Encrypt:** Choose a file containing decrypted data, select its corresponding key ID, and click the **Run** button.

## Access Key Handling

On startup, the application retrieves access keys automatically from the **[Dead by Queue Key API](https://keyapi.deadbyqueue.com/keys)** and stores them in memory for the current session. When Behaviour Interactive updates Dead by Daylight and the keys change, the API automatically provides the updated keys.

**Note:** An active internet connection is required when launching the application. If the API cannot be reached, any features that rely on access keys may not function until connectivity is restored.

## Attributions / Permissions

Some portions of this project are based on code by [Masusder](https://github.com/Masusder). Permission to use and modify this code has been granted by the author.

## License

DBDCrypter is licensed under the [GNU General Public License v3.0 (GPLv3)](https://github.com/EigenvoidDev/DBDCrypter/blob/main/LICENSE).