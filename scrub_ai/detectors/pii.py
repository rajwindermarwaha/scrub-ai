from __future__ import annotations

from .base import BaseDetector, Match

_REPLACEMENTS: dict[str, str] = {
    "EMAIL_ADDRESS": "[EMAIL]",
    "PHONE_NUMBER": "[PHONE_NUMBER]",
    "PERSON": "[PERSON]",
    "CREDIT_CARD": "[CREDIT_CARD]",
    "IBAN_CODE": "[IBAN]",
    "US_SSN": "[SSN]",
    "US_PASSPORT": "[PASSPORT]",
    "LOCATION": "[LOCATION]",
    "URL": "[URL]",
    "IP_ADDRESS": "[IP_ADDRESS]",
}

_SKIP_ENTITIES: frozenset[str] = frozenset({"IP_ADDRESS"})


class PIIDetector(BaseDetector):
    name = "pii"
    priority = 2

    def __init__(self) -> None:
        try:
            from presidio_analyzer import AnalyzerEngine  # type: ignore[import]
            self._analyzer = AnalyzerEngine()
            self._available = True
        except ImportError:
            self._analyzer = None
            self._available = False

    def detect(self, text: str) -> list[Match]:
        if not self._available or not text:
            return []

        try:
            results = self._analyzer.analyze(text=text, language="en")
        except Exception:
            return []

        matches = []
        for result in results:
            entity = result.entity_type
            if entity in _SKIP_ENTITIES:
                continue
            replacement = _REPLACEMENTS.get(entity, f"[{entity}]")
            matches.append(Match(
                start=result.start,
                end=result.end,
                original=text[result.start:result.end],
                replacement=replacement,
                category=self.name,
                label=entity.lower(),
                confidence=float(result.score),
            ))
        return matches
