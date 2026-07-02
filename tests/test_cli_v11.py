from __future__ import annotations

from click.testing import CliRunner

from scrub_ai.cli import main


class TestProfileFlag:
    def test_aws_suppresses_network_detection(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--profile", "aws"], input="host=10.0.0.1\n")
        assert result.exit_code == 0
        assert "10.0.0.1" in result.output

    def test_k8s_suppresses_cloud_detection(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--profile", "k8s"],
                               input="sa=myapp@myproject.iam.gserviceaccount.com\n")
        assert result.exit_code == 0
        assert "myapp@myproject.iam.gserviceaccount.com" in result.output

    def test_secrets_profile_detects_passwords(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--profile", "secrets"], input="password=hunter2\n")
        assert result.exit_code == 0
        assert "hunter2" not in result.output

    def test_invalid_profile_exits_with_error(self) -> None:
        runner = CliRunner()
        result = runner.invoke(main, ["--profile", "bogus"], input="anything\n")
        assert result.exit_code != 0


class TestMinConfidenceFlag:
    def test_high_min_confidence_filters_hex_token(self) -> None:
        runner = CliRunner()
        # hex_token confidence is 0.70 -- threshold 0.80 should suppress it
        result = runner.invoke(main, ["--min-confidence", "0.80"],
                               input="0123456789abcdef0123456789abcdef\n")
        assert result.exit_code == 0
        assert "0123456789abcdef0123456789abcdef" in result.output

    def test_min_confidence_keeps_high_confidence_matches(self) -> None:
        runner = CliRunner()
        # JWT confidence is 1.0 -- always caught
        result = runner.invoke(main, ["--min-confidence", "0.95"],
                               input="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c\n")
        assert result.exit_code == 0
        assert "[JWT]" in result.output
