from scrub_ai.detectors.cloud import CloudDetector


def _labels(matches):
    return {m.label for m in matches}


def _replacements(matches):
    return {m.replacement for m in matches}


def test_detects_aws_gcp_and_azure_core_patterns() -> None:
    detector = CloudDetector()
    text = (
        "aws_access_key=AKIA1234567890ABCDEF\n"
        "account_id=123456789012\n"
        "arn=arn:aws:iam::123456789012:role/Admin\n"
        "gcp_key=AIza12345678901234567890123456789012345\n"
        "svc=service-account@myproj.iam.gserviceaccount.com\n"
        "project_id=my-scrub-project\n"
        "subscription_id=123e4567-e89b-12d3-a456-426614174000\n"
        "client_secret=abcdefghijklmnopqrstuvwxyzABCDEFGH12\n"
    )

    matches = detector.detect(text)
    labels = _labels(matches)
    replacements = _replacements(matches)

    assert "aws_access_key_id" in labels
    assert "aws_account_id" in labels
    assert "aws_arn" in labels
    assert "gcp_api_key" in labels
    assert "gcp_service_account" in labels
    assert "gcp_project_id" in labels
    assert "azure_id" in labels
    assert "azure_client_secret" in labels

    assert "[AWS_ACCESS_KEY_ID]" in replacements
    assert "[AWS_ACCOUNT_ID]" in replacements
    assert "[AWS_ARN]" in replacements
    assert "[GCP_API_KEY]" in replacements
    assert "[GCP_SERVICE_ACCOUNT]" in replacements
    assert "[GCP_PROJECT_ID]" in replacements
    assert "[AZURE_ID]" in replacements
    assert "[AZURE_CLIENT_SECRET]" in replacements


def test_detects_aws_secret_and_session_token_context_patterns() -> None:
    detector = CloudDetector()
    aws_secret = "A" * 40
    session_token = "B" * 120
    text = (
        f"aws_secret_access_key={aws_secret}\n"
        f"aws_session_token={session_token}\n"
    )

    matches = detector.detect(text)
    labels = _labels(matches)

    assert "aws_secret_access_key" in labels
    assert "aws_session_token" in labels
