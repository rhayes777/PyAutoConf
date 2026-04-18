import os
import warnings
from pathlib import Path

from autoconf import exc


class WorkspaceVersionMismatchError(exc.ConfigException):
    pass


def check_version(library_version, workspace_root=None):
    """
    Verify that the workspace at ``workspace_root`` matches ``library_version``.

    Reads ``version.txt`` from ``workspace_root`` (defaults to the current
    working directory, which is where users run workspace scripts from).
    Raises ``WorkspaceVersionMismatchError`` if the file's version differs
    from ``library_version``. If ``version.txt`` does not exist (e.g. an
    older workspace clone or one cloned from ``main`` outside a release tag)
    a warning is emitted and the check is skipped.

    Set ``PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`` to disable the check
    entirely — intended for developers running source checkouts where
    workspace and library versions intentionally diverge.
    """
    if os.environ.get("PYAUTO_SKIP_WORKSPACE_VERSION_CHECK") == "1":
        return

    root = Path(workspace_root) if workspace_root else Path.cwd()
    version_file = root / "version.txt"

    if not version_file.exists():
        warnings.warn(
            f"No version.txt found at {version_file}. Cannot verify that the "
            f"workspace matches the installed library version ({library_version}). "
            f"If you cloned the workspace from main rather than a release tag, "
            f"set PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1 to silence this warning."
        )
        return

    workspace_version = version_file.read_text().strip()

    if workspace_version != library_version:
        raise WorkspaceVersionMismatchError(
            f"Workspace version ({workspace_version}) at {root} does not match "
            f"the installed library version ({library_version}). Re-clone the "
            f"workspace at the matching tag:\n\n"
            f"    git clone --branch {library_version} <workspace-repo-url>\n\n"
            f"Or set PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1 to override (intended "
            f"for source-checkout development)."
        )
