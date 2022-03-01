# thanks @robertguetzkow
import importlib
import os
import subprocess
import sys
from pathlib import Path
from collections import namedtuple

import bpy.app

Dependency = namedtuple("Dependency", ["module", "package", "name"])
dependencies = (Dependency(module="mediapipe", package=None, name=None),
                Dependency(module="opencv-python", package=None, name="cv2"))

global dependencies_installed
dependencies_installed = False


def python_exe():
    version = bpy.app.version

    # blender vers =< 2.91 contain a path to their py executable
    if version[0] == 2 and version[1] <= 91:
        executable = bpy.app.binary_path_python
    # newer versions sys.executable should point to the py executable
    else:
        executable = sys.executable

    # some version point to the binary path instead of the py executable
    if executable == bpy.app.binary_path:
        py_path = Path(sys.prefix) / "bin"
        py_exec = next(py_path.glob("python*"))  # first file that starts with "python" in "bin" dir
        executable = str(py_exec)

    return executable


def import_module(module_name, global_name=None, reload=True):
    if global_name is None:
        global_name = module_name

    if global_name in globals():
        importlib.reload(globals()[global_name])

    else:
        # Attempt to import the module and assign it to globals dictionary.
        globals()[global_name] = importlib.import_module(global_name)


def install_pip():
    try:
        print("accessing pip installer")
        subprocess.run([python_exe(), "-m", "pip", "--version"], check=True)
        # subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        import ensurepip
        print("installing pip installer")
        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)


def update_pip():
    subprocess.call([python_exe(), "-m", "pip", "install", "--upgrade", "pip"])
    # subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])


def install_and_import_module(module_name, package_name=None, global_name=None):
    if package_name is None:
        package_name = module_name

    if global_name is None:
        global_name = module_name

    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"
    print("Try to install:", package_name)
    try:
        subprocess.run([python_exe(), "-m", "pip", "install", package_name], check=True, env=environ_copy)
        # subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True, env=environ_copy)
    except Exception as e:
        print("INSTALL USING --USER TAG\n", e)
        subprocess.run([python_exe(), "-m", "pip", "install", package_name], check=True, env=environ_copy)
        # subprocess.run([sys.executable, "-m", "pip", "install", package_name, "--user"], check=True, env=environ_copy)
    print("Installation process finished")
    # The installation succeeded, attempt to import the module again
    import_module(module_name, global_name)
