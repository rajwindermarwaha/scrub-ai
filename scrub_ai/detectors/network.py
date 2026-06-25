from __future__ import annotations

import re

from .base import BaseDetector


class NetworkDetector(BaseDetector):
    name = "network"
    priority = 3
    patterns = [
        # IPv4 addresses
        (
            re.compile(
                r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b"
            ),
            "[IP_ADDRESS]",
            "ipv4_address",
        ),

        # IPv6 addresses (full and compressed forms)
        (
            re.compile(
                r"\b(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}\b|\b(?:[A-Fa-f0-9]{1,4}:){1,7}:\b"
            ),
            "[IP_ADDRESS]",
            "ipv6_address",
        ),

        # Internal hostnames
        (
            re.compile(
                r"\b(?:localhost|[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.(?:internal|local|corp|lan|home\.arpa))\b",
                re.IGNORECASE,
            ),
            "[INTERNAL_HOSTNAME]",
            "internal_hostname",
        ),

        # Internal URLs
        (
            re.compile(
                r"\bhttps?://(?:localhost|127\.0\.0\.1|10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}|[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*\.(?:internal|local|corp|lan|home\.arpa))(?::\d{1,5})?(?:/[^\s\"']*)?",
                re.IGNORECASE,
            ),
            "[INTERNAL_URL]",
            "internal_url",
        ),
    ]