from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrub_ai.detectors.custom import CustomPatternDetector


def _write_patterns(path: Path, entries: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries), encoding="utf-8")


class TestNoFile:
    def test_returns_empty_when_file_missing(self, tmp_path) -> None:
        detector = CustomPatternDetector(patterns_file=tmp_path / "nonexistent.json")
        assert detector.detect("anything here") == []


class TestValidPatterns:
    def test_detects_matching_pattern(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [{"pattern": r"ticket-\d{6}", "replacement": "[TICKET]", "label": "internal_ticket"}])
        detector = CustomPatternDetector(patterns_file=f)
        matches = detector.detect("See ticket-123456 for details")
        assert len(matches) == 1
        assert matches[0].original == "ticket-123456"
        assert matches[0].replacement == "[TICKET]"
        assert matches[0].label == "internal_ticket"
        assert matches[0].category == "custom"

    def test_default_replacement_and_label(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [{"pattern": r"CORP-\d+"}])
        detector = CustomPatternDetector(patterns_file=f)
        matches = detector.detect("ref CORP-42")
        assert matches[0].replacement == "[CUSTOM]"
        assert matches[0].label == "custom"

    def test_confidence_is_loaded(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [{"pattern": r"CORP-\d+", "confidence": 0.75}])
        detector = CustomPatternDetector(patterns_file=f)
        matches = detector.detect("ref CORP-42")
        assert matches[0].confidence == pytest.approx(0.75)

    def test_multiple_patterns(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [
            {"pattern": r"ticket-\d+", "label": "ticket"},
            {"pattern": r"deploy-\d+", "label": "deploy"},
        ])
        detector = CustomPatternDetector(patterns_file=f)
        matches = detector.detect("ticket-1 and deploy-2 today")
        assert {m.label for m in matches} == {"ticket", "deploy"}

    def test_no_match_returns_empty(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [{"pattern": r"ticket-\d+"}])
        detector = CustomPatternDetector(patterns_file=f)
        assert detector.detect("nothing relevant here") == []


class TestMalformedFile:
    def test_invalid_json_returns_empty(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        f.write_text("not valid json", encoding="utf-8")
        detector = CustomPatternDetector(patterns_file=f)
        assert detector.detect("anything") == []

    def test_invalid_regex_skips_silently(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [{"pattern": r"[invalid("}])
        detector = CustomPatternDetector(patterns_file=f)
        assert detector.detect("anything") == []

    def test_empty_array_returns_empty(self, tmp_path) -> None:
        f = tmp_path / "patterns.json"
        _write_patterns(f, [])
        detector = CustomPatternDetector(patterns_file=f)
        assert detector.detect("anything") == []
