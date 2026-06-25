from scrub_ai.detectors.network import NetworkDetector


def _labels(matches):
    return {m.label for m in matches}


def _replacements(matches):
    return {m.replacement for m in matches}


def test_detects_ipv4_and_ipv6_addresses() -> None:
    detector = NetworkDetector()
    text = "Public: 8.8.8.8, Private: 10.0.1.45, IPv6: 2001:db8::1"

    matches = detector.detect(text)

    labels = _labels(matches)
    replacements = _replacements(matches)

    assert "ipv4_address" in labels
    assert "ipv6_address" in labels
    assert "[IP_ADDRESS]" in replacements


def test_detects_internal_hostname_and_url() -> None:
    detector = NetworkDetector()
    text = "host=db01.prod.internal url=https://db01.prod.internal:8443/health"

    matches = detector.detect(text)
    labels = _labels(matches)

    assert "internal_hostname" in labels
    assert "internal_url" in labels
