import requests

# ========================
# Encryption / Compression
# ========================

CLIENT_DATA_ENCRYPTION_PREFIX = "DbdDAwAC"
FULL_PROFILE_ENCRYPTION_PREFIX = "DbdDAgAC"
FULL_PROFILE_AES_KEY = b"5BCC2D6A95D4DF04A005504E59A9B36E"
ZLIB_COMPRESSION_PREFIX = "DbdDAQEB"

# ========================
# Remote Key API
# ========================

KEY_API_URL = "https://keyapi.deadbyqueue.com/keys"


def clean_quotes(s):
    """
    Removes wrapping quotes and unescapes \" inside strings.
    """
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s.replace('\\"', '"')


def version_to_tuple(version):
    """
    Converts a version string like '9.3.0' into a tuple (9, 3, 0).
    """
    return tuple(int(x) for x in version.split("."))


# ========================
# Access Keys
# ========================


def fetch_access_keys():
    """
    Fetches Dead by Daylight access keys from the remote key API.

    Returns:
        dict: { key_id: access_key, ... }
            - Only includes keys with versions >= 9.3.0.
            - Skips keys starting with "9999." or "m_5.".
        Returns an empty dict if the request fails or no valid keys are found.
    """
    try:
        response = requests.get(KEY_API_URL, timeout=5)
        response.raise_for_status()
        response_text = response.text
    except Exception:
        return {}

    access_keys = {}

    for line in response_text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue

        left, right = line.split(":", 1)
        left = clean_quotes(left.strip())
        right = clean_quotes(right.strip())

        if not left or not right:
            continue

        if left.startswith("9999.") or left.startswith("m_5."):
            continue

        version_prefix = left.split("_")[0]
        if version_to_tuple(version_prefix) < (9, 3, 0):
            continue

        access_keys[left] = right

    return access_keys


ACCESS_KEYS = fetch_access_keys()

# ========================
# Decryption Branches
# ========================

# Human-readable branch names mapped to branch codes.
# Used to select the correct branch-specific decryption key.
DECRYPT_BRANCH_MAP = {
    "Staging": "stage",
    "Certification": "cert",
    "Player Test Build": "ptb",
    "Live": "live",
}

DECRYPT_BRANCHES = list(DECRYPT_BRANCH_MAP.keys())

# ========================
# Encryption Key IDs
# ========================

# Version-tagged key identifiers fetched from the remote key API.
# Used for encrypting data for the correct game version.
ENCRYPT_KEYS = list(ACCESS_KEYS.keys())