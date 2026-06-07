import base64
import requests

from config import (
    EXCLUDED_PREFIXES,
    KEY_API_URL,
    MIN_VERSION,
    REQUEST_TIMEOUT,
)

# ==================
# String Helpers
# ==================


def clean_quotes(value):
    value = value.strip()

    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    return value.replace('\\"', '"')


# ==================
# Access Key Helpers
# ==================


def decode_access_key(access_key):
    if any(character in access_key for character in "-_"):
        return base64.urlsafe_b64decode(access_key)

    return base64.b64decode(access_key)


# ==================
# Version Helpers
# ==================


def version_to_tuple(version):
    return tuple(int(part) for part in version.split("."))


# ==================
# Access Key Parsing
# ==================


def parse_access_keys(response_text):
    """
    Parse API response into a dictionary of access keys.

    Filters out excluded prefixes and versions below MIN_VERSION.
    Returns a mapping of key_id -> access_key.
    """
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

        version = key_id.split("_", 1)[0]

        try:
            if version_to_tuple(version) < MIN_VERSION:
                continue
        except ValueError:
            continue

        access_keys[key_id] = access_key

    return access_keys


# ==================
# API Access
# ==================


def fetch_access_keys():
    """
    Fetch access keys from the API and return parsed results.

    Returns an empty dictionary if the request fails.
    """
    try:
        response = requests.get(
            KEY_API_URL,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        print(f"Failed to fetch access keys: {exc}")
        return {}

    return parse_access_keys(response.text)
