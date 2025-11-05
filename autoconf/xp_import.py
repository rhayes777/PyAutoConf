import contextlib
import numpy as np
import jax
import jax.numpy as jnp


def get_xp(*args, **kwargs):
    for x in jax.tree_util.tree_leaves((args, kwargs)):
        if isinstance(x, jax.core.Tracer):
            return jnp
    return np

@contextlib.contextmanager
def _temporary_xp_binding(fn_globals, xp):
    old_xp = fn_globals.get("xp", None)
    fn_globals["xp"] = xp
    try:
        yield
    finally:
        if old_xp is None:
            del fn_globals["xp"]
        else:
            fn_globals["xp"] = old_xp

def auto_xp(fn):
    def wrapped(*args, **kwargs):
        xp = get_xp(args, kwargs)
        with _temporary_xp_binding(fn.__globals__, xp):
            return fn(*args, **kwargs)
    return wrapped
