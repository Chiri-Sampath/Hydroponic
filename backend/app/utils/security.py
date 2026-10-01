"""
AgriSmart AI — Security Utilities
====================================
Password hashing, token generation, file validation.
No secrets are hardcoded here — all keys come from config/env.
"""

import os
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional

import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt. Never store plain text."""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def check_password(plain_password: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed.encode("utf-8"))


def generate_reset_token(length: int = 64) -> str:
    """Generate a cryptographically secure URL-safe reset token."""
    return secrets.token_urlsafe(length)


def generate_batch_code(prefix: str = "BATCH") -> str:
    """Generate a unique batch code for quality passports."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    suffix = secrets.token_hex(4).upper()
    return f"{prefix}-{timestamp}-{suffix}"


def generate_share_token(length: int = 32) -> str:
    """Generate a read-only share token for quality passports."""
    return secrets.token_urlsafe(length)


def allowed_upload_file(filename: str, allowed_extensions: set) -> bool:
    """Check if a file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def safe_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    Keeps only alphanumeric chars, dots, underscores, and hyphens.
    """
    basename = os.path.basename(filename)
    allowed = set(string.ascii_letters + string.digits + "._-")
    safe = "".join(c for c in basename if c in allowed)
    return safe or "unnamed_file"


def is_valid_email(email: str) -> bool:
    """Basic email format check."""
    import re
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 254
