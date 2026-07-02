from __future__ import annotations

from scrub_ai.detectors.base import BaseDetector

PROFILES: dict[str, list[str]] = {
    "aws": ["secrets", "cloud"],
    "k8s": ["secrets", "network"],
    "secrets": ["secrets"],
    "network": ["network"],
}


def available_profiles() -> list[str]:
    return sorted(PROFILES)


def get_detectors_for_profile(profile: str) -> list[BaseDetector]:
    from scrub_ai.detectors import SecretsDetector, CloudDetector, NetworkDetector
    from scrub_ai.detectors.custom import CustomPatternDetector
    from scrub_ai.detectors.pii import PIIDetector

    key = profile.lower()
    if key not in PROFILES:
        raise ValueError(
            f"Unknown profile: {profile!r}. "
            f"Available profiles: {', '.join(available_profiles())}"
        )

    _category_map: dict[str, type[BaseDetector]] = {
        "secrets": SecretsDetector,
        "cloud": CloudDetector,
        "network": NetworkDetector,
    }

    detectors: list[BaseDetector] = [_category_map[name]() for name in PROFILES[key]]
    detectors.append(CustomPatternDetector())
    detectors.append(PIIDetector())
    return detectors
