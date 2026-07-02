from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from scrub_ai.detectors.pii import PIIDetector


class _FakeResult:
    def __init__(self, entity_type: str, start: int, end: int, score: float = 0.85) -> None:
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.score = score


def _make_detector(results: list) -> PIIDetector:
    engine = MagicMock()
    engine.analyze.return_value = results
    detector = PIIDetector.__new__(PIIDetector)
    detector._available = True
    detector._analyzer = engine
    return detector


class TestPresidioNotInstalled:
    def test_detect_returns_empty_when_not_available(self) -> None:
        detector = PIIDetector.__new__(PIIDetector)
        detector._available = False
        detector._analyzer = None
        assert detector.detect("Call me at 555-1234") == []

    def test_empty_text_returns_empty(self) -> None:
        detector = _make_detector([])
        assert detector.detect("") == []


class TestPIIDetection:
    def test_detects_email(self) -> None:
        text = "Email me at alice@example.com please"
        detector = _make_detector([_FakeResult("EMAIL_ADDRESS", 12, 31, score=0.9)])
        matches = detector.detect(text)
        assert len(matches) == 1
        assert matches[0].replacement == "[EMAIL]"
        assert matches[0].label == "email_address"
        assert matches[0].category == "pii"
        assert matches[0].confidence == pytest.approx(0.9)

    def test_detects_phone_number(self) -> None:
        detector = _make_detector([_FakeResult("PHONE_NUMBER", 5, 17, score=0.85)])
        matches = detector.detect("Call 555-867-5309")
        assert matches[0].replacement == "[PHONE_NUMBER]"
        assert matches[0].label == "phone_number"

    def test_detects_person_name(self) -> None:
        detector = _make_detector([_FakeResult("PERSON", 0, 10, score=0.8)])
        matches = detector.detect("John Smith approved this")
        assert matches[0].replacement == "[PERSON]"

    def test_unknown_entity_uses_generic_replacement(self) -> None:
        detector = _make_detector([_FakeResult("WEIRD_ENTITY", 0, 4, score=0.7)])
        matches = detector.detect("some weird thing")
        assert matches[0].replacement == "[WEIRD_ENTITY]"

    def test_ip_address_entity_is_skipped(self) -> None:
        detector = _make_detector([_FakeResult("IP_ADDRESS", 10, 17, score=0.9)])
        assert detector.detect("server at 10.0.0.1") == []

    def test_multiple_entities(self) -> None:
        detector = _make_detector([
            _FakeResult("PERSON", 0, 5, score=0.85),
            _FakeResult("PHONE_NUMBER", 13, 21, score=0.9),
        ])
        matches = detector.detect("Alice called 555-1234")
        assert len(matches) == 2
        assert {m.label for m in matches} == {"person", "phone_number"}
