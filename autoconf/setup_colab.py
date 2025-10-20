import logging
import os
os.environ['XLA_FLAGS'] = "--xla_disable_hlo_passes=constant_folding"

logger = logging.getLogger(__name__)

def check_jax_using_gpu(log_gpu_warning : bool = True) -> bool:

    import jax

    devices = jax.devices()

    # Normalize device_kind for matching
    for d in devices:
        kind = str(d).lower()

        no_gpu = False

        if "gpu" in kind or "cuda" in kind:
            print(f"GPU / CUDA detected: {d}")
        elif "tpu" in kind:
            print(f"TPU detected: {d}")
        elif "cpu" in kind:
            print(f"CPU detected: {d}")
            no_gpu = True
        else:
            print(f"Other device detected: {d}")
            no_gpu = True

    if no_gpu and log_gpu_warning:

        logger.info(
            """
            JAX did not detect a GPU or TPU device and is using the CPU for computations.

            PyAutoLens runs > 50 times faster with a GPU, so it is recommended to reinstall
            JAX With GPU support, if you have a GPU available, by following the JAX 
            installation instructions.
            """)

    return no_gpu

def for_autolens(raise_error_if_not_gpu: bool = True):

    import os
    os.environ['XLA_FLAGS'] = "--xla_disable_hlo_passes=constant_folding"

    import subprocess
    import sys

    try:

        import google.colab

        no_gpu = check_jax_using_gpu(log_gpu_warning=False)

        if no_gpu and raise_error_if_not_gpu:

            raise RuntimeError(
                """
                No GPU detected in Google Colab. PyAutoLens runs > 50 times faster with a GPU, so switch GPU 
                on in Colab settings.

                To do this:

                - Click "Runtime" in the top menu.
                - Click "Change runtime type".
                - Under "Hardware accelerator", select one of the "GPU" options available.

                You can set up Colab with a CPU (e.g. if GPUs are unavailable)  by uncommenting the 
                line "raise_error_if_not_gpu=False" in the setup_colab() function call.
                """
            )

    except ImportError:
        print(
            """
            You are not running in a Google Colab environment so cannot use the setup_colab() function.

            You should therefore have PyAutoLens installed locally in your environment already (e.g. via pip or 
            conda and can run the rest of your script normally).
            
            You may now continue running your script or Notebook.
            """
        )
        return

    print()
    print("Now Installing PyAutoLens and setting up Colab Environment:")

    # Install required packages
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "autoconf", "autofit", "autoarray", "autogalaxy", "autolens",
                           "pyvis==0.3.2", "dill==0.4.0", "jaxnnls",
                           "pyprojroot==0.2.0", "nautilus-sampler==1.0.4",
                           "timeout_decorator==0.5.0", "anesthetic==2.8.14",
                           "--no-deps"])

    from autoconf import conf

    try:
        subprocess.run([
            "git", "clone", "https://github.com/Jammy2211/autolens_workspace"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print("Workspace already exists so not cloning again.")

    os.chdir("/content/autolens_workspace")

    conf.instance.push(
        new_path="/content/autolens_workspace/config",
        output_path="/content/autolens_workspace/output",
    )

    print(
        """
        ***Google Colab Setup Complete, which included:***

        - Installation of PyAutoLens and other required packages.
        - Cloning of the autolens_workspace GitHub repository.
        - Setting up environment variables for JAX for improved performance.
        - Setting the configuration paths to the workspace config and output folders suitable for Colab.
        """
    )