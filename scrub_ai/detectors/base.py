from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class Match:
    start: int
    end: int
    original: str
    replacement: str
    category: str
    label: str
    confidence: float = 1.0


class BaseDetector:
    name: str = ""
    priority: int = 99
    # Each entry is either (pattern, replacement, label) or (pattern, replacement, label, confidence).
    patterns: list[tuple] = []

    def detect(self, text: str) -> list[Match]:
        matches = []
        for entry in self.patterns:
            pattern, replacement, label = entry[0], entry[1], entry[2]
            confidence = entry[3] if len(entry) >= 4 else 1.0
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
