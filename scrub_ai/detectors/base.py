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
    patterns: list[tuple[re.Pattern, str, str]] = []  # (pattern, replacement, label)

    def detect(self, text: str) -> list[Match]:
        matches = []
        for pattern, replacement, label in self.patterns:
            for m in pattern.finditer(text):
                matches.append(Match(
                    start=m.start(),
                    end=m.end(),
                    original=m.group(),
                    replacement=replacement,
                    category=self.name,
                    label=label,
                ))
        return matches
