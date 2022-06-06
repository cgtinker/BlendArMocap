'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# thanks @robertguetzkow
import importlib
import os
import subprocess
import sys
from collections import namedtuple
from pathlib import Path
from ... import cgt_naming
import warnings
import bpy.app


# region python executable and site-packages
def get_python_exe():
    version = bpy.app.version
    if version[0] > 2 or version[0] == 2 and version[1] >= 92:
        # in newer versions sys.executable should point to the py executable
        executable = sys.executable

    else:
        try:
            # blender vers =< 2.91 contains a path to their py executable
            executable = bpy.app.binary_path_python
        except AttributeError:
            executable = None
            pass

    # some version the path points to the binary path instead of the py executable
    if executable == bpy.app.binary_path or executable == None:
        py_path = Path(sys.prefix) / "bin"
        py_exec = next(py_path.glob("python*"))  # first file that starts with "python" in "bin" dir
        executable = str(py_exec)
        print(f"{cgt_naming.PACKAGE} - cmd failed, redirecting to: {executable}")

    print(f"{cgt_naming.PACKAGE} - blender bin: {bpy.app.binary_path}, blender version: {version}")
    print(f"{cgt_naming.PACKAGE} - python exe: {executable}")
    return executable


def clear_user_site():
    """ Clear python site packages to avoid user site packages. """
    # Disallow pip from checking the user site-package
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"
    return environ_copy
# endregion


# region package import and info
def import_module(_dependency):
    """ Attempt to import module and assign it to the globals dictionary.
        May only be used with properly installed dependencies. """
    tmp_dependency = dependency_naming(_dependency)

    # TODO: temporarily fetching mediapipe protobuf error  till update
    try:
        if tmp_dependency.name in globals():
            importlib.reload(globals()[tmp_dependency.name])

        else:
            globals()[tmp_dependency.name] = importlib.import_module(tmp_dependency.name)
    except TypeError as e:
        # TODO: Remove dirty versioning fix which is required to fix installation issues of beta users
        print(f"Importing {tmp_dependency.name} dependency failed")
        if "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python" in str(e):
            print("TRY TO FIX PROTOCOL BUFFER ERR\n\n")
            try:
                uninstall_dependency(Dependency(module="protobuf==3.19.1", package=None, name="google.protobuf", pkg="protobuf"))
                install_and_import_module(Dependency(module="protobuf==3.19.1", package=None, name="google.protobuf", pkg="protobuf"))
            except Exception as e:
                print("{\nUNKNOWN EXCEPTION OCCURRED\n")
                print(e)
        else:
            print(e)


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
    _dependency = dependency_naming(_dependency)
    try:
        # Try to import the module to check if it is available.
        # Blender may has to be restarted to take effect on newly installed or removed dependencies.
        tmp_dependency = dependency_naming(_dependency)
        importlib.import_module(_dependency.name)

        # Installed dependencies are added to globals.
        if tmp_dependency.name in globals():
            importlib.reload(globals()[tmp_dependency.name])
            return True
        else:
            if tmp_dependency.name == 'pip':
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
        # cmd = [python_exe, "-m", "pip", "install", "--no-cache-dir", tmp_dependency.package]
        cmd = [python_exe, "-m", "pip", "install", tmp_dependency.package]
        print(cmd)
        installed = subprocess.call(cmd, env=environ_copy) == 0

    except Exception as e:
        print(e)
        print("ATTEMPT TO USE USER TAG")
        # The "--user" option does not work with Blender's Python version as it's in another directory.
        # However, the added user site packages tries to bypass the behaviour
        cmd = [python_exe, "-m", "pip", "install", "--no-cache-dir", tmp_dependency.package, "--user"]
        print(cmd)
        installed = subprocess.call(cmd) == 0

    # subprocess.run(cmd, check=True, env=environ_copy)
    if installed:
        print(f"{tmp_dependency.package} installed successfully.")
    else:
        print(f"Cannot install {tmp_dependency.package}.")

    # Attempt to import the module
    import_module(tmp_dependency)


def uninstall_dependency(_dependency):
    cmd = [python_exe, "-m", "pip", "freeze", ">", _dependency.pkg]
    frozen = subprocess.call(cmd) == 0
    print(f"{_dependency.pkg} disabled {frozen}")

    cmd = [python_exe, "-m", "pip", "uninstall", "-y", _dependency.pkg]
    uninstalled = subprocess.call(cmd, shell=True) == 0

    if uninstalled:
        print(f"Uninstalled {_dependency.module} successfully.")
        return True
    else:
        print(f"Failed to uninstall {_dependency.module}.")
        return False


def force_remove_remains():
    if not sys.platform == 'win32':
        return

    import pkg_resources
    dist_info = pkg_resources.get_distribution("pip")

    for file in Path(str(dist_info.location)).iterdir():
        # check for substrings (prevent removal of other libs)
        sub_strings = ["~" + _dependency.name[1:] for _dependency in required_dependencies]
        sub_strings += ["~" + _dependency.pkg[1:] for _dependency in required_dependencies]
        r_package = [True if sub_str in str(file.name) else False for sub_str in sub_strings]

        # pip adds a ~ when before deleting a package
        if str(file.name).startswith("~") and True in r_package:
            import shutil
            try:
                shutil.rmtree(file)
            except PermissionError as e:
                print(e)
                print("\nRestart Blender with elevated privileges to remove the conflicted files")
# endregion


Dependency = namedtuple("Dependency", ["module", "package", "name", "pkg"])
required_dependencies = (
    Dependency(module="protobuf==3.19.1", package=None, name="google.protobuf", pkg="protobuf"),
    Dependency(module="mediapipe==0.8.10", package=None, name="mediapipe", pkg="mediapipe"),
    Dependency(module="opencv-python==4.5.5.64", package=None, name="cv2", pkg="opencv_contrib_python"))


global dependencies_installed
dependencies_installed = True
with warnings.catch_warnings():
    # catching depreciated warning
    warnings.simplefilter("ignore")
    python_exe = get_python_exe()

for dependency in required_dependencies:
    try:
        import_module(dependency)
    except ModuleNotFoundError:
        pass

    if not is_package_installed(dependency):
        dependencies_installed = False
