from __future__ import annotations

import pytest

from scrub_ai.profiles import available_profiles, get_detectors_for_profile
from scrub_ai.detectors import SecretsDetector, CloudDetector, NetworkDetector
from scrub_ai.detectors.custom import CustomPatternDetector
from scrub_ai.detectors.pii import PIIDetector


class TestAvailableProfiles:
    def test_returns_sorted_list(self) -> None:
        profiles = available_profiles()
        assert profiles == sorted(profiles)

    def test_includes_expected_profiles(self) -> None:
        profiles = available_profiles()
        for p in ("aws", "k8s", "secrets", "network"):
            assert p in profiles


class TestGetDetectorsForProfile:
    def _types(self, profile: str) -> list:
        return [type(d) for d in get_detectors_for_profile(profile)]

    def test_aws_includes_secrets_and_cloud(self) -> None:
        types = self._types("aws")
        assert SecretsDetector in types
        assert CloudDetector in types
        assert NetworkDetector not in types

    def test_k8s_includes_secrets_and_network(self) -> None:
        types = self._types("k8s")
        assert SecretsDetector in types
        assert NetworkDetector in types
        assert CloudDetector not in types

    def test_secrets_profile(self) -> None:
        types = self._types("secrets")
        assert SecretsDetector in types
        assert CloudDetector not in types
        assert NetworkDetector not in types

    def test_network_profile(self) -> None:
        types = self._types("network")
        assert NetworkDetector in types
        assert SecretsDetector not in types

    def test_custom_and_pii_always_included(self) -> None:
        for profile in available_profiles():
            types = self._types(profile)
            assert CustomPatternDetector in types
            assert PIIDetector in types

    def test_unknown_profile_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown profile"):
            get_detectors_for_profile("bogus")

    def test_case_insensitive(self) -> None:
        assert self._types("aws") == self._types("AWS")
