from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from .base import BaseDetector, Match


class CustomPatternDetector(BaseDetector):
    name = "custom"
    priority = 10

    def __init__(self, patterns_file=None):
        self._custom_patterns = self._load(patterns_file or self._default_path())

    def _default_path(self):
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
            return Path(appdata) / "scrub-ai" / "patterns.json"
        return Path.home() / ".config" / "scrub-ai" / "patterns.json"

    def _load(self, path):
        if not path.exists():
            return []
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
            result = []
            for entry in entries:
                pattern = re.compile(entry["pattern"])
                replacement = entry.get("replacement", "[CUSTOM]")
                label = entry.get("label", "custom")
                confidence = float(entry.get("confidence", 1.0))
                result.append((pattern, replacement, label, confidence))
            return result
        except (json.JSONDecodeError, OSError, KeyError, re.error):
            return []

    def detect(self, text):
        matches = []
        for pattern, replacement, label, confidence in self._custom_patterns:
            for m in pattern.finditer(text):
                matches.append(Match(
                    start=m.start(),
                    end=m.end(),
                    original=m.group(),
                    replacement=replacement,
                    category=self.name,
                    label=label,
                    confidence=confidence,
                ))
        return matches