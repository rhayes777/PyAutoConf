import sys
from types import SimpleNamespace
import warnings

import pytest

import autonerves


def _set_python_version(monkeypatch, major, minor):
    monkeypatch.setattr(
        autonerves,
        "sys",
        SimpleNamespace(version_info=(major, minor), stderr=sys.stderr),
    )
    monkeypatch.setattr(
        autonerves,
        "_python_version_check_bypassed",
        lambda: False,
    )


@pytest.mark.parametrize("minor", [12, 13])
def test_supported_python_versions_do_not_warn(monkeypatch, capsys, minor):
    _set_python_version(monkeypatch, major=3, minor=minor)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        autonerves._emit_python_version_warning()

    assert caught == []
    assert capsys.readouterr().err == ""


def test_python_below_minimum_is_reported_as_unsupported(monkeypatch, capsys):
    _set_python_version(monkeypatch, major=3, minor=11)

    with pytest.warns(UserWarning, match=r"require Python >=3\.12"):
        autonerves._emit_python_version_warning()

    message = capsys.readouterr().err
    assert "Python 3.12 or newer is required" in message
    assert "unsupported by current PyAuto releases" in message
    assert "pre-migration PyAuto release" in message


def test_python_above_supported_range_is_reported_as_experimental(monkeypatch, capsys):
    _set_python_version(monkeypatch, major=3, minor=14)

    with pytest.warns(UserWarning, match=r"experimental Python 3\.14"):
        autonerves._emit_python_version_warning()

    message = capsys.readouterr().err
    assert "Python 3.14 detected -- this Python version is experimental" in message
    assert "tests and supports Python 3.12 and 3.13" in message
    assert "Use Python 3.12 or 3.13 for production work" in message


def test_python_version_warning_respects_yaml_bypass(monkeypatch, tmp_path, capsys):
    config_path = tmp_path / "config"
    config_path.mkdir()
    (config_path / "general.yaml").write_text(
        "version:\n  python_version_check: false\n"
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        autonerves,
        "sys",
        SimpleNamespace(version_info=(3, 14)),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        autonerves._emit_python_version_warning()

    assert autonerves._python_version_check_bypassed() is True
    assert caught == []
    assert capsys.readouterr().err == ""
