// content.test.js — tests for paste interception logic
// Uses jsdom to simulate DOM elements and paste events.

const { sanitize } = require("../detectors");

// Inline the paste handler logic (mirrors content.js) so we can test it without a real browser
function handlePaste(event, activeElement) {
  const text = event.clipboardData?.getData("text/plain");
  if (!text) return false;

  const { clean, matches } = sanitize(text);
  if (matches.length === 0) return false;

  event.preventDefault();
  event.stopImmediatePropagation();

  if (activeElement && (activeElement.tagName === "TEXTAREA" || activeElement.tagName === "INPUT")) {
    const start = activeElement.selectionStart ?? activeElement.value.length;
    const end = activeElement.selectionEnd ?? activeElement.value.length;
    activeElement.value = activeElement.value.slice(0, start) + clean + activeElement.value.slice(end);
    activeElement.selectionStart = activeElement.selectionEnd = start + clean.length;
    activeElement.dispatchEvent(new Event("input", { bubbles: true }));
  } else if (activeElement?.contentEditable === "true" || activeElement?.isContentEditable === true) {
    activeElement.textContent += clean;
  }

  return { clean, matches };
}

function makePasteEvent(text) {
  return {
    clipboardData: { getData: (type) => type === "text/plain" ? text : "" },
    preventDefault: jest.fn(),
    stopImmediatePropagation: jest.fn(),
  };
}

describe("content script — textarea paste", () => {
  test("sanitizes sensitive text pasted into textarea", () => {
    const el = document.createElement("textarea");
    el.value = "prefix: ";
    el.selectionStart = el.selectionEnd = el.value.length;

    const event = makePasteEvent("password=s3cr3t");
    const result = handlePaste(event, el);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(result.matches).toHaveLength(1);
    expect(el.value).toBe("prefix: [REDACTED]");
  });

  test("inserts clean text at cursor position (mid-string)", () => {
    const el = document.createElement("textarea");
    el.value = "before  after";
    el.selectionStart = 7;
    el.selectionEnd = 7;

    const event = makePasteEvent("api_key=abc123def456ghi789jkl012");
    handlePaste(event, el);

    expect(el.value).toContain("[API_KEY]");
  });

  test("does not intercept clean text", () => {
    const el = document.createElement("textarea");
    el.value = "";

    const event = makePasteEvent("Hello, this is safe text.");
    const result = handlePaste(event, el);

    expect(event.preventDefault).not.toHaveBeenCalled();
    expect(result).toBe(false);
    expect(el.value).toBe("");
  });

  test("does not intercept empty paste", () => {
    const el = document.createElement("textarea");
    const event = makePasteEvent("");
    const result = handlePaste(event, el);

    expect(result).toBe(false);
    expect(event.preventDefault).not.toHaveBeenCalled();
  });

  test("fires input event after sanitized paste", () => {
    const el = document.createElement("textarea");
    el.value = "";
    el.selectionStart = el.selectionEnd = 0;

    const inputFired = jest.fn();
    el.addEventListener("input", inputFired);

    const event = makePasteEvent("password=hunter2");
    handlePaste(event, el);

    expect(inputFired).toHaveBeenCalled();
  });

  test("cursor positioned after inserted text", () => {
    const el = document.createElement("textarea");
    el.value = "";
    el.selectionStart = el.selectionEnd = 0;

    const event = makePasteEvent("password=hunter2");
    handlePaste(event, el);

    expect(el.selectionStart).toBe(el.value.length);
    expect(el.selectionEnd).toBe(el.value.length);
  });
});

describe("content script — contentEditable paste", () => {
  test("sanitizes sensitive text pasted into contentEditable div", () => {
    const el = document.createElement("div");
    el.contentEditable = "true";
    document.body.appendChild(el);
    el.textContent = "";

    const event = makePasteEvent("AKIAIOSFODNN7EXAMPLE");
    const result = handlePaste(event, el);

    expect(event.preventDefault).toHaveBeenCalled();
    expect(result.matches[0].label).toBe("aws_access_key");
    expect(el.textContent).toContain("[AWS_ACCESS_KEY]");
  });

  test("does not intercept clean text in contentEditable", () => {
    const el = document.createElement("div");
    el.contentEditable = "true";

    const event = makePasteEvent("just a normal message");
    const result = handlePaste(event, el);

    expect(result).toBe(false);
    expect(event.preventDefault).not.toHaveBeenCalled();
  });
});

describe("content script — multiple matches", () => {
  test("all sensitive values replaced in one paste", () => {
    const el = document.createElement("textarea");
    el.value = "";
    el.selectionStart = el.selectionEnd = 0;

    const event = makePasteEvent("password=secret\nhost: 10.0.0.1\nkey: AKIAIOSFODNN7EXAMPLE");
    const result = handlePaste(event, el);

    expect(result.matches.length).toBeGreaterThanOrEqual(3);
    expect(el.value).toContain("[REDACTED]");
    expect(el.value).toContain("[IP_ADDRESS]");
    expect(el.value).toContain("[AWS_ACCESS_KEY]");
  });
});
