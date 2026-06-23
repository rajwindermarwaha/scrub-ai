# Contributing to scrub-ai

Thank you for your interest in contributing! This document explains how to get started.

---

## Development Setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/scrub-ai
cd scrub-ai

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate   # macOS/Linux

# 3. Install in development mode with dev dependencies
pip install -e ".[dev]"

# 4. Run the tests to make sure everything works
pytest
```

---

## How to Contribute

### Adding a new detector pattern

1. Find the relevant detector in `scrub_ai/detectors/`
2. Add your regex pattern to the `patterns` list
3. Add a test case in `tests/fixtures/` with sample text that should match
4. Add a test in the relevant `tests/test_*_detector.py` file
5. Open a PR

### Adding a new detector category

1. Create `scrub_ai/detectors/your_category.py`
2. Inherit from `BaseDetector`
3. Register it in `scrub_ai/sanitizer.py`
4. Add tests
5. Open a PR

---

## Code Style

- Follow PEP 8
- Type hints on all functions
- Docstrings on all classes and public methods
- Tests required for all new patterns and detectors

---

## Questions?

Open an issue on GitHub.
