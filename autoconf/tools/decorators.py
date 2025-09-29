import jax.numpy as jnp
import numpy as np

def get_xp(x):
    if isinstance(x, np.ndarray) or isinstance(x, float):
        return np
    elif isinstance(x, tuple):
        if isinstance(x[0], np.ndarray or isinstance(x[0], float)):
            return np
    return jnp

def xp_cast(arr):
    """
    Ensure arrays are consistently handled in a NumPy + JAX mixed environment.

    This helper casts only *NumPy* arrays to `numpy.ndarray`, leaving JAX
    arrays (e.g. `jax.Array`) unchanged. It is useful when writing code that
    supports both backends but needs to avoid accidentally converting JAX
    arrays into NumPy and thus breaking JIT/vmap/pmap compilation.

    Parameters
    ----------
    arr : numpy.ndarray or jax.Array
        Input array to normalize.

    Returns
    -------
    numpy.ndarray or jax.Array
        If `arr` is a NumPy array, returns a fresh `numpy.ndarray` copy (to
        standardize dtype/stride handling). If `arr` is already a JAX array,
        returns it unchanged so it can flow through JAX transforms.
    """
    if isinstance(arr, np.ndarray):
        return np.array(arr)
    return arr

def xp_add(arr, idx, vals):
    """
    Scatter-add for both NumPy and JAX backends.

    Parameters
    ----------
    xp : module
        Either `numpy` or `jax.numpy`.
    size : int or tuple
        Shape of the output array.
    idx : array
        Indices to add into.
    vals : array
        Values to add at the given indices.
    dtype : type
        Data type of the output array.

    Returns
    -------
    out : array
        Result of scatter-add.
    """
    if isinstance(arr, np.ndarray):
        np.add.at(arr, idx, vals)
        return arr
    return arr.at[idx].add(vals)

def xp_set(arr, idx, vals):
    """
    Scatter-set for both NumPy and JAX backends.

    Parameters
    ----------
    arr : array
        Input array to update.
    idx : array or tuple
        Indices to set.
    vals : array
        Values to assign at the given indices.

    Returns
    -------
    out : array
        Result of scatter-set.
    """
    if isinstance(arr, np.ndarray):
        arr[idx] = vals
        return arr
    # JAX: use .at[].set
    return arr.at[idx].set(vals)

class CachedProperty(object):
    """
    A property that is only computed once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property.

    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self.func.__name__ not in obj.__dict__:
            obj.__dict__[self.func.__name__] = self.func(obj)
        return obj.__dict__[self.func.__name__]


cached_property = CachedProperty
