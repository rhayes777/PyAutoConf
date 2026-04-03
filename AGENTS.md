# PyAutoConf — Agent Instructions

**PyAutoConf** is the configuration management library for the PyAuto ecosystem. It handles object serialization/deserialization, JSON-based priors, and configuration generation.

## Setup

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest test_autoconf/
```

### Sandboxed / Codex runs

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python -m pytest test_autoconf/
```

## Key Architecture

- `autoconf/conf.py` — Core configuration system
- `autoconf/dictable.py` — Dictionary/serialization support for YAML
- `autoconf/fitsable.py` — FITS file handling
- `autoconf/json_prior/` — JSON-based configuration priors
- `autoconf/tools/` — Utility decorators and helpers
- `autoconf/mock/` — Mock objects for testing

## Key Rules

- All files must use Unix line endings (LF)
- If changing public API, note it in your PR description — all downstream PyAuto packages depend on this

## Working on Issues

1. Read the issue description and any linked plan.
2. Identify affected files and write your changes.
3. Run the full test suite: `python -m pytest test_autoconf/`
4. Ensure all tests pass before opening a PR.
5. If changing public API, clearly document what changed — PyAutoFit, PyAutoArray, PyAutoGalaxy, and PyAutoLens all depend on this package.
