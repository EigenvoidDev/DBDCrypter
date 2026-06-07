# =========================
# Configuration / Constants
# =========================

KEY_API_URL = "https://keyapi.deadbyqueue.com/keys"
REQUEST_TIMEOUT = 5

MIN_VERSION = (9, 5, 0)
EXCLUDED_PREFIXES = ("9999.", "m_5.")

# =========================
# Data Prefixes
# =========================


class DataPrefixes:
    CLIENT_DATA = "DbdDAwAC"
    FULL_PROFILE = "DbdDAgAC"
    ZLIB = "DbdDAQEB"


# =========================
# Encryption Keys
# =========================


class EncryptionKeys:
    FULL_PROFILE_AES = b"5BCC2D6A95D4DF04A005504E59A9B36E"
