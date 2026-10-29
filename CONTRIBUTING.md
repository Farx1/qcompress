# Contributing

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt pytest-cov pre-commit
pre-commit install
```

## Before opening a pull request

```bash
python -m pytest --cov=src      # same command as CI
pre-commit run --all-files      # ruff
```

CI (`.github/workflows/ci.yml`) runs the tests on Python 3.10 and 3.11 with
CPU-only torch and fails if line coverage of `src/` drops below the
threshold set there. Raise the threshold when you add tests; never lower it
to make a PR pass.

## Conventions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`).
- One topic per pull request. Add an entry under *Unreleased* in
  `CHANGELOG.md`.
- New numerical code needs a test against a dense or closed-form reference,
  not only a shape check.
- Any number quoted in the README must be reproducible from a script in
  `scripts/` with the exact command next to it.
