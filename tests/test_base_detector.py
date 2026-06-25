import re

from scrub_ai.detectors.base import BaseDetector


class DummyDetector(BaseDetector):
    name = "dummy"
    priority = 99
    patterns = [
        (re.compile(r"secret"), "[SECRET]", "secret_word"),
        (re.compile(r"\d+"), "[NUMBER]", "number"),
    ]


def test_detect_returns_empty_list_for_no_matches() -> None:
    detector = DummyDetector()

    matches = detector.detect("nothing sensitive here")

    assert matches == []


def test_detect_populates_match_fields_correctly() -> None:
    detector = DummyDetector()
    text = "my secret is safe"

    matches = detector.detect(text)

    assert len(matches) == 1
    match = matches[0]
    assert match.start == 3
    assert match.end == 9
    assert match.original == "secret"
    assert match.replacement == "[SECRET]"
    assert match.category == "dummy"
    assert match.label == "secret_word"
    assert match.confidence == 1.0


def test_detect_supports_multiple_patterns_and_occurrences() -> None:
    detector = DummyDetector()
    text = "secret 123 and 456"

    matches = detector.detect(text)
    labels = [m.label for m in matches]

    assert len(matches) == 3
    assert labels.count("secret_word") == 1
    assert labels.count("number") == 2
