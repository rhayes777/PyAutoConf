# Copilot Coding Agent Instructions

You are working on **PyAutoConf**, the configuration management library for the PyAuto ecosystem.

## Key Rules

- Run tests after every change: `python -m pytest test_autoconf/`
- All files must use Unix line endings (LF, `\n`)
- If changing public API (function signatures, class names, import paths), clearly document what changed in your PR description — all downstream PyAuto packages depend on this

## Architecture

- `autoconf/conf.py` — Core configuration system
- `autoconf/dictable.py` — Dictionary/serialization support
- `autoconf/fitsable.py` — FITS file handling
- `autoconf/json_prior/` — JSON-based configuration priors
- `autoconf/tools/` — Utility decorators and helpers
- `test_autoconf/` — Test suite

## Sandboxed runs

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python -m pytest test_autoconf/
```
