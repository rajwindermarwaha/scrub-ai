from scrub_ai.detectors.secrets import SecretsDetector


def _labels(matches):
    return {m.label for m in matches}


def _replacements(matches):
    return {m.replacement for m in matches}


def test_detects_common_secret_patterns() -> None:
    detector = SecretsDetector()
    text = (
        "Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456\n"
        "api_key=abcdefghijklmno123456789\n"
        "password=SuperSecret123\n"
        "jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIn0."
        "c2lnbmF0dXJlMTIzNDU2Nzg5MA\n"
        "token=0123456789abcdef0123456789abcdef\n"
    )

    matches = detector.detect(text)
    labels = _labels(matches)
    replacements = _replacements(matches)

    assert "bearer_token" in labels
    assert "api_key" in labels
    assert "password" in labels
    assert "jwt" in labels
    assert "hex_token" in labels

    assert "[BEARER_TOKEN]" in replacements
    assert "[API_KEY]" in replacements
    assert "[REDACTED]" in replacements
    assert "[JWT]" in replacements
    assert "[TOKEN]" in replacements


def test_detects_private_key_block() -> None:
    detector = SecretsDetector()
    text = (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvAIBADANBgkqhkiG9w0BAQEFAASC...\n"
        "-----END PRIVATE KEY-----\n"
    )

    matches = detector.detect(text)
    labels = _labels(matches)

    assert "private_key" in labels
