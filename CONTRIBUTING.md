# Contributing to Localhost Doctor

Thanks for helping make localhost debugging less painful! The easiest and most
valuable contributions are **new symptom patterns** — no Python expertise needed.

## Adding a symptom to the knowledge base

The knowledge base lives at
[`src/localhost_doctor/kb/symptoms.yaml`](src/localhost_doctor/kb/symptoms.yaml).
Each entry maps error text patterns to a title, likely causes, and fixes:

```yaml
- match: ["your error text fragment", "another spelling users see"]
  title: Short error name
  causes:
    - Why this usually happens
  fixes:
    - The concrete thing to try first
    - The fallback
```

Good fields to cover for a new tool (Laragon, Docker Desktop, nginx, Postgres,
IIS...):

- The **exact error string** users see (copy it from a real log — this is what
  gets matched).
- The **log file location** for that component, if your symptom is diagnosed
  from logs.
- Fixes ordered from **least to most destructive**.

Then add a test case in `tests/` mirroring the existing symptom tests, and run:

```bash
pip install -e ".[dev]"  # or: pip install -e . pytest
pytest
```

Open a PR with a one-line description of the failure mode you added.

## Other contributions

- **Stack layouts**: support for detecting XAMPP/WAMP/Laragon installs in
  non-standard directories.
- **Platforms**: diagnostics currently target Windows; Linux/macOS equivalents
  for process/port checks are welcome.
- **Bug reports**: open an issue with the tool call you ran, the raw output, and
  what your stack was actually doing — raw log excerpts are gold.

## Ground rules

- All diagnostics are **read-only**. Don't submit code that mutates system
  state without explicit user confirmation (that's the v2 guarded-fixes design).
- Keep the knowledge base plain-English: the audience is a beginner whose
  localhost just broke, not a sysadmin.
