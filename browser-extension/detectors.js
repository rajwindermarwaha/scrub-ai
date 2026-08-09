// detectors.js — scrub-ai browser extension
// Ports core regex patterns from the Python CLI to JavaScript.
// Exposes a single function: sanitize(text) -> { clean, matches }

const PATTERNS = [
  // --- Secrets ---
  { label: "private_key",    re: /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/g, replacement: "[PRIVATE_KEY]",    confidence: 0.99 },
  { label: "jwt",            re: /eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g,                                                    replacement: "[JWT]",            confidence: 0.99 },
  { label: "bearer_token",   re: /[Bb]earer\s+([a-zA-Z0-9\-._~+/]{20,})/g,                                                                    replacement: "[BEARER_TOKEN]",   confidence: 0.95 },
  { label: "password",       re: /(?:password|passwd|pwd)\s*[:=]\s*\S+/gi,                                                                     replacement: "[REDACTED]",       confidence: 0.95 },
  { label: "api_key",        re: /(?:api_key|api_token|access_token|secret_key)\s*[:=]\s*\S+/gi,                                               replacement: "[API_KEY]",        confidence: 0.95 },
  { label: "hex_token",      re: /\b[0-9a-f]{32,64}\b/g,                                                                                       replacement: "[HEX_TOKEN]",      confidence: 0.75 },

  // --- AWS --- (listed before hex_token in priority; higher confidence wins overlap resolution)
  { label: "aws_access_key", re: /\b(AKIA|ASIA|AROA|AIDA|ANPA|ANVA|AIPA)[A-Z0-9]{16}\b/g,                                                     replacement: "[AWS_ACCESS_KEY]", confidence: 0.99 },
  { label: "aws_secret_key", re: /(?:aws_secret_access_key|aws_secret)\s*[:=]\s*[A-Za-z0-9/+=]{40}/gi,                                         replacement: "[AWS_SECRET_KEY]", confidence: 0.99 },
  { label: "aws_account_id", re: /(?:account_id|aws_account)\s*[:=]\s*\d{12}/gi,                                                               replacement: "[AWS_ACCOUNT_ID]", confidence: 0.95 },
  { label: "aws_arn",        re: /arn:aws:[a-z0-9\-]+:[a-z0-9\-]*:\d{12}:[^\s]+/g,                                                            replacement: "[AWS_ARN]",        confidence: 0.99 },

  // --- GCP ---
  { label: "gcp_api_key",    re: /AIza[0-9A-Za-z\-_]{35}/g,                                                                                   replacement: "[GCP_API_KEY]",    confidence: 0.99 },

  // --- Azure ---
  { label: "azure_sub_id",   re: /(?:subscription_id|tenant_id|client_id)\s*[:=]\s*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, replacement: "[AZURE_ID]", confidence: 0.95 },

  // --- Network ---
  { label: "ipv4",           re: /\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b/g, replacement: "[IP_ADDRESS]", confidence: 0.90 },
  { label: "internal_host",  re: /\b[\w-]+\.(?:internal|local|corp|lan)\b/gi,                                                                  replacement: "[INTERNAL_HOST]",  confidence: 0.85 },
];

/**
 * Sanitize text — replace all sensitive matches.
 * @param {string} text
 * @returns {{ clean: string, matches: Array<{label, original, replacement, start, end}> }}
 */
function sanitize(text) {
  const found = [];

  // Collect all matches with positions
  for (const { label, re, replacement, confidence } of PATTERNS) {
    re.lastIndex = 0;
    let m;
    while ((m = re.exec(text)) !== null) {
      found.push({ label, original: m[0], replacement, confidence, start: m.index, end: m.index + m[0].length });
    }
  }

  if (found.length === 0) return { clean: text, matches: [] };

  // Sort by start position, resolve overlaps (higher confidence wins)
  found.sort((a, b) => a.start - b.start || b.confidence - a.confidence);
  const resolved = [];
  let cursor = 0;
  for (const match of found) {
    if (match.start >= cursor) {
      resolved.push(match);
      cursor = match.end;
    }
  }

  // Apply replacements from end to start to preserve offsets
  let clean = text;
  for (const match of [...resolved].reverse()) {
    clean = clean.slice(0, match.start) + match.replacement + clean.slice(match.end);
  }

  return { clean, matches: resolved };
}

// Export for Jest (Node), no-op in browser
if (typeof module !== "undefined") module.exports = { sanitize, PATTERNS };
