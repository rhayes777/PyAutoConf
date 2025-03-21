import pytest

from astropy.io import fits
import numpy as np
import os
from os import path

from autoconf import conf
from autoconf import fitsable

test_path = "{}".format(path.dirname(path.realpath(__file__)))

test_data_path = os.path.join(
    "{}".format(os.path.dirname(os.path.realpath(__file__))), "files"
)


def create_fits(fits_path, array):
    if path.exists(fits_path):
        os.remove(fits_path)

    hdu_list = fits.HDUList()

    hdu_list.append(fits.ImageHDU(array))

    hdu_list.writeto(f"{fits_path}")


def test__from_fits__all_imaging_data_structures_are_flipped_for_ds9():
    conf.instance.push(new_path=path.join(test_path, "files", "config_flip"))

    fits_path = path.join("{}".format(path.dirname(path.realpath(__file__))), "files")

    arr = np.array([[1.0, 0.0], [0.0, 0.0]])
    array_path = path.join(fits_path, "array.fits")
    create_fits(fits_path=array_path, array=arr)

    arr = fitsable.ndarray_via_fits_from(file_path=array_path, hdu=0)
    assert (arr.native == np.array([[0.0, 0.0], [1.0, 0.0]])).all()

    arr.output_to_fits(file_path=array_path, overwrite=True)

    hdu_list = fits.open(array_path)
    arr = np.array(hdu_list[0].data).astype("float64")
    assert (arr == np.array([[1.0, 0.0], [0.0, 0.0]])).all()


def test__ndarray_via_fits_from():
    arr = fitsable.ndarray_via_fits_from(
        file_path=os.path.join(test_data_path, "3x3_ones.fits"), hdu=0
    )

    assert (arr == np.ones((3, 3))).all()

    arr = fitsable.ndarray_via_fits_from(
        file_path=os.path.join(test_data_path, "4x3_ones.fits"), hdu=0
    )

    assert (arr == np.ones((4, 3))).all()


def test__output_to_fits():
    file_path = os.path.join(test_data_path, "array_out.fits")

    if os.path.exists(file_path):
        os.remove(file_path)

    arr = np.array([[10.0, 30.0, 40.0], [92.0, 19.0, 20.0]])

    fitsable.output_to_fits(arr, file_path=file_path)

    array_load = fitsable.ndarray_via_fits_from(file_path=file_path, hdu=0)

    assert (arr == array_load).all()


def test__output_to_fits__header_dict():
    file_path = os.path.join(test_data_path, "array_out.fits")

    if os.path.exists(file_path):
        os.remove(file_path)

    arr = np.array([[10.0, 30.0, 40.0], [92.0, 19.0, 20.0]])

    fitsable.output_to_fits(arr, file_path=file_path, header_dict={"A": 1})

    header = fitsable.header_obj_from(file_path=file_path, hdu=0)

    assert header["A"] == 1


def test__header_obj_from():
    header_obj = fitsable.header_obj_from(
        file_path=os.path.join(test_data_path, "3x3_ones.fits"), hdu=0
    )

    assert isinstance(header_obj, fits.header.Header)
    assert header_obj["BITPIX"] == -64
