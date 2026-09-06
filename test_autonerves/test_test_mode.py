"""Tests for autonerves.test_mode helpers — focused on
``with_test_mode_segment`` since the other helpers (``is_test_mode``,
``skip_fit_output``, etc.) are exercised by PyAutoFit/PyAutoArray
integration tests downstream."""

import os
from pathlib import Path

import pytest

from autonerves.test_mode import (
    SMALL_DATASETS_SHAPE_NATIVE,
    disable_jax,
    is_test_mode,
    with_test_mode_segment,
)

# ``test_mode_samples`` is real API, but its ``test_`` prefix means a bare-name
# import here would be collected by pytest as a test function
# (PytestReturnNotNoneWarning, an ERROR in future pytest) — alias it instead.
from autonerves.test_mode import test_mode_samples as _test_mode_samples


@pytest.fixture(autouse=True)
def _restore_test_mode_env():
    """Save/restore PYAUTO_TEST_MODE around each test so a failure
    can't leak state to its neighbours."""

    saved = os.environ.get("PYAUTO_TEST_MODE")
    yield
    if saved is None:
        os.environ.pop("PYAUTO_TEST_MODE", None)
    else:
        os.environ["PYAUTO_TEST_MODE"] = saved


def test_with_test_mode_segment__env_unset_returns_base_unchanged():
    os.environ.pop("PYAUTO_TEST_MODE", None)
    assert with_test_mode_segment(Path("output")) == Path("output")


def test_with_test_mode_segment__env_zero_returns_base_unchanged():
    """``PYAUTO_TEST_MODE=0`` is the documented off state, so the
    helper must treat it the same as unset (no test_mode segment)."""
    os.environ["PYAUTO_TEST_MODE"] = "0"
    assert is_test_mode() is False
    assert with_test_mode_segment(Path("output")) == Path("output")


@pytest.mark.parametrize("level", ["1", "2", "3"])
def test_with_test_mode_segment__env_set_inserts_segment(level):
    os.environ["PYAUTO_TEST_MODE"] = level
    assert with_test_mode_segment(Path("output")) == Path("output") / "test_mode"


def test_with_test_mode_segment__chains_with_pathlib_concat():
    """The helper's return value must compose with further ``/`` ops so
    workspace scripts can write ``with_test_mode_segment(base) / 'name'``
    in a single line."""
    os.environ["PYAUTO_TEST_MODE"] = "2"
    composed = with_test_mode_segment(Path("output")) / "results_folder"
    assert composed == Path("output") / "test_mode" / "results_folder"


class TestTestModeSamples:
    @pytest.fixture(autouse=True)
    def _restore_samples_env(self):
        saved = os.environ.get("PYAUTO_TEST_MODE_SAMPLES")
        yield
        if saved is None:
            os.environ.pop("PYAUTO_TEST_MODE_SAMPLES", None)
        else:
            os.environ["PYAUTO_TEST_MODE_SAMPLES"] = saved

    def test__env_unset_returns_historical_default_of_four(self):
        os.environ.pop("PYAUTO_TEST_MODE_SAMPLES", None)
        assert _test_mode_samples() == 4

    def test__env_set_returns_value(self):
        os.environ["PYAUTO_TEST_MODE_SAMPLES"] = "50000"
        assert _test_mode_samples() == 50000

    def test__values_below_four_raise(self):
        os.environ["PYAUTO_TEST_MODE_SAMPLES"] = "3"
        with pytest.raises(ValueError):
            _test_mode_samples()


class TestDisableJax:
    """``PYAUTO_DISABLE_JAX`` is the documented global switch for forcing the
    NumPy path. It had no predicate before this class existed, which is why it
    was honoured in exactly one place in the stack while two workspace guides
    documented it as global."""

    def test__env_unset_is_false(self, monkeypatch):
        monkeypatch.delenv("PYAUTO_DISABLE_JAX", raising=False)

        assert disable_jax() is False

    def test__env_one_is_true(self, monkeypatch):
        monkeypatch.setenv("PYAUTO_DISABLE_JAX", "1")

        assert disable_jax() is True

    @pytest.mark.parametrize("value", ["0", "true", "True", "yes", ""])
    def test__only_the_exact_string_one_enables_it(self, monkeypatch, value):
        # Matching every other PYAUTO_* switch in the module: a truthy-looking
        # string is not "1", and reading it as one would silently disable JAX
        # for anyone who wrote PYAUTO_DISABLE_JAX=0 to mean "no".
        monkeypatch.setenv("PYAUTO_DISABLE_JAX", value)

        assert disable_jax() is False


def test__small_datasets_cap_shape_is_the_two_axis_tuple_readers_compare():
    # The cap is stamped into FITS headers as "<rows>x<cols>" and compared back
    # against this constant by ``autoarray.util.dataset_util``. Pin its shape
    # and type: a scalar or a 3-tuple here would produce a card no reader can
    # parse, which reads as "absent" and silently un-fixes the re-simulation
    # case the card exists for.
    assert isinstance(SMALL_DATASETS_SHAPE_NATIVE, tuple)
    assert len(SMALL_DATASETS_SHAPE_NATIVE) == 2
    assert all(isinstance(axis, int) for axis in SMALL_DATASETS_SHAPE_NATIVE)
