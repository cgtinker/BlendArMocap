# thanks @robertguetzkow
import os
import sys
import subprocess
import importlib
from collections import namedtuple

Dependency = namedtuple("Dependency", ["module", "package", "name"])
dependencies = (Dependency(module="mediapipe", package=None, name=None),
               Dependency(module="opencv-python", package=None, name="cv2"))


global dependencies_installed
dependencies_installed = False


def import_module(module_name, global_name=None, reload=True):
    """
    Import a module.
    :param module_name: Module to import.
    :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
       This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
       the global_name under which the module can be accessed.
    :raises: ImportError and ModuleNotFoundError
    """
    print("Trying to import module")
    if global_name is None:
        global_name = module_name

    if global_name in globals():
        print("load module from globals")
        importlib.reload(globals()[global_name])

    else:
        print("assign to globals")
        # Attempt to import the module and assign it to globals dictionary.
        globals()[global_name] = importlib.import_module(global_name)


def install_pip():
    """
    Installs pip if not already present. Please note that ensurepip.bootstrap() also calls pip, which adds the
    environment variable PIP_REQ_TRACKER. After ensurepip.bootstrap() finishes execution, the directory doesn't exist
    anymore. However, when subprocess is used to call pip, in order to install a package, the environment variables
    still contain PIP_REQ_TRACKER with the now nonexistent path. This is a problem since pip checks if PIP_REQ_TRACKER
    is set and if it is, attempts to use it as temp directory. This would result in an error because the
    directory can't be found. Therefore, PIP_REQ_TRACKER needs to be removed from environment variables.
    :return:
    """

    try:
        print("accessing pip installer")
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip
        print("installing pip installer")
        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)


def install_and_import_module(module_name, package_name=None, global_name=None):
    """
    Installs the package through pip and attempts to import the installed module.
    :param module_name: Module to import.
    :param package_name: (Optional) Name of the package that needs to be installed. If None it is assumed to be equal
       to the module_name.
    :param global_name: (Optional) Name under which the module is imported. If None the module_name will be used.
       This allows to import under a different name with the same effect as e.g. "import numpy as np" where "np" is
       the global_name under which the module can be accessed.
    :raises: subprocess.CalledProcessError and ImportError
    """
    if package_name is None:
        package_name = module_name

    if global_name is None:
        global_name = module_name

    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"
    print("Try to install:", package_name, environ_copy["PYTHONNOUSERSITE"])
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True, env=environ_copy)
    except Exception:
        print("INSTALL USING SUPER USER")
        subprocess.run([sys.executable, "-m", "pip", "install", package_name, "--user"], check=True, env=environ_copy)
    print("Installation process finished")
    # The installation succeeded, attempt to import the module again
    import_module(module_name, global_name)
