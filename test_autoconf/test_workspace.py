import pytest

from autoconf.workspace import check_version, WorkspaceVersionMismatchError


def test_match(tmp_path):
    (tmp_path / "version.txt").write_text("2026.4.13.6\n")
    check_version("2026.4.13.6", workspace_root=tmp_path)


def test_mismatch_raises(tmp_path):
    (tmp_path / "version.txt").write_text("2026.4.13.6\n")
    with pytest.raises(WorkspaceVersionMismatchError) as info:
        check_version("2025.1.1.1", workspace_root=tmp_path)
    assert "2026.4.13.6" in str(info.value)
    assert "2025.1.1.1" in str(info.value)


def test_missing_file_warns(tmp_path):
    with pytest.warns(UserWarning, match="No version.txt"):
        check_version("2026.4.13.6", workspace_root=tmp_path)


def test_env_override_skips_mismatch(tmp_path, monkeypatch):
    monkeypatch.setenv("PYAUTO_SKIP_WORKSPACE_VERSION_CHECK", "1")
    (tmp_path / "version.txt").write_text("2025.1.1.1\n")
    check_version("2026.4.13.6", workspace_root=tmp_path)


def test_env_override_skips_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("PYAUTO_SKIP_WORKSPACE_VERSION_CHECK", "1")
    check_version("2026.4.13.6", workspace_root=tmp_path)


def test_default_root_is_cwd(tmp_path, monkeypatch):
    (tmp_path / "version.txt").write_text("2026.4.13.6\n")
    monkeypatch.chdir(tmp_path)
    check_version("2026.4.13.6")
