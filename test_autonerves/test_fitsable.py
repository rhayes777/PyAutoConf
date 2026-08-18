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
