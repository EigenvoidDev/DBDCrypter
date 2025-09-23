# DBDCrypter

[Dead by Daylight](https://deadbydaylight.com/) is an online asymmetric multiplayer survival horror video game developed and published by Canadian studio [Behaviour Interactive](https://www.bhvr.com/).

**DBDCrypter** is a desktop GUI tool for decrypting and re-encrypting data from Dead by Daylight's private API. It supports both client and full-profile data formats, with branch-specific keys for QA, Stage, Cert, PTB, and Live environments.

## Installation

### Option 1: Run from Source

If you are running the application from source (e.g., cloned from GitHub), ensure you have [Python 3.9 or later](https://www.python.org/downloads/) installed. Then install the required dependencies with pip:
```
pip install PyQt6 pycryptodome
```
After installation, open a terminal, navigate to the project’s root directory, and start the application with:
```
python main.py
```

### Option 2: Download Prebuilt Release

If you are on **Windows**, download the prebuilt release from the [Releases page](https://github.com/EigenvoidDev/DBDCrypter/releases). Once downloaded, simply double-click the file to launch the application.

#### Windows Security Warnings

On **Windows 8 and later**, you may see a **SmartScreen warning** because the application is unsigned. Code-signing certificates require a paid license, so Windows may list it as coming from an "unknown publisher".

Some antivirus software may also flag the application as suspicious or block the download. These detections are **false positives**. If the application is blocked from running, you may need to add it to your allowlist or exclusions.

## Usage

At the top of the interface, select whether you want to **decrypt** or **encrypt** data:
- **Decrypt:** Enter the encrypted data manually or load it from a file, then select the appropriate branch and click the **Run** button.
- **Encrypt:** Choose a file containing decrypted data, select its corresponding branch, and click the **Run** button.

## Updating Access Keys

**Note:** When a new Dead by Daylight update is released, the access keys for each game branch may change. You will need to manually update them in the `config.py` module to match the new game version. To update the access keys, follow these steps:

1. Launch [FModel](https://github.com/4sval/FModel), select Dead by Daylight as the detected game, and provide the appropriate mapping file and AES key. Load the game archives, navigate to the `DeadByDaylight` directory, and open `Config > DefaultGame.ini`.

2. In `DefaultGame.ini`, locate the section header `[/Script/S3Command.AccessKeys]`. The access keys are listed directly beneath this header.

3. If `DefaultGame.ini` does not appear in the `Config` folder, export the raw data of the `Config` folder's package to a directory of your choice. Then open the exported file to locate the access keys.

4. Copy the updated access keys from `DefaultGame.ini` and paste them into the `config.py` module, in the `ACCESS_KEYS` dictionary.

## Attributions / Permissions

Some portions of this project are based on code by [Masusder](https://github.com/Masusder). Permission to use and modify this code has been granted by the author.

## License

DBDCrypter is licensed under the [GNU General Public License v3.0 (GPLv3)](https://github.com/EigenvoidDev/DBDCrypter/blob/main/LICENSE).