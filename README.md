# DBDCrypter

[Dead by Daylight](https://deadbydaylight.com/) is an online asymmetric multiplayer survival horror video game developed and published by Canadian studio [Behaviour Interactive](https://www.bhvr.com/).

**DBDCrypter** is a command-line tool that can decrypt and re-encrypt data served from Dead by Daylight's private API. It handles both asset and profile data formats and supports branch-specific keys for QA, Stage, Cert, PTB, and Live environments.

## Requirements

This tool requires the [PyCryptodome](https://pypi.org/project/pycryptodome/) library to run. You can install it using pip:
```
pip install pycryptodome
```

## Usage

To run this tool, open a terminal, navigate to its root directory, and execute:
```
python main.py
```

You will be prompted to choose whether to decrypt or encrypt data.
- **For decryption:** You can either manually enter the encrypted data or load it from a file. Once provided, you will be prompted to select a branch by entering its corresponding key.
- **For encryption:** You will be prompted to select a file containing decrypted data and then enter its corresponding versioned branch.

## Updating Access keys

**Note:** When a new Dead by Daylight update is released, the access keys for each game branch may change. You will need to manually update the access keys in the `config.py` module to reflect the new game version. To update the access keys, follow these steps:

1. Launch [FModel](https://github.com/4sval/FModel), select Dead by Daylight as the detected game, and provide the appropriate mapping file and AES key. Then, load the game archives, navigate to the `DeadByDaylight` directory, and open `Config > DefaultGame.ini`.

2. In `DefaultGame.ini`, locate the section header `[/Script/S3Command.AccessKeys]`. The access keys are listed directly beneath this header.

3. If `DefaultGame.ini` does not appear in the `Config` folder, then export the raw data of the `Config` folder's package to a directory of your choice. After exporting, open the file from the output directory to locate the access keys.

4. Copy the updated access keys from `DefaultGame.ini` and paste them into the `config.py` module, where the `ACCESS_KEYS` dictionary is defined.

## License

DBDCrypter is licensed under the [Apache License 2.0](https://github.com/EigenvoidDev/DBDCrypter/blob/main/LICENSE). Licenses and attributions for third-party components are available in the [NOTICE file](https://github.com/EigenvoidDev/DBDCrypter/blob/main/NOTICE).