from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from scrub_ai.detectors import CloudDetector, NetworkDetector, SecretsDetector
from scrub_ai.detectors.base import BaseDetector, Match
from scrub_ai.detectors.custom import CustomPatternDetector
from scrub_ai.detectors.pii import PIIDetector


@dataclass
class SanitizationResult:
    clean_text: str
    matches: list[Match]
    report: dict[str, object]


class Sanitizer:
    """Sanitizes text using all enabled detectors."""

    def __init__(self, detectors: list[BaseDetector] | None = None) -> None:
        self.detectors = detectors or [
            SecretsDetector(),
            CloudDetector(),
            NetworkDetector(),
            CustomPatternDetector(),
            PIIDetector(),
        ]

    def sanitize(self, text: str, min_confidence: float = 0.0) -> SanitizationResult:
        """Run detectors, resolve overlaps, apply replacements, and build a report."""
        all_matches: list[Match] = []
        for detector in sorted(self.detectors, key=lambda d: d.priority):
            all_matches.extend(detector.detect(text))

        if min_confidence > 0.0:
            all_matches = [m for m in all_matches if m.confidence >= min_confidence]

        selected_matches = self._resolve_overlaps(all_matches)
        clean_text = self._apply_replacements(text, selected_matches)
        report = self._build_report(selected_matches)

        return SanitizationResult(clean_text=clean_text, matches=selected_matches, report=report)

    def _resolve_overlaps(self, matches: list[Match]) -> list[Match]:
        if not matches:
            return []

        # Prefer higher confidence, then earlier start, then longest span.
        candidates = sorted(
            matches,
            key=lambda m: (-m.confidence, m.start, -(m.end - m.start)),
        )

        selected: list[Match] = []
        for candidate in candidates:
            has_overlap = False
            for existing in selected:
                if candidate.start < existing.end and existing.start < candidate.end:
                    has_overlap = True
                    break
            if not has_overlap:
                selected.append(candidate)

        return sorted(selected, key=lambda m: m.start)

    def _apply_replacements(self, text: str, matches: list[Match]) -> str:
        if not matches:
            return text

        clean = text
        for match in sorted(matches, key=lambda m: m.start, reverse=True):
            clean = clean[: match.start] + match.replacement + clean[match.end :]
        return clean

    def _build_report(self, matches: list[Match]) -> dict[str, object]:
        category_counts = Counter(m.category for m in matches)
        label_counts = Counter(m.label for m in matches)

        return {
            "total_matches": len(matches),
            "by_category": dict(category_counts),
            "by_label": dict(label_counts),
            "is_clean": len(matches) == 0,
        }


def sanitize_text(text: str, detectors: list[BaseDetector] | None = None, min_confidence: float = 0.0) -> tuple[str, dict[str, object]]:
    """Convenience helper returning `(clean_text, report)`."""
    result = Sanitizer(detectors=detectors).sanitize(text, min_confidence=min_confidence)
    return result.clean_text, result.report
