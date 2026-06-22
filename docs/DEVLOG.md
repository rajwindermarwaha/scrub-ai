# scrub-ai — Developer Log

A running log of every step taken to build scrub-ai, what was done, and why.

---

## Step 1 — Project planning docs pushed to GitHub
**What:** Created README, PLAN, ARCHITECTURE, DECISIONS, CONTRIBUTING, and .gitignore. Pushed to GitHub.

**Why:** Before writing any code, document the problem, the solution, the tech stack, and the architecture. This prevents wasted effort building the wrong thing. It also makes the repo look credible from day one.

---

## Step 2 — Created `feature/v1-core` branch
**What:** Created a new Git branch called `feature/v1-core` and pushed it to GitHub.

**Why:** All v1 code goes on this branch, not on `main`. This keeps `main` stable and clean. The rule is: only merge into `main` when the feature is fully working and tested. This is standard Git workflow (called feature branching).

---
