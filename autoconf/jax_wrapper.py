import logging

logger = logging.getLogger(__name__)

import os

xla_env = os.environ.get("XLA_FLAGS")

xla_env_set = True

if xla_env is None:
    xla_env_set = False
elif isinstance(xla_env, str):
    xla_env_set = "--xla_disable_hlo_passes=constant_folding" in xla_env

if not xla_env_set:
    logger.info(
        """
        For fast JAX compile times, the envirment variable XLA_FLAGS must be set to "--xla_disable_hlo_passes=constant_folding",
        which is currently not.
        
        In Python, to do this manually, use the code: 
        
        import os
        os.environ["XLA_FLAGS"] = "--xla_disable_hlo_passes=constant_folding"
        
        The environment variable has been set automatically for you now, however if JAX has already been imported, 
        this change will not take effect and JAX function compiling times may be slow. 
        
        Therefore, it is recommended to set this environment variable before running your script, e.g. in your terminal.
        """)

    os.environ['XLA_FLAGS'] = "--xla_disable_hlo_passes=constant_folding"

jax_enable_x64 = os.environ.get("JAX_ENABLE_X64")

if jax_enable_x64 is None:
    jax_enable_x64 = False
elif isinstance(jax_enable_x64, str):
    jax_enable_x64 = jax_enable_x64.lower() == "true"

if not jax_enable_x64:

    os.environ["JAX_ENABLE_X64"] = "True"

    logger.info(
        """"
        JAX 64-bit precision has been automatically enabled for you (JAX_ENABLE_X64=True),
        as double precision is required for most scientific computing applications.
        
        To enable 64 precision as default in JAX, set the environment variable 
        JAX_ENABLE_X64=true before running your script.
        """
    )
