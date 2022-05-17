# thanks @robertguetzkow
import importlib
import os
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

import bpy.app


# region python executable and site-packages
def python_exe():
    version = bpy.app.version
    print("binary:", bpy.app.binary_path)

    # blender vers =< 2.91 contains a path to their py executable
    if version[0] == 2 and version[1] <= 91:
        executable = bpy.app.binary_path_python

    # in newer versions sys.executable should point to the py executable
    else:
        executable = sys.executable
    print(f"blender version: {version}, exe: {executable}")

    # some version the path points to the binary path instead of the py executable
    if executable == bpy.app.binary_path:
        py_path = Path(sys.prefix) / "bin"
        py_exec = next(py_path.glob("python*"))  # first file that starts with "python" in "bin" dir
        executable = str(py_exec)
        print(f"cmd failed, redirecting to: {executable}")

    return executable


def clear_user_site():
    """ Clear python site packages to avoid user site packages. """
    # Disallow pip from checking the user site-package
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"
    return environ_copy


python_exe = python_exe()


# endregion


# region package import and info
def import_module(_dependency):
    """ Attempt to import module and assign it to the globals dictionary.
        May only be used with properly installed dependencies. """
    tmp_dependency = dependency_naming(_dependency)

    if tmp_dependency.name in globals():
        importlib.reload(globals()[tmp_dependency.name])

    else:
        globals()[tmp_dependency.name] = importlib.import_module(tmp_dependency.name)


def get_package_info(_dependency):
    """ Restart of blender is required to import 'pkg_resources' properly.
        Does NOT work directly after running a python subprocess. """
    import pkg_resources

    try:
        # get version and path of the package
        dist_info = pkg_resources.get_distribution(
            _dependency.pkg
        )
        _version = dist_info.version

        _path = Path(dist_info.location) / dist_info.project_name
        _path = str(_path)

    except pkg_resources.DistributionNotFound as e:
        print(e)
        _version = None
        _path = None
    return _version, _path


def is_package_installed(_dependency):
    try:
        # Try to import the module to check if it is available.
        # Blender may has to be restarted to take effect on newly installed or removed dependencies.
        importlib.import_module(_dependency.name)
        tmp_dependency = dependency_naming(_dependency)

        # Installed dependencies are added to globals.
        if tmp_dependency.name in globals():
            importlib.reload(globals()[tmp_dependency.name])
            return True
        else:
            if tmp_dependency.name is 'pip':
                # pip shouldn't be in globals
                return True
            return False
    except ModuleNotFoundError:
        return False


# endregion


# region pip
def install_pip():
    if is_package_installed(Dependency("pip", "pip", "pip", "pip")):
        return

    print(f"Attempting to install pip.")
    try:
        # https://github.com/robertguetzkow/blender-python-examples/blob/master/add-ons/install-dependencies/install-dependencies.py
        import ensurepip
        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)
    except Exception as e:
        print(e)
        clear_user_site()
        subprocess.check_call([python_exe, "-m", "ensurepip"])


def update_pip():
    # https://github.com/pypa/pip/issues/5599
    # updating pip is depreciated, use on own risk
    updated = subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"]) == 0

    if updated:
        print(f"Updated pip successfully.")
    else:
        print(f"Pip update failed. Please check the console for details.")
# endregion


# region dependencies
def dependency_naming(_dependency):
    """ Updates the dependency names depending on the input.
    Returns module name of the dependency as package and global name if the vars are not available. """
    _name, _package = _dependency.name, _dependency.package

    if _dependency.package is None:
        _package = _dependency.module

    if _dependency.name is None:
        _name = _dependency.module

    tmp_dependency = Dependency(_dependency.module, _package, _name, _dependency.pkg)
    return tmp_dependency


def install_and_import_module(_dependency):
    """ Installs a dependency and imports the module to blender. """
    tmp_dependency = dependency_naming(_dependency)

    if is_package_installed(tmp_dependency):
        print(f"{tmp_dependency.package} is already installed.")
        return

    try:
        print(f"Attempting to install: {_dependency.module}")
        environ_copy = clear_user_site()
        cmd = [python_exe, "-m", "pip", "install", "--no-cache-dir", tmp_dependency.package]
        installed = subprocess.call(cmd, env=environ_copy) == 0

    except Exception as e:
        print(e)
        # The "--user" option does not work with Blender's Python version as it's in another directory.
        # However, the added user site packages tries to bypass the behaviour
        cmd = [python_exe, "-m", "pip", "install", "--no-cache-dir", tmp_dependency.package, "--user"]
        installed = subprocess.call(cmd) == 0

    # subprocess.run(cmd, check=True, env=environ_copy)
    if installed:
        print(f"{tmp_dependency.package} installed successfully. "
              f"Please restart Blender to see effect.")
    else:
        print(f"Cannot install {tmp_dependency.package}."
              f"Please check the console for details.")

    # Attempt to import the module
    import_module(tmp_dependency)


def uninstall_dependency(_dependency):
    # Uninstall dependency without question prompt.
    cmd = [python_exe, "-m", "pip", "uninstall", "-y", _dependency.pkg]
    uninstalled = subprocess.call(cmd) == 0

    if uninstalled:
        print(f"Uninstalled {_dependency.module} successfully.")
    else:
        print(f"Failed to uninstall {_dependency.module}.")
# endregion


Dependency = namedtuple("Dependency", ["module", "package", "name", "pkg"])
required_dependencies = (Dependency(module="mediapipe", package=None, name=None, pkg="mediapipe"),
                         Dependency(module="opencv-python", package=None, name="cv2", pkg="opencv_contrib_python"))

global dependencies_installed
dependencies_installed = True

for dependency in required_dependencies:
    m_dependency = dependency_naming(dependency)
    if not is_package_installed(m_dependency):
        dependencies_installed = False
