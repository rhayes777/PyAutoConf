import os
import warnings
from pathlib import Path

from autoconf import exc


class WorkspaceVersionMismatchError(exc.ConfigException):
    pass


_BYPASS_ENV_VAR = "PYAUTO_SKIP_WORKSPACE_VERSION_CHECK"


def _read_general_yaml(workspace_root):
    """
    Return the parsed ``config/general.yaml`` dict for ``workspace_root``.

    Returns an empty dict on any failure (missing file, missing yaml module,
    unreadable YAML) so the caller can fall through to legacy ``version.txt``
    handling without crashing the user's script on import.
    """
    try:
        import yaml

        config_path = workspace_root / "config" / "general.yaml"
        with config_path.open("r") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _yaml_bypass_set(general_yaml):
    return general_yaml.get("version", {}).get("workspace_version_check") is False


def _yaml_workspace_version(general_yaml):
    value = general_yaml.get("version", {}).get("workspace_version")
    if value is None:
        return None
    return str(value).strip()


def _missing_version_warning(workspace_root, library_version):
    return (
        f"Cannot verify the workspace at {workspace_root} matches the "
        f"installed library version ({library_version}): no "
        f"`version.workspace_version` key in config/general.yaml and no "
        f"version.txt at the workspace root.\n\n"
        f"If you cloned the workspace from `main` rather than a release tag, "
        f"set `version.workspace_version_check: False` in "
        f"config/general.yaml to silence this warning. The `main` branch "
        f"updates more frequently than library releases, so version "
        f"mismatches are expected and not actionable for `main`-branch users.\n\n"
        f"You can also set the environment variable "
        f"{_BYPASS_ENV_VAR}=1 to disable temporarily."
    )


def _mismatch_message(workspace_version, library_version, workspace_root):
    return (
        f"Workspace version ({workspace_version}) at {workspace_root} does "
        f"not match the installed library version ({library_version}).\n\n"
        f"This usually means your installed library was upgraded but your "
        f"workspace clone is from an older release tag. Re-clone the "
        f"workspace at the matching tag:\n\n"
        f"    git clone --branch {library_version} <workspace-repo-url>\n\n"
        f"To bypass this check, edit config/general.yaml:\n\n"
        f"    version:\n"
        f"      workspace_version_check: False\n\n"
        f"IMPORTANT: If you cloned the workspace from `main` rather than a "
        f"release tag, you should set `workspace_version_check: False`. The "
        f"`main` branch updates much more frequently than library releases, "
        f"so version mismatches are expected and not actionable for "
        f"`main`-branch users.\n\n"
        f"You can also set the environment variable "
        f"{_BYPASS_ENV_VAR}=1 to disable temporarily."
    )


def check_version(library_version, workspace_root=None):
    """
    Verify that the workspace at ``workspace_root`` matches ``library_version``.

    Resolves the workspace version with the following precedence:

    1. ``config/general.yaml`` — ``version.workspace_version`` key, written by
       the release pipeline. Travels with the user's config directory even
       when scripts are copy-pasted out of the workspace root.
    2. ``version.txt`` at the workspace root — legacy fallback for clones
       that pre-date the YAML key.

    If neither source is found, a warning is emitted and the check is
    skipped. If both sources exist but disagree, the YAML value wins
    (release pipeline writes both atomically; YAML is the configured
    source-of-truth on the user's machine).

    The check can be disabled in two ways:

    * Set ``version.workspace_version_check: False`` in
      ``config/general.yaml`` — the recommended path for users on
      ``main``-branch workspace clones, where mismatches are expected
      because ``main`` updates more frequently than library releases.
    * Set ``PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`` — intended for
      developers running source checkouts where workspace and library
      versions intentionally diverge.

    Defaults ``workspace_root`` to the current working directory, which is
    where users run workspace scripts from.
    """
    if os.environ.get(_BYPASS_ENV_VAR) == "1":
        return

    root = Path(workspace_root) if workspace_root else Path.cwd()

    general_yaml = _read_general_yaml(root)

    if _yaml_bypass_set(general_yaml):
        return

    workspace_version = _yaml_workspace_version(general_yaml)

    if workspace_version is None:
        version_file = root / "version.txt"
        if version_file.exists():
            workspace_version = version_file.read_text().strip()

    if workspace_version is None or workspace_version == "":
        warnings.warn(_missing_version_warning(root, library_version))
        return

    if workspace_version != library_version:
        raise WorkspaceVersionMismatchError(
            _mismatch_message(workspace_version, library_version, root)
        )
