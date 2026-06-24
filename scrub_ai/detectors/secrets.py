from __future__ import annotations
import re
from .base import BaseDetector


class SecretsDetector(BaseDetector):
    name = "secrets"
    priority = 1
    patterns = [
        # Private keys (PEM blocks)
        (re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"), "[PRIVATE_KEY]", "private_key"),

        # JWTs
        (re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"), "[JWT]", "jwt"),

        # Bearer tokens
        (re.compile(r"(?i)bearer\s+([A-Za-z0-9\-._~+/]{20,})"), "[BEARER_TOKEN]", "bearer_token"),

        # Generic API keys (key = value patterns)
        (re.compile(r"(?i)(?:api[_-]?key|apikey|access[_-]?token|auth[_-]?token|secret[_-]?key)\s*[=:]\s*['\"]?([A-Za-z0-9\-._~+/]{16,})['\"]?"), "[API_KEY]", "api_key"),

        # Passwords in key=value form
        (re.compile(r"(?i)(?:password|passwd|pwd)\s*[=:]\s*['\"]?(\S+)['\"]?"), "[REDACTED]", "password"),

        # Generic high-entropy tokens (hex 32+ chars)
        (re.compile(r"\b[0-9a-f]{32,64}\b"), "[TOKEN]", "hex_token"),
    ]
