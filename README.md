# DBDCrypter

[Dead by Daylight](https://deadbydaylight.com/) is an online asymmetric multiplayer survival horror video game developed and published by Canadian studio [Behaviour Interactive](https://www.bhvr.com/).

**DBDCrypter** is a desktop GUI tool for decrypting and re-encrypting data from Dead by Daylight's private API. It supports both client and full-profile data formats using environment-specific access keys for the Stage, Cert, PTB, and Live environments.

## Installation

### Option 1: Run from Source

If you want to run the application from source, ensure you have [Python 3.10 or later](https://www.python.org/downloads/) installed. Then open a terminal and run:
```
git clone https://github.com/EigenvoidDev/DBDCrypter.git
cd DBDCrypter
```
Install the required dependencies:
```
pip install -r requirements.txt
```
Finally, start the application:
```
python main.py
```

### Option 2: Download Prebuilt Release

If you are on **Windows**, download the prebuilt release from the [Releases page](https://github.com/EigenvoidDev/DBDCrypter/releases). Once downloaded, simply double-click the file to launch the application.

#### Windows Security Warnings

On **Windows 8 and later**, you may see a security warning when launching the application. This occurs because the application is not digitally signed, and Windows relies on code-signing to verify the identity of software publishers. Since obtaining a code-signing certificate requires a paid license, unsigned applications are labeled as coming from an "unknown publisher".

Some antivirus software may also flag the application as suspicious or block the download. These detections are **false positives**. If the application is blocked from running, you may need to add it to your allowlist or exclusions.

## Usage

The application opens in **Decrypt mode by default**.

At the top of the interface, select the desired mode:

- **Decrypt:** Load encrypted data from a file or enter it manually, select the corresponding **Key ID**, and click **Run**.
- **Encrypt:** Load decrypted data from a file, select the corresponding **Key ID**, and click **Run**.

## Access Key Handling

On startup, the application retrieves the latest access keys from the [Dead by Queue Key API](https://keyapi.deadbyqueue.com/keys) and stores them in memory for the duration of the session. When Behaviour Interactive updates Dead by Daylight, the API provides updated access keys.

**Note:** An active internet connection is required when launching the application. If the API cannot be reached, features that rely on access keys may not function until connectivity is restored.

## Attributions / Permissions

Some portions of this project are based on code by [Masusder](https://github.com/Masusder). Permission to use and modify this code was granted by the author.

## License

DBDCrypter is licensed under the [GNU General Public License v3.0 (GPLv3)](https://github.com/EigenvoidDev/DBDCrypter/blob/main/LICENSE).
