from scrub_ai.detectors.base import BaseDetector
from scrub_ai.sanitizer import Sanitizer, sanitize_text


class OverlapDetector(BaseDetector):
    name = "test"
    priority = 1

    def detect(self, text: str):
        return [
            # Larger low-confidence span
            self._match(7, 15, "[WIDE]", "wide", confidence=0.7),
            # Smaller high-confidence span inside larger span
            self._match(10, 15, "[NARROW]", "narrow", confidence=1.0),
        ]

    def _match(self, start, end, replacement, label, confidence=1.0):
        from scrub_ai.detectors.base import Match

        return Match(
            start=start,
            end=end,
            original="",
            replacement=replacement,
            category=self.name,
            label=label,
            confidence=confidence,
        )


def test_sanitize_text_replaces_detected_values() -> None:
    text = "password=SuperSecret123 host=db01.prod.internal ip=10.0.1.45"

    clean, report = sanitize_text(text)

    assert "SuperSecret123" not in clean
    assert "db01.prod.internal" not in clean
    assert "10.0.1.45" not in clean
    assert report["total_matches"] >= 3
    assert report["is_clean"] is False


def test_overlap_resolution_prefers_higher_confidence() -> None:
    sanitizer = Sanitizer(detectors=[OverlapDetector()])
    text = "token: abcdefgh"

    result = sanitizer.sanitize(text)

    assert result.clean_text == "token: abc[NARROW]"
    assert result.report["by_label"]["narrow"] == 1
    assert "wide" not in result.report["by_label"]
