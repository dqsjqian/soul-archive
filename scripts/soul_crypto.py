#!/usr/bin/env python3
"""
🔐 Soul Archive Data Protection Module

Provides transparent privacy protection for soul archive data files.
Sensitive data is sealed with AES-256-GCM when privacy mode is enabled.

Algorithm: AES-256-GCM (authenticated data protection)
Key derivation: PBKDF2-HMAC-SHA256 (600,000 iterations)
Each file has its own random IV (nonce), stored alongside the ciphertext.

Sealed file format (binary):
  [4 bytes marker "SOUL"][12 bytes nonce][N bytes ciphertext+tag]

Usage:
  from soul_crypto import SoulCrypto

  crypto = SoulCrypto(password="user_password", salt=b"...")
  # or
  crypto = SoulCrypto.from_config(config_dict, password="user_password")

  sealed = crypto.seal_json({"key": "value"})
  opened = crypto.unseal_json(sealed)

  crypto.seal_file(Path("data.json"))  # in-place seal
  opened = crypto.unseal_file(Path("data.json"))  # read without modifying

Cross-platform: uses only Python standard library + cryptography package
"""

import base64
import getpass
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Optional, Union


# ============================================================
# Constants
# ============================================================

SALT_SIZE = 16          # 128-bit salt
NONCE_SIZE = 12         # 96-bit nonce (GCM standard)
KEY_SIZE = 32           # 256-bit key
KDF_ITERATIONS = 600_000  # OWASP 2023 recommendation for PBKDF2-SHA256
DATA_MARKER = b"SOUL"  # Magic bytes to identify sealed (protected) files


# ============================================================
# Core Crypto Class
# ============================================================

class SoulCrypto:
    """
    Handles AES-256-GCM privacy protection for soul archive data.

    Uses PBKDF2-HMAC-SHA256 for key derivation from access key + salt.
    Each seal operation generates a fresh random nonce.
    """

    def __init__(self, password: str, salt: bytes):
        """
        Initialize with access key and salt.

        Args:
            password: User's access key (confidential) string
            salt: 16-byte salt (stored in config.json)
        """
        self._key = self._derive_key(password, salt)
        self._salt = salt

    @staticmethod
    def generate_salt() -> bytes:
        """Generate a cryptographically secure random salt."""
        return os.urandom(SALT_SIZE)

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive a 256-bit key from access key using PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations=KDF_ITERATIONS,
            dklen=KEY_SIZE
        )

    @classmethod
    def from_config(cls, config: dict, password: str) -> "SoulCrypto":
        """
        Create SoulCrypto from config.json data.

        Args:
            config: The config dict (must have encryption_salt)
            password: User's access key (confidential)
        """
        salt_b64 = config.get("encryption_salt")
        if not salt_b64:
            raise ValueError("config.json 中缺少 encryption_salt 字段")
        salt = base64.b64decode(salt_b64)
        return cls(password=password, salt=salt)

    def verify_password(self, config: dict) -> bool:
        """
        Verify access key against stored verification hash.

        Args:
            config: config dict with encryption_verify field
        Returns:
            True if access key is correct
        """
        verify_b64 = config.get("encryption_verify")
        if not verify_b64:
            return True  # No verification hash stored, skip check
        verify_data = base64.b64decode(verify_b64)
        try:
            plaintext = self._unseal_bytes(verify_data)
            return plaintext == b"soul-archive-verify"
        except Exception:
            return False

    def create_verify_token(self) -> str:
        """Create a verification token for access key validation."""
        sealed = self._seal_bytes(b"soul-archive-verify")
        return base64.b64encode(sealed).decode("ascii")

    # ---- Low-level seal/unseal ----

    def _seal_bytes(self, plaintext: bytes) -> bytes:
        """
        Seal bytes using AES-256-GCM.

        Returns: nonce (12 bytes) + ciphertext + tag (16 bytes)
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            _require_cryptography()
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = os.urandom(NONCE_SIZE)
        aesgcm = AESGCM(self._key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def _unseal_bytes(self, data: bytes) -> bytes:
        """
        Unseal bytes sealed with _seal_bytes.

        Args:
            data: nonce (12 bytes) + ciphertext + tag
        Returns:
            Original plaintext bytes
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        except ImportError:
            _require_cryptography()
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        if len(data) < NONCE_SIZE + 16:  # nonce + minimum tag
            raise ValueError("Sealed data format error: data too short")

        nonce = data[:NONCE_SIZE]
        ciphertext = data[NONCE_SIZE:]
        aesgcm = AESGCM(self._key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    # ---- JSON-level seal/unseal ----

    def seal_json(self, data: dict) -> bytes:
        """
        Seal a dict as JSON → UTF-8 bytes → AES-256-GCM.

        Returns: MARKER(4) + nonce(12) + ciphertext+tag
        """
        plaintext = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        sealed = self._seal_bytes(plaintext)
        return DATA_MARKER + sealed

    def unseal_json(self, data: bytes) -> dict:
        """
        Unseal bytes back to a dict.

        Args:
            data: MARKER(4) + nonce(12) + ciphertext+tag
        Returns:
            Original dict
        """
        if not data.startswith(DATA_MARKER):
            raise ValueError("Not valid sealed data (missing SOUL marker)")
        sealed = data[len(DATA_MARKER):]
        plaintext = self._unseal_bytes(sealed)
        return json.loads(plaintext.decode("utf-8"))

    # ---- File-level seal/unseal ----

    def seal_file(self, path: Path) -> None:
        """
        Seal a JSON file in-place with privacy protection.
        If file is already sealed, skip it.
        """
        raw = path.read_bytes()
        if raw.startswith(DATA_MARKER):
            return  # Already sealed
        # Parse to validate it's valid JSON first
        try:
            data = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return  # Not a JSON file, skip
        sealed = self.seal_json(data)
        path.write_bytes(sealed)

    def unseal_file(self, path: Path) -> dict:
        """
        Read and unseal a file, return the dict.
        If file is not sealed (plain JSON), just parse it.
        Does NOT modify the file on disk.
        """
        raw = path.read_bytes()
        if raw.startswith(DATA_MARKER):
            return self.unseal_json(raw)
        else:
            # Plain text JSON -- just parse it
            return json.loads(raw.decode("utf-8"))

    def seal_file_save(self, path: Path, data: dict) -> None:
        """
        Seal a dict and write to file.
        """
        sealed = self.seal_json(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(sealed)

    # ---- JSONL support ----

    def seal_jsonl_record(self, record: dict) -> bytes:
        """Seal a single JSONL record. Returns base64-encoded line + newline."""
        plaintext = json.dumps(record, ensure_ascii=False).encode("utf-8")
        sealed = self._seal_bytes(plaintext)
        return base64.b64encode(DATA_MARKER + sealed) + b"\n"

    def unseal_jsonl_record(self, line: bytes) -> dict:
        """Unseal a single JSONL line (base64 encoded)."""
        line = line.strip()
        if not line:
            raise ValueError("Empty line")
        try:
            # Try base64 decode first (sealed line)
            raw = base64.b64decode(line)
            if raw.startswith(DATA_MARKER):
                return self.unseal_json(raw)
        except Exception:
            pass
        # Fallback: plain text JSON line
        return json.loads(line.decode("utf-8"))

    def append_sealed_record(self, path: Path, record: dict) -> None:
        """Append a sealed record to a JSONL file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "ab") as f:
            f.write(self.seal_jsonl_record(record))

    def read_sealed_records(self, path: Path) -> list:
        """Read all records from a sealed JSONL file."""
        records = []
        if not path.exists():
            return records
        with open(path, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(self.unseal_jsonl_record(line))
                except Exception:
                    # Try plain JSON fallback
                    try:
                        records.append(json.loads(line.decode("utf-8")))
                    except Exception:
                        continue
        return records


# ============================================================
# Utility Functions
# ============================================================

def is_file_sealed(path: Path) -> bool:
    """Check if a file is sealed (starts with SOUL marker)."""
    if not path.exists():
        return False
    with open(path, "rb") as f:
        header = f.read(len(DATA_MARKER))
    return header == DATA_MARKER


def is_file_sealed_jsonl(path: Path) -> bool:
    """Check if a JSONL file has sealed lines."""
    if not path.exists():
        return False
    with open(path, "rb") as f:
        first_line = f.readline().strip()
    if not first_line:
        return False
    try:
        raw = base64.b64decode(first_line)
        return raw.startswith(DATA_MARKER)
    except Exception:
        return False


def prompt_password(confirm: bool = False) -> str:
    """
    Interactively prompt user for access key.

    Args:
        confirm: If True, ask for key twice to confirm
    Returns:
        Access key string
    Raises:
        PrivacyProtectionError if key is empty or mismatched
    """
    # Check environment variable first
    env_pw = os.environ.get("SOUL_PASSWORD")
    if env_pw:
        return env_pw

    password = getpass.getpass("🔐 请输入灵魂存档访问密钥: ")
    if not password:
        raise PrivacyProtectionError("访问密钥不能为空")

    if confirm:
        password2 = getpass.getpass("🔐 请再次输入访问密钥确认: ")
        if password != password2:
            raise PrivacyProtectionError("两次输入的访问密钥不一致")

    return password


def get_crypto_from_config(config: dict, password: str = None) -> Optional[SoulCrypto]:
    """
    Get a SoulCrypto instance from config, or None if privacy protection is disabled.

    Args:
        config: config.json dict
        password: Access key string. If None, will prompt interactively.
    Returns:
        SoulCrypto instance or None
    Raises:
        PrivacyProtectionError on wrong access key
    """
    if not config.get("encryption"):
        return None

    if password is None:
        password = prompt_password()

    crypto = SoulCrypto.from_config(config, password)

    if not crypto.verify_password(config):
        raise PrivacyProtectionError("访问密钥错误")

    return crypto


def _require_cryptography():
    """Check if cryptography package is installed, raise if not."""
    try:
        import cryptography  # noqa: F401
    except ImportError:
        raise PrivacyProtectionError(
            "数据保护功能需要安装 cryptography 包:\n"
            "   pip install cryptography"
        )


# ============================================================
# Data protection: apply or remove privacy protection on soul data files
# ============================================================

# Data files that contain personal information and need privacy protection
PROTECTED_DATA_FILES = [
    "identity/basic_info.json",
    "identity/personality.json",
    "style/language.json",
    "style/communication.json",
    "memory/semantic/topics.json",
    "memory/semantic/knowledge.json",
    "memory/emotional/patterns.json",
    "relationships/people.json",
    "agent/patterns.json",
]

# Append-only log files that contain personal information
PROTECTED_LOG_FILES = [
    "soul_changelog.jsonl",
    "agent/corrections.jsonl",
    "agent/reflections.jsonl",
]

# Non-sensitive metadata (always plain text)
METADATA_FILES = [
    "config.json",
    "profile.json",
]


class PrivacyProtectionError(Exception):
    """Raised when a privacy protection operation fails (e.g. wrong access key)."""
    pass


def protect_data_files(soul_dir: Path, crypto: SoulCrypto) -> list:
    """Apply privacy protection to personal data files.

    Only processes files that are currently unprotected.
    Returns list of newly protected file paths.
    """
    protected = []

    for rel_path in PROTECTED_DATA_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and not is_file_sealed(fpath):
            crypto.seal_file(fpath)
            protected.append(str(rel_path))

    for rel_path in PROTECTED_LOG_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and not is_file_sealed_jsonl(fpath):
            _protect_log_file(fpath, crypto)
            protected.append(str(rel_path))

    # Episodic memory logs
    for log_dir in [soul_dir / "memory" / "episodic", soul_dir / "agent" / "episodes"]:
        if log_dir.exists():
            for jl in log_dir.glob("*.jsonl"):
                if not is_file_sealed_jsonl(jl):
                    _protect_log_file(jl, crypto)
                    protected.append(str(jl.relative_to(soul_dir)))

    return protected


def restore_data_files(soul_dir: Path, crypto: SoulCrypto) -> list:
    """Remove privacy protection from data files (restore to plain text).

    Only processes files that are currently protected.
    Returns list of restored file paths.
    """
    restored = []

    for rel_path in PROTECTED_DATA_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and is_file_sealed(fpath):
            data = crypto.unseal_file(fpath)
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            restored.append(str(rel_path))

    for rel_path in PROTECTED_LOG_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and is_file_sealed_jsonl(fpath):
            _restore_log_file(fpath, crypto)
            restored.append(str(rel_path))

    for log_dir in [soul_dir / "memory" / "episodic", soul_dir / "agent" / "episodes"]:
        if log_dir.exists():
            for jl in log_dir.glob("*.jsonl"):
                if is_file_sealed_jsonl(jl):
                    _restore_log_file(jl, crypto)
                    restored.append(str(jl.relative_to(soul_dir)))

    return restored


def _protect_log_file(path: Path, crypto: SoulCrypto) -> None:
    """Apply privacy protection to a single log file (JSONL format)."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    with open(path, "wb") as f:
        for record in records:
            f.write(crypto.seal_jsonl_record(record))


def _restore_log_file(path: Path, crypto: SoulCrypto) -> None:
    """Remove privacy protection from a single log file (JSONL format)."""
    records = crypto.read_sealed_records(path)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ============================================================
# Privacy verification: access key check before any data access
# ============================================================

VERIFY_FILE = ".encryption_verify"
VERIFY_MAGIC = "soul-archive-verify"
VERIFY_PAYLOAD = {"magic": VERIFY_MAGIC, "version": 1}


def create_verify_file(soul_dir: Path, crypto: SoulCrypto = None) -> None:
    """Create the privacy verification file.

    - If crypto is None: write plain JSON (unprotected mode)
    - If crypto is given: write protected version (protected mode)

    This file is ALWAYS created during init. Its state (plain vs protected)
    tells whether an access key is needed to access the archive.
    """
    verify_path = soul_dir / VERIFY_FILE
    if crypto:
        verify_path.write_bytes(crypto.seal_json(VERIFY_PAYLOAD))
    else:
        with open(verify_path, "w", encoding="utf-8") as f:
            json.dump(VERIFY_PAYLOAD, f, ensure_ascii=False)


def check_verify_file(soul_dir: Path) -> str:
    """Check whether the archive is in protected or unprotected mode.

    Returns:
      "none"      - verify file doesn't exist (needs initialization)
      "plain"     - unprotected mode (no access key needed)
      "protected" - protected mode (access key required)
      "invalid"   - verify file exists but is corrupted
    """
    verify_path = soul_dir / VERIFY_FILE
    if not verify_path.exists():
        return "none"
    try:
        raw = verify_path.read_bytes()
        if raw.startswith(DATA_MARKER):
            return "protected"
        data = json.loads(raw.decode("utf-8"))
        if data.get("magic") == VERIFY_MAGIC:
            return "plain"
        return "invalid"
    except Exception:
        return "invalid"


def verify_password(soul_dir: Path, crypto: SoulCrypto) -> bool:
    """Verify access key against the verification file.

    ONLY reads the verify file -- never touches data files.
    Returns True if access key is correct.
    """
    verify_path = soul_dir / VERIFY_FILE
    if not verify_path.exists():
        return False
    try:
        data = crypto.unseal_json(verify_path.read_bytes())
        return data.get("magic") == VERIFY_MAGIC
    except Exception:
        return False


def _check_any_protected(soul_dir: Path) -> bool:
    """Check if any data file has privacy protection applied."""
    for rel_path in PROTECTED_DATA_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and is_file_sealed(fpath):
            return True
    for rel_path in PROTECTED_LOG_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and is_file_sealed_jsonl(fpath):
            return True
    return False


def _check_any_unprotected(soul_dir: Path) -> bool:
    """Check if any personal data file is still unprotected."""
    for rel_path in PROTECTED_DATA_FILES:
        fpath = soul_dir / rel_path
        if fpath.exists() and not is_file_sealed(fpath):
            try:
                raw = fpath.read_bytes()
                if raw and not raw.startswith(DATA_MARKER):
                    return True
            except Exception:
                pass
    return False


def _resolve_password(password: str = None) -> str:
    """Resolve access key from argument, environment variable, or interactive prompt.

    Priority: explicit argument > SOUL_PASSWORD env var > interactive prompt.
    Raises PrivacyProtectionError if no access key can be obtained.
    """
    if password:
        return password
    env_pw = os.environ.get("SOUL_PASSWORD")
    if env_pw:
        return env_pw
    try:
        pw = getpass.getpass("🔐 请输入灵魂存档访问密钥: ")
        if pw:
            return pw
    except (EOFError, KeyboardInterrupt):
        pass
    raise PrivacyProtectionError(
        "需要访问密钥才能访问受保护的灵魂存档。\n"
        "   方式 1: 设置环境变量 SOUL_ACCESS_KEY\n"
        "   方式 2: 使用 --access-key 参数\n"
        "   方式 3: 交互式输入"
    )


def _resolve_new_password(password: str = None) -> str:
    """Resolve a new access key (with confirmation) for first-time setup."""
    if password:
        return password
    env_pw = os.environ.get("SOUL_PASSWORD")
    if env_pw:
        return env_pw
    return prompt_password(confirm=True)


# ============================================================
# Privacy manager: unified entry point for data protection state
# ============================================================

def ensure_privacy_state(soul_dir: Path, config: dict, password: str = None) -> SoulCrypto:
    """Ensure the archive's privacy protection matches the user's configuration.

    Reads the verification file to determine current state, then reconciles
    with config.json settings. Handles all transitions gracefully:

      - Unprotected → Unprotected : no-op
      - Protected → Protected     : verify password, return crypto
      - Unprotected → Protected   : ask for new password, apply protection
      - Protected → Unprotected   : ask for password, remove protection

    The verification file (.encryption_verify) is always checked FIRST.
    Password is verified before any data file is read or modified.

    Returns: SoulCrypto if protection is active, None otherwise.
    Raises: PrivacyProtectionError on wrong access key or missing credentials.
    """
    verify_state = check_verify_file(soul_dir)
    protection_enabled = config.get("encryption", False)
    has_salt = bool(config.get("encryption_salt"))

    # ---- Currently unprotected ----
    if verify_state == "plain":
        if not protection_enabled:
            return None

        # User wants to enable protection
        print()
        print("🔐 正在启用数据保护...")
        print("   ⚠️  请牢记此访问密钥！访问密钥丢失将无法恢复数据。")
        print()
        pw = _resolve_new_password(password)
        salt = SoulCrypto.generate_salt()
        crypto = SoulCrypto(pw, salt)

        create_verify_file(soul_dir, crypto)
        config["encryption_salt"] = base64.b64encode(salt).decode("ascii")
        config["encryption_verify"] = crypto.create_verify_token()
        config["encryption_algorithm"] = "AES-256-GCM"
        config["encryption_key_derivation"] = "PBKDF2-SHA256"
        with open(soul_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        protected = protect_data_files(soul_dir, crypto)
        print(f"   ✅ 已保护 {len(protected)} 个数据文件")
        print()
        return crypto

    # ---- Currently protected ----
    if verify_state == "protected":
        if not has_salt:
            raise PrivacyProtectionError(
                "验证文件显示数据已受保护，但 config.json 缺少必要的配置信息。"
            )

        pw = _resolve_password(password)
        crypto = SoulCrypto.from_config(config, pw)

        if not verify_password(soul_dir, crypto):
            raise PrivacyProtectionError("访问密钥错误，无法访问受保护的数据。")

        if protection_enabled:
            # Normal protected operation; ensure consistency
            if _check_any_unprotected(soul_dir):
                newly = protect_data_files(soul_dir, crypto)
                if newly:
                    print(f"🔐 已补充保护 {len(newly)} 个数据文件")
            return crypto
        else:
            # User wants to disable protection
            print()
            print("🔓 正在移除数据保护...")
            restored = restore_data_files(soul_dir, crypto)
            if restored:
                print(f"   ✅ 已恢复 {len(restored)} 个数据文件为明文")
            create_verify_file(soul_dir, crypto=None)
            print("   ✅ 数据保护已关闭")
            print()
            return None

    # ---- No verify file (first run or upgrade from older version) ----
    if verify_state in ("none", "invalid"):
        if protection_enabled and has_salt:
            # Upgrading from older version that didn't have verify file
            pw = _resolve_password(password)
            crypto = SoulCrypto.from_config(config, pw)
            if not crypto.verify_password(config):
                raise PrivacyProtectionError("访问密钥错误。")
            create_verify_file(soul_dir, crypto)
            if _check_any_unprotected(soul_dir):
                newly = protect_data_files(soul_dir, crypto)
                if newly:
                    print(f"🔐 已补充保护 {len(newly)} 个数据文件")
            return crypto

        if protection_enabled and not has_salt:
            # First-time protection setup
            print()
            print("🔐 首次启用数据保护...")
            print("   ⚠️  请牢记此访问密钥！访问密钥丢失将无法恢复数据。")
            print()
            pw = _resolve_new_password(password)
            salt = SoulCrypto.generate_salt()
            crypto = SoulCrypto(pw, salt)
            create_verify_file(soul_dir, crypto)
            config["encryption_salt"] = base64.b64encode(salt).decode("ascii")
            config["encryption_verify"] = crypto.create_verify_token()
            config["encryption_algorithm"] = "AES-256-GCM"
            config["encryption_key_derivation"] = "PBKDF2-SHA256"
            with open(soul_dir / "config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            protected = protect_data_files(soul_dir, crypto)
            if protected:
                print(f"   ✅ 已保护 {len(protected)} 个数据文件")
            print()
            return crypto

        # No protection needed
        create_verify_file(soul_dir, crypto=None)
        return None
