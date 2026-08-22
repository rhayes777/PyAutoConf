import pytest

from astropy.io import fits
import numpy as np
import os
from pathlib import Path

from autonerves import conf
from autonerves import fitsable

test_path = Path(__file__).resolve().parent

test_data_path = Path(__file__).resolve().parent / "files"


def create_fits(fits_path, array):
    fits_path = Path(fits_path)
    if fits_path.exists():
        os.remove(fits_path)

    hdu_list = fits.HDUList()

    hdu_list.append(fits.ImageHDU(array))

    hdu_list.writeto(f"{fits_path}")



def test__ndarray_via_fits_from():
    arr = fitsable.ndarray_via_fits_from(
        file_path=test_data_path / "3x3_ones.fits", hdu=0
    )

    assert (arr == np.ones((3, 3))).all()

    arr = fitsable.ndarray_via_fits_from(
        file_path=test_data_path / "4x3_ones.fits", hdu=0
    )

    assert (arr == np.ones((4, 3))).all()


def test__output_to_fits():
    file_path = test_data_path / "array_out.fits"

    if file_path.exists():
        os.remove(file_path)

    arr = np.array([[10.0, 30.0, 40.0], [92.0, 19.0, 20.0]])

    fitsable.output_to_fits(arr, file_path=file_path)

    array_load = fitsable.ndarray_via_fits_from(file_path=file_path, hdu=0)

    assert (arr == array_load).all()


def test__output_to_fits__header_dict():
    file_path = test_data_path / "array_out.fits"

    if file_path.exists():
        os.remove(file_path)

    arr = np.array([[10.0, 30.0, 40.0], [92.0, 19.0, 20.0]])

    fitsable.output_to_fits(arr, file_path=file_path, header_dict={"A": 1})

    header = fitsable.header_obj_from(file_path=file_path, hdu=0)

    assert header["A"] == 1


def test__fits_readers_close_their_file_handles():
    """Regression: `fits.open` without close leaked file handles, emitting
    `ResourceWarning: unclosed file` throughout every downstream repo that
    loads FITS via these helpers."""
    import gc
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error", ResourceWarning)
        fitsable.ndarray_via_fits_from(
            file_path=test_data_path / "3x3_ones.fits", hdu=0
        )
        fitsable.header_obj_from(file_path=test_data_path / "3x3_ones.fits", hdu=0)
        gc.collect()


def test__header_obj_from():
    header_obj = fitsable.header_obj_from(
        file_path=test_data_path / "3x3_ones.fits", hdu=0
    )

    assert isinstance(header_obj, fits.header.Header)
    assert header_obj["BITPIX"] == -64


"""
__small-datasets regime stamp (PyAutoNerves#153)__

`PYAUTO_SMALL_DATASETS=1` caps simulated datasets to a reduced resolution.
Nothing else on disk records that, so a capped dataset can survive into a later
full-resolution run and be loaded silently (autolens_workspace_test#260). The
stamp records the regime in the same call that writes the data, which makes it
truthful by construction and -- unlike a shape heuristic -- able to catch
corruption that leaves the shape unchanged.

Both funnels are covered below because they are genuinely separate paths:
`output_to_fits` builds and writes in one call, while the multi-HDU dataset
writers in PyAutoArray build via `hdu_list_for_output_from` and write via
`write_hdu_list`, never touching `output_to_fits`.
"""

KEY = fitsable.SMALL_DATASETS_HEADER_KEY


def _stamp(file_path, hdu=0):
    with fits.open(file_path) as hdu_list:
        return hdu_list[hdu].header.get(KEY)


def test__output_to_fits__stamps_the_regime(tmp_path, monkeypatch):
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "1")
    fitsable.output_to_fits(np.ones((4, 4)), file_path=tmp_path / "small.fits")
    assert _stamp(tmp_path / "small.fits") is True

    monkeypatch.delenv("PYAUTO_SMALL_DATASETS", raising=False)
    fitsable.output_to_fits(np.ones((4, 4)), file_path=tmp_path / "full.fits")
    assert _stamp(tmp_path / "full.fits") is False


def test__stamp_is_written_in_both_regimes__absence_is_never_full(
    tmp_path, monkeypatch
):
    # The full regime is recorded EXPLICITLY as F rather than by omission.
    # That is the whole point: a reader can then tell "known full" from "no
    # idea", and only the first is safe to act on. If F were encoded as
    # absence, every legacy dataset would masquerade as full resolution and
    # the original bug would come straight back.
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "0")
    fitsable.output_to_fits(np.ones((4, 4)), file_path=tmp_path / "zero.fits")

    assert KEY in fits.open(tmp_path / "zero.fits")[0].header
    assert _stamp(tmp_path / "zero.fits") is False


def test__stamp_round_trips_as_a_fits_boolean_not_a_string(tmp_path, monkeypatch):
    # Readers distinguish True/False/absent and must never coerce: bool("F")
    # is True. Pin the on-disk type so a future change to the header-writing
    # path cannot silently downgrade the card to a string or a float.
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "1")
    fitsable.output_to_fits(np.ones((4, 4)), file_path=tmp_path / "t.fits")

    value = fits.open(tmp_path / "t.fits")[0].header[KEY]
    assert isinstance(value, bool)
    assert "SMALLDAT=                    T" in str(
        fits.open(tmp_path / "t.fits")[0].header.cards[KEY]
    )


def test__multi_hdu_funnel__stamps_every_hdu(tmp_path, monkeypatch):
    # The path PyAutoArray's fits_imaging/fits_interferometer take when given a
    # single `file_path` -- it bypasses output_to_fits entirely.
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "1")

    hdu_list = fitsable.hdu_list_for_output_from(
        values_list=[np.ones((4, 4)), np.zeros((4, 4))],
        ext_name_list=["data", "noise_map"],
    )
    fitsable.write_hdu_list(hdu_list, file_path=tmp_path / "dataset.fits")

    assert _stamp(tmp_path / "dataset.fits", hdu=0) is True
    assert _stamp(tmp_path / "dataset.fits", hdu=1) is True


def test__write_hdu_list__stamps_an_hdu_list_built_elsewhere(tmp_path, monkeypatch):
    # write_hdu_list is the terminal write, so it must stamp even an HDUList
    # this module did not construct -- `hdu_list_for_output_from` is publicly
    # re-exported as `aa.hdu_list_for_output_from`, so callers can and do build
    # their own.
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "1")

    hdu_list = fits.HDUList([fits.PrimaryHDU(np.ones((4, 4)))])
    fitsable.write_hdu_list(hdu_list, file_path=tmp_path / "raw.fits")

    assert _stamp(tmp_path / "raw.fits") is True


def test__stamp_does_not_disturb_header_dict_entries(tmp_path, monkeypatch):
    # The stamp rides alongside the mask's PIXSCAY/PIXSCAX/ORIGINY/ORIGINX
    # cards; it must not displace or overwrite any of them.
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "1")

    fitsable.output_to_fits(
        np.ones((4, 4)),
        file_path=tmp_path / "h.fits",
        header_dict={"PIXSCAY": 0.5, "PIXSCAX": 0.5, "ORIGINY": 0.0, "ORIGINX": 0.0},
    )

    header = fits.open(tmp_path / "h.fits")[0].header
    assert header["PIXSCAY"] == 0.5
    assert header["PIXSCAX"] == 0.5
    assert header[KEY] is True


def test__stamp_is_idempotent_across_both_funnels(tmp_path, monkeypatch):
    # hdu_list_for_output_from and write_hdu_list BOTH stamp, and output_to_fits
    # goes through both. Assignment (not append) keeps that from duplicating the
    # card -- a duplicate would make header[KEY] ambiguous.
    monkeypatch.setenv("PYAUTO_SMALL_DATASETS", "1")
    fitsable.output_to_fits(np.ones((4, 4)), file_path=tmp_path / "once.fits")

    header = fits.open(tmp_path / "once.fits")[0].header
    assert len([c for c in header.cards if c.keyword == KEY]) == 1


def test__stamp_key_stays_within_the_fits_standard_card_limit():
    # Not stylistic. A 9-char keyword is silently promoted to a HIERARCH card
    # by astropy rather than raising, and header.get() by the short name then
    # returns None -- which readers treat as "unknown regime" and fall back to
    # the shape heuristic. An over-long key would therefore not fail loudly, it
    # would quietly un-fix the interferometer case. Pin the ceiling.
    assert len(KEY) <= 8
    assert KEY == KEY.upper()
