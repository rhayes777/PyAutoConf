# PyAutoConf

**PyAutoConf** is the configuration management library for the PyAuto ecosystem. It handles object serialization/deserialization via YAML, JSON-based priors and configuration generation, and provides utility tools for scientific Python applications.

- Package name: `autoconf`
- Requires Python >= 3.12

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
## Never rewrite history

NEVER perform these operations on any repo with a remote:

- `git init` in a directory already tracked by git
- `rm -rf .git && git init`
- Commit with subject "Initial commit", "Fresh start", "Start fresh", "Reset
  for AI workflow", or any equivalent message on a branch with a remote
- `git push --force` to `main` (or any branch tracked as `origin/HEAD`)
- `git filter-repo` / `git filter-branch` on shared branches
- `git rebase -i` rewriting commits already pushed to a shared branch

If the working tree needs a clean state, the **only** correct sequence is:

    git fetch origin
    git reset --hard origin/main
    git clean -fd

This applies equally to humans, local Claude Code, cloud Claude agents, Codex,
and any other agent. The "Initial commit — fresh start for AI workflow" pattern
that appeared independently on origin and local for three workspace repos is
exactly what this rule prevents — it costs ~40 commits of redundant local work
every time it happens.
