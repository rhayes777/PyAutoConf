# PyAutoConf

**PyAutoConf** is the configuration management library for the PyAuto ecosystem. It handles object serialization/deserialization via YAML, JSON-based priors and configuration generation, and provides utility tools for scientific Python applications.

- Package name: `autoconf`
- Requires Python >= 3.9

## Repository Structure

- `autoconf/` — Main package
  - `conf.py` — Core configuration system
  - `dictable.py` — Dictionary/serialization support
  - `fitsable.py` — FITS file handling
  - `json_prior/` — JSON-based configuration priors
  - `tools/` — Utility decorators and helpers
  - `mock/` — Mock objects for testing
- `test_autoconf/` — Test suite (pytest)

## Commands

### Install
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
python -m pytest test_autoconf/
python -m pytest test_autoconf/ -s
```

### Codex / sandboxed runs

When running Python from Codex or any restricted environment, set writable cache directories:

```bash
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib python -m pytest test_autoconf/
```

## Line Endings — Always Unix (LF)

All files **must use Unix line endings (LF, `\n`)**. Never write `\r\n` line endings.
