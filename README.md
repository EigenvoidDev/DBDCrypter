# Dead By Daylight Content Delivery Network Decryptor

[Dead by Daylight](https://deadbydaylight.com/) is an online asymmetric multiplayer survival horror video game developed and published by Canadian studio [Behaviour Interactive](https://www.bhvr.com/).

**Dead by Daylight Content Delivery Network Decryptor** is a script designed to decrypt encrypted data transmitted via the Dead by Daylight Content Delivery Network (CDN). Although the CDN exclusively handles asset data, this script can also decrypt save profile data. It supports multiple game branches, including QA, Stage, Cert, PTB, and Live, each with its own access key tailored to the specific game version. The decryption process utilizes AES encryption, and when necessary, data is decompressed using zlib.

## Requirements

This script requires the [PyCryptodome](https://pypi.org/project/pycryptodome/) library to run. You can install it using pip:
```
pip install pycryptodome
```

## Usage

To run this script, navigate to the directory containing the script and execute the following command in your terminal:
```
python dbd_cdn_decryptor.py
```

You will be prompted to enter the encrypted data or load it from a file. After submitting it and pressing "Enter," you will be asked to select a branch. Type the key for your chosen branch and press "Enter."

## Updating Access Keys

Please note that when a new Dead by Daylight update is released, access keys for the different game branches may change. You will need to manually update the access keys in the script to reflect the new game version. To update the access keys in the script, follow these steps:

1. Launch [FModel](https://github.com/4sval/FModel), select Dead by Daylight as your detected game, and provide the relevant mapping file and AES key. Then, load the game archives, navigate to the `DeadByDaylight` directory, and open `Config > DefaultGame.ini`.

2. In `DefaultGame.ini`, search for the section header `[/Script/S3Command.AccessKeys]`. Below this, you will find a list of AES access keys.

3. If `DefaultGame.ini` is not visible in the `Config` folder within FModel, then export the `Config` folder's package raw data to your chosen output directory. After exporting, open the file from there to locate the access keys.

4. Copy the updated access keys from `DefaultGame.ini` and paste them into the script's configuration section, where the keys are defined.

## License

Dead by Daylight Content Delivery Network Decryptor is licensed under [Apache License 2.0](https://github.com/EigenvoidDev/DeadByDaylightCDNDecryptor/blob/main/LICENSE), and licenses of third-party libraries used are listed [here](https://github.com/EigenvoidDev/DeadByDaylightCDNDecryptor/blob/main/NOTICE).
