import requests

# =========================
# Configuration / Constants
# =========================

KEY_API_URL = "https://keyapi.deadbyqueue.com/keys"
REQUEST_TIMEOUT = 5

MIN_VERSION = (9, 5, 0)
EXCLUDED_PREFIXES = ("9999.", "m_5.")


class DataPrefixes:
    CLIENT_DATA = "DbdDAwAC"
    FULL_PROFILE = "DbdDAgAC"
    ZLIB = "DbdDAQEB"


class EncryptionKeys:
    FULL_PROFILE_AES = b"5BCC2D6A95D4DF04A005504E59A9B36E"


# =========================
# Utility Functions
# =========================


def clean_quotes(s):
    """Strip wrapping quotes and unescape escaped quotes."""
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s.replace('\\"', '"')


def version_to_tuple(version):
    return tuple(int(x) for x in version.split("."))


# =========================
# Parsing Logic
# =========================


def parse_access_keys(response_text):
    """Parse API response into access keys, filtering by version and excluded prefixes."""
    access_keys = {}

    for line in response_text.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue

        key_id, access_key = line.split(":", 1)
        key_id = clean_quotes(key_id.strip())
        access_key = clean_quotes(access_key.strip())

        if not key_id or not access_key:
            continue

        if key_id.startswith(EXCLUDED_PREFIXES):
            continue

        version_prefix = key_id.split("_")[0]

        try:
            if version_to_tuple(version_prefix) < MIN_VERSION:
                continue
        except ValueError:
            continue

        access_keys[key_id] = access_key

    return access_keys


# =========================
# API Access
# =========================


def fetch_access_keys():
    """Fetch access keys from the API and return parsed results, or {} on failure."""
    try:
        response = requests.get(KEY_API_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return {}

    return parse_access_keys(response.text)


# =========================
# Environment Branches
# =========================

ENVIRONMENT_BRANCH_MAP = {
    "Staging": "stage",
    "Certification": "cert",
    "Player Test Build": "ptb",
    "Live": "live",
}

ENVIRONMENT_BRANCHES = tuple(ENVIRONMENT_BRANCH_MAP.keys())
