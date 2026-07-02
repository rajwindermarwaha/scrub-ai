from __future__ import annotations
import re
from .base import BaseDetector


class CloudDetector(BaseDetector):
    name = "cloud"
    priority = 2
    patterns = [
        # ── AWS ──────────────────────────────────────────────────────────────

        # AWS Access Key IDs (AKIA / ASIA / AROA / AIDA / ANPA / ANVA / APKA prefixes)
        (re.compile(r"\b(?:AKIA|ASIA|AROA|AIDA|ANPA|ANVA|APKA)[0-9A-Z]{16}\b"), "[AWS_ACCESS_KEY_ID]", "aws_access_key_id", 1.0),

        # AWS Secret Access Keys — 40-char base64 in key=value context
        (re.compile(r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]?([A-Za-z0-9+/]{40})['\"]?"), "[AWS_SECRET_ACCESS_KEY]", "aws_secret_access_key", 0.95),

        # AWS Account IDs — 12-digit numbers in ARN or account= context
        (re.compile(r"(?i)(?:account[_-]?id|aws[_-]?account)\s*[=:]\s*['\"]?(\d{12})['\"]?"), "[AWS_ACCOUNT_ID]", "aws_account_id", 0.90),

        # ARNs — arn:aws:service:region:account-id:resource
        (re.compile(r"\barn:aws[a-z0-9-]*:[a-z0-9\-]*:[a-z0-9\-]*:\d{12}:[^\s\"']+"), "[AWS_ARN]", "aws_arn", 1.0),

        # AWS Session Tokens (base64, 100–300 chars, in token= context)
        (re.compile(r"(?i)(?:aws[_-]?session[_-]?token|session[_-]?token)\s*[=:]\s*['\"]?([A-Za-z0-9+/=]{100,300})['\"]?"), "[AWS_SESSION_TOKEN]", "aws_session_token", 0.95),

        # ── GCP ──────────────────────────────────────────────────────────────

        # GCP API keys (AIza prefix, 39 chars total)
        (re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), "[GCP_API_KEY]", "gcp_api_key", 1.0),

        # GCP service account email
        (re.compile(r"\b[a-z0-9\-]+@[a-z0-9\-]+\.iam\.gserviceaccount\.com\b"), "[GCP_SERVICE_ACCOUNT]", "gcp_service_account", 1.0),

        # GCP project IDs in project= / project_id= context
        (re.compile(r"(?i)(?:project[_-]?id|gcp[_-]?project)\s*[=:]\s*['\"]?([a-z][a-z0-9\-]{4,28}[a-z0-9])['\"]?"), "[GCP_PROJECT_ID]", "gcp_project_id", 0.80),

        # ── Azure ─────────────────────────────────────────────────────────────

        # Azure Subscription / Tenant / Client IDs (UUIDs in context)
        (re.compile(r"(?i)(?:subscription[_-]?id|tenant[_-]?id|client[_-]?id)\s*[=:]\s*['\"]?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})['\"]?"), "[AZURE_ID]", "azure_id", 0.90),

        # Azure Client Secrets (34-char random string in client_secret= context)
        (re.compile(r"(?i)client[_-]?secret\s*[=:]\s*['\"]?([A-Za-z0-9~._\-]{34,})['\"]?"), "[AZURE_CLIENT_SECRET]", "azure_client_secret", 0.85),

        # Azure Storage connection strings
        (re.compile(r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{88};[^\s\"']*"), "[AZURE_STORAGE_CONNECTION_STRING]", "azure_storage_connection_string", 1.0),

        # Azure SAS tokens (sv=...&sig=... in URL or standalone)
        (re.compile(r"(?i)(?:sv|se|sr|sp|sig)=[A-Za-z0-9%+/=]+(?:&(?:sv|se|sr|sp|sig)=[A-Za-z0-9%+/=]+){3,}"), "[AZURE_SAS_TOKEN]", "azure_sas_token", 0.95),
    ]
