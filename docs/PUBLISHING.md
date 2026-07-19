# scrub-ai — Publishing Guide

How to publish a new version to PyPI. Follow these steps in order every time.

---

## Checklist

### Step 1 — Finish the feature branch

- All code written and tested
- `pytest -q` passes with zero failures
- `docs/PROGRESS.md` and `docs/DEVLOG.md` updated

### Step 2 — Bump the version

Update the version number in **both** files:

- `pyproject.toml` → `version = "X.Y.Z"`
- `scrub_ai/__init__.py` → `__version__ = "X.Y.Z"`

Both must match. Forgetting either one causes the wrong version to be built and uploaded.

### Step 3 — Commit and push the version bump

```bash
git add pyproject.toml scrub_ai/__init__.py
git commit -m "chore: bump version to X.Y.Z"
git push origin feature/vX.Y
```

### Step 4 — Merge to main

```bash
git checkout main
git merge feature/vX.Y
git push origin main
```

### Step 5 — Run the publish workflow

1. Go to the repo on GitHub → **Actions** → **Publish**
2. Click **Run workflow**
3. Enter the version (e.g. `1.2.0`) → click **Run workflow**

The workflow runs two jobs:

| Job | What it does |
|---|---|
| `publish-test` | Builds the package and uploads to TestPyPI automatically |
| `publish-pypi` | Waits for your approval, then uploads to real PyPI |

### Step 6 — Approve the PyPI release

Once `publish-test` succeeds, GitHub will send you an approval request email.

1. Open the Actions run
2. Click **Review deployments**
3. Check the TestPyPI upload looks correct
4. Click **Approve and deploy**

### Step 7 — Verify the release

```bash
# Install from PyPI in a clean environment to confirm it works
pip install scrub-ai==X.Y.Z
echo "password=test123" | scrub-ai
```

---

## Common mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Forgot to bump version | Upload rejected with `400 Bad Request` — same version already exists | Bump version in both files, commit, push, re-run workflow |
| Bumped only one file | Wrong version shown on PyPI or in `scrub-ai --version` | Always update both `pyproject.toml` and `scrub_ai/__init__.py` |
| Pushed to feature branch, not main | CI passes but publish workflow not visible or runs on stale code | Merge to main first, then run the workflow |
| Re-uploading same version to TestPyPI | `400 Bad Request` from test.pypi.org | TestPyPI does not allow re-uploads — bump to a new version |

---

## Secrets and access

The publish workflow uses two GitHub Actions secrets:

| Secret | Used for |
|---|---|
| `TEST_PYPI_API_TOKEN` | Uploading to https://test.pypi.org |
| `PYPI_API_TOKEN` | Uploading to https://pypi.org |

These are stored in **Settings → Secrets and variables → Actions** on the GitHub repo. Only the repo owner can read or update them.

The `publish-pypi` job is protected by the `release` environment — only the required reviewer (repo owner) can approve it.
