// content.js — scrub-ai browser extension
// Intercepts paste events, sanitizes sensitive content, re-injects clean text.

document.addEventListener("paste", (event) => {
  const text = event.clipboardData?.getData("text/plain");
  if (!text) return;

  const { clean, matches } = sanitize(text);
  if (matches.length === 0) return;

  // Prevent the original paste
  event.preventDefault();
  event.stopImmediatePropagation();

  // Insert clean text at the cursor
  const active = document.activeElement;
  if (active && (active.tagName === "TEXTAREA" || active.tagName === "INPUT")) {
    const start = active.selectionStart ?? active.value.length;
    const end = active.selectionEnd ?? active.value.length;
    active.value = active.value.slice(0, start) + clean + active.value.slice(end);
    active.selectionStart = active.selectionEnd = start + clean.length;
    active.dispatchEvent(new Event("input", { bubbles: true }));
  } else if (active?.contentEditable === "true" || active?.isContentEditable === true) {
    document.execCommand("insertText", false, clean);
  }

  console.info(`[scrub-ai] Masked ${matches.length} sensitive value(s):`, matches.map(m => m.label).join(", "));
}, true);
