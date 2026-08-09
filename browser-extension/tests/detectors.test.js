const { sanitize } = require("../detectors");

describe("sanitize — secrets", () => {
  test("masks JWT", () => {
    const text = "token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";
    const { clean, matches } = sanitize(text);
    expect(clean).toContain("[JWT]");
    expect(matches[0].label).toBe("jwt");
  });

  test("masks password key=value", () => {
    const { clean } = sanitize("password=s3cr3tP@ss!");
    expect(clean).toBe("[REDACTED]");
  });

  test("masks api_key", () => {
    const { clean } = sanitize("api_key=abcdef1234567890abcdef1234567890");
    expect(clean).toContain("[API_KEY]");
  });

  test("masks bearer token", () => {
    const { clean } = sanitize("Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456");
    expect(clean).toContain("[BEARER_TOKEN]");
  });

  test("clean text returns no matches", () => {
    const { clean, matches } = sanitize("Hello, this is a normal message.");
    expect(clean).toBe("Hello, this is a normal message.");
    expect(matches).toHaveLength(0);
  });
});

describe("sanitize — AWS", () => {
  test("masks AWS access key", () => {
    const { clean, matches } = sanitize("key: AKIAIOSFODNN7EXAMPLE");
    expect(clean).toContain("[AWS_ACCESS_KEY]");
    expect(matches[0].label).toBe("aws_access_key");
  });

  test("masks AWS ARN", () => {
    const { clean } = sanitize("arn:aws:iam::123456789012:user/johndoe");
    expect(clean).toContain("[AWS_ARN]");
  });

  test("masks AWS account ID", () => {
    const { clean } = sanitize("account_id=123456789012");
    expect(clean).toContain("[AWS_ACCOUNT_ID]");
  });
});

describe("sanitize — GCP", () => {
  test("masks GCP API key", () => {
    const { clean } = sanitize("key=AIzaSyD-9tSrke72I6e7KR9lZ5HHaXXXXXXXXXX");
    expect(clean).toContain("[GCP_API_KEY]");
  });
});

describe("sanitize — network", () => {
  test("masks private IPv4", () => {
    const { clean } = sanitize("host: 10.0.1.45");
    expect(clean).toContain("[IP_ADDRESS]");
  });

  test("does not mask public IP", () => {
    const { clean } = sanitize("host: 8.8.8.8");
    expect(clean).toBe("host: 8.8.8.8");
  });

  test("masks internal hostname", () => {
    const { clean } = sanitize("db01.prod.internal");
    expect(clean).toContain("[INTERNAL_HOST]");
  });
});

describe("sanitize — overlap resolution", () => {
  test("higher confidence match wins on overlap", () => {
    // AWS access key overlaps with hex_token — aws_access_key (0.99) should win
    const { matches } = sanitize("AKIAIOSFODNN7EXAMPLE");
    expect(matches.some(m => m.label === "aws_access_key")).toBe(true);
    expect(matches.some(m => m.label === "hex_token")).toBe(false);
  });

  test("multiple non-overlapping matches all replaced", () => {
    const { clean, matches } = sanitize("password=secret host: 10.0.0.1");
    expect(clean).toContain("[REDACTED]");
    expect(clean).toContain("[IP_ADDRESS]");
    expect(matches).toHaveLength(2);
  });
});
