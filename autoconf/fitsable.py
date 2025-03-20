from __future__ import annotations
from astropy.io import fits
import numpy as np
from typing import TYPE_CHECKING, Optional, Union

from autoconf import conf


def hdu_for_output_from(
    array_2d: np.ndarray,
    header_dict: Optional[dict] = None,
    ext_name: Optional[str] = None,
    return_as_primary: bool = False,
) -> Union[fits.PrimaryHDU, fits.ImageHDU]:
    """
    Returns the HDU which can be used to output an array to a .fits file.

    Before outputting a NumPy array, the array may be flipped upside-down using np.flipud depending on the project
    config files. This is for Astronomy projects so that structures appear the same orientation as ``.fits`` files
    loaded in DS9.

    The output .fits files may contain multiple HDUs comprising different images. Conventionally, the first array,
    the `PrimaryHDU`, contains the 2D mask applied to the data and the remaining HDUs contain the data itself.

    Parameters
    ----------
    array_2d
        The 2D array that is written to fits.
    header_dict
        A dictionary of values that are written to the header of the .fits file.
    ext_name
        The name of the extension in the fits file, which displays in the header of the fits file and is visible
        for example when the .fits is loaded in DS9.
    return_as_primary
        Whether the HDU is returned as a PrimaryHDU or ImageHDU.

    Returns
    -------
    hdu
        The HDU containing the data and its header which can then be written to .fits.

    Examples
    --------
    array_2d = np.ones((5,5))
    hdu_for_output_from(array_2d=array_2d, header_dict={"Example": 0.5}, ext_name="data", return_as_primary=True)
    """
    header = fits.Header()

    header["EXTNAME"] = ext_name.upper()

    if header_dict is not None:
        for key, value in header_dict.items():
            header.append((key, value, [""]))

    flip_for_ds9 = conf.instance["general"]["fits"]["flip_for_ds9"]

    if flip_for_ds9:
        array_2d = np.flipud(array_2d)

    if return_as_primary:
        return fits.PrimaryHDU(array_2d, header=header)
    return fits.ImageHDU(array_2d, header=header)