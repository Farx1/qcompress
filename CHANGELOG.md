# Changelog

All notable changes are listed here. Format:
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). No version has
been released yet.

## [Unreleased]

### Added
- CI on Python 3.10 and 3.11 (CPU torch) with a coverage threshold, ruff via
  pre-commit, Dependabot, `CITATION.cff`, `CONTRIBUTING.md`, `SECURITY.md`.

### Fixed
- Test setup: `pytest.ini` makes `src` importable; `.gitignore` re-encoded
  as UTF-8; committed `.pyc` files removed (#4).
