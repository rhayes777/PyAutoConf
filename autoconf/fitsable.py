from __future__ import annotations
from astropy.io import fits
import numpy as np
from typing import Optional, Union, List

from autoconf import conf


def hdu_list_for_output_from(
    values_list: List[np.ndarray],
    header_dict: Optional[dict] = None,
    ext_name_list: Optional[List[str]] = None,
) -> fits.HDUList:
    """
    Returns the HDU list which can be used to output arrays to a .fits file.

    Before outputting each NumPy array, the array may be flipped upside-down using np.flipud depending on the project
    config files. This is for Astronomy projects so that structures appear the same orientation as ``.fits`` files
    loaded in DS9.

    The output .fits files may contain multiple HDUs comprising different images. Conventionally, the first array,
    the `PrimaryHDU`, contains the 2D mask applied to the data and the remaining HDUs contain the data itself.
    The mask is used to add information to the header, for example the pixel scale of the data.
    
    Each HDU contains its `ext_name` in the header, which is visible when the .fits file is loaded in DS9.

    Parameters
    ----------
    values
        The 1D or 2D array that is written to fits.
    header_dict
        A dictionary of values that are written to the header of the .fits file.
    ext_name_list
        The names of the extension in the fits file, which displays in the header of the fits file and is visible
        for example when the .fits is loaded in DS9.

    Returns
    -------
    The HDU list containing the data and its header which can then be written to .fits.

    Examples
    --------
    data = np.ones((5,5))
    noise_map = np.ones((5,5))

    hdu_list_for_output_from(
        values_list=[data, noise_map]
        header_dict={"Example": 0.5},
        ext_name_list=["data", "noise_map"]
    )
    """
    hdu_list = []
    
    header = fits.Header()

    if header_dict is not None:
        for key, value in header_dict.items():
            header.append((key, value, [""]))
    
    for i, values in enumerate(values_list):
    
        if ext_name_list is not None:
            header["EXTNAME"] = ext_name_list[i].upper()
    
        if len(values.shape) > 1:
    
            flip_for_ds9 = conf.instance["general"]["fits"]["flip_for_ds9"]
    
            if flip_for_ds9:
                values = np.flipud(values)
                
        if i == 0:
            hdu_list.append(fits.PrimaryHDU(values, header=header))
        else:
            hdu_list.append(fits.ImageHDU(values, header=header))
         
    return fits.HDUList(hdus=hdu_list)