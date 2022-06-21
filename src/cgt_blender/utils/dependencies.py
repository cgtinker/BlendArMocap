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
from importlib import machinery
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
        with warnings.catch_warnings():
            # catching depreciated warning
            warnings.simplefilter("ignore")
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
    environ_copy["PYTHONNOUSERSITE"] = "-1"
    return environ_copy
# endregion


# region package import and info
def import_module(_dependency):
    """ Attempt to import module and assign it to the globals dictionary.
        May only be used with properly installed dependencies. """
    if not is_package_installed(_dependency):
        return False

    tmp_dependency = dependency_naming(_dependency)
    try:
        if tmp_dependency.name in globals():
            importlib.reload(globals()[tmp_dependency.name])
            return True
        else:
            module = importlib.import_module(tmp_dependency.name)
            globals()[tmp_dependency.name] = module
            return True
    except ModuleNotFoundError as e:
        print(e)
        return False


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
    # find spec using importlib
    try:
        package = importlib.util.find_spec(_dependency.name)
    except ModuleNotFoundError:
        return False
    except ValueError:
        return False

    # only accept it as valid if there is a source file for the module - not bytecode only.
    found = issubclass(type(package), importlib.machinery.ModuleSpec)

    if found:
        return True
    return False


def reinstall_dependency(_dependency):
    print("Attempt to reinstall dependency", _dependency)
    try:
        uninstall_dependency(_dependency)
        install_and_import_module(_dependency)

        if sys.platform == "win32":
            import time
            print("Attempt to shutdown blender.")
            time.sleep(3)
            bpy.ops.wm.quit_blender()
    except Exception as e:
        print("{\nUNKNOWN EXCEPTION OCCURRED\n")
        print(e)
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
        return

    print(f"Attempting to install: {_dependency.module}")
    environ_copy = clear_user_site()
    cmd = [python_exe, "-m", "pip", "install", "--no-cache-dir", tmp_dependency.package]
    # cmd = [python_exe, "-m", "pip", "install", tmp_dependency.package]
    print(cmd)
    import socket
    try:
        installed = subprocess.call(cmd, env=environ_copy) == 0
    except socket.timeout:
        installed = False
        print("PLEASE CHECK YOUR INTERNET CONNECTION AND RETRY.")

    # subprocess.run(cmd, check=True, env=environ_copy)
    if installed:
        print(f"{tmp_dependency.package} installed successfully.")
    else:
        print(f"Cannot install {tmp_dependency.package}.")

    # Attempt to import the module
    import_module(tmp_dependency)


def move_package_b4removal(_dependency):
    """ Moving packages to delete in a separate folder.
        Deleting the folder contents after restarting Blender.
        -> force_remove_remains()
        https://developer.blender.org/T77837 """
    import re
    print("Moving package to custom trash folder for removal upon restart.", _dependency)

    def canonize_path(name):
        # pip/src/pip/_vendor/packaging/utils.py
        _canonicalize_regex = re.compile(r"[-_.]+")
        value = _canonicalize_regex.sub("-", name).lower()
        return value

    import pkg_resources
    try:
        dist_info = pkg_resources.get_distribution(_dependency.pkg)
    except pkg_resources.DistributionNotFound:
        return

    tmp_dist_path = Path(dist_info.location) / f"{dist_info.project_name}-{dist_info.version}.dist-info"
    canonize_dist = canonize_path(str(tmp_dist_path))

    site_packages = Path(dist_info.location)
    # get path to package
    try:
        package_init = importlib.import_module(_dependency.name).__file__
        package_path = Path(package_init).parent
    except Exception as e:
        print("Cannot fetch path to package:", e)
        # trying to create name based on module name (might fail)
        package_path = Path(site_packages) / _dependency.name

    # compare to dists in site packages
    dist_path = None
    for dist in site_packages.iterdir():
        tmp_canonize_dist = canonize_path(str(dist))
        if canonize_dist == tmp_canonize_dist:
            dist_path = dist
            break

    # todo: improve path name - path to custom trash
    file = Path(__file__).parent.parent.parent
    trash = file / "trash"
    trash.mkdir(parents=True, exist_ok=True)

    print("try to delete")
    # move dists to custom trash folder to delete on restart
    import shutil
    success = []
    for r_path in [dist_path, package_path]:
        if r_path is None:
            continue

        if r_path.is_dir():
            shutil.move(str(r_path), str(trash))
            print(f"Successfully moved package for further removal:\nFrom: {str(r_path)}\nTo: {str(trash)}")
            success.append(True)
        else:
            print("Failed to move package to", str(trash))
            success.append(False)

    # return if moving dirs was successful
    if False in success:
        return False
    return True


def uninstall_dependency(_dependency):
    """
    print("Trying to remove", _dependency)
    if sys.platform != "win32":
       pass
    else:
        # uninstalling using pip is currently not possible on win
       return move_package_b4removal(_dependency)

    # Uninstall dependency without question prompt on linux / macos
    cmd = [python_exe, "-m", "pip", "uninstall", "-y", _dependency.pkg]
    uninstalled = subprocess.call(cmd) == 0

    if uninstalled:
        print(f"Uninstalled {_dependency.module} successfully.")
        return True
    else:
        print(f"Failed to uninstall {_dependency.module}.")
        print(uninstalled)
        return False
    """
    return move_package_b4removal(_dependency)


def force_remove_remains():
    # uninstalling packages doesn't work on windows, they are getting
    # force removed on restart
    # if sys.platform != 'win32':
    #     return

    # todo: improve path name
    m_dir = Path(__file__).parent.parent.parent
    trash = m_dir / "trash"
    trash.mkdir(parents=True, exist_ok=True)
    import shutil
    for file in trash.iterdir():
        try:
            shutil.rmtree(file)
        except PermissionError as e:
            print(e)
            print("\n\nRestart Blender to remove files")
# endregion


def analyze_dependencies(_dependencies):
    """ yields if dependency is installed and the corrupted dependency """
    def corrupted_package(package):
        if package.name == "cv2":
            _version, _path = get_package_info(
                Dependency(module="opencv-python", package=None, name="cv2", pkg="opencv_python"))
            if _version is not None or _path is not None:
                return False, [
                    Dependency(module="opencv-python", package=None, name="cv2", pkg="opencv_python"),
                    Dependency(module="mediapipe", package=None, name="mediapipe", pkg="mediapipe"),
                ]
            else:
                return False, [package]
        elif package.name in ["mediapipe", "protobuf"]:
            return False, [
                Dependency(module="protobuf", package=None, name="google.protobuf", pkg="protobuf"),
                Dependency(module="mediapipe", package=None, name="mediapipe", pkg="mediapipe"),
            ]
        else:
            return False, [package]

    for _dependency in _dependencies:
        # check if package is installed
        if not is_package_installed(_dependency):
            yield False, []
            continue
        print(_dependencies)
        # try to import the dependency and add it to globs
        # except corrupted dependency
        try:
            _importable = import_module(_dependency)
            if not _importable:
                yield corrupted_package(_dependency)
                continue
        except ModuleNotFoundError as e:
            print("MODULE CANNOT BE FOUND\n", e)
            yield corrupted_package(_dependency)
            continue
        except TypeError as e:
            print("PLEASE CHECK IF PROTOBUF VERSION > 3.20.0\n", e)
            yield corrupted_package(_dependency)
        except ImportError as e:
            print("PLEASE CHECK IF CV2 IS CORRUPTED\n", e)
            yield corrupted_package(_dependency)

        # check for path and version of the dependency, except cv2py preinstalled (conflict)
        try:
            _version, _path = get_package_info(_dependency)
        except ModuleNotFoundError as e:
            print("MODULE CANNOT BE FOUND\n", e)
            yield corrupted_package(_dependency)
            continue

        if _version is None or _path is None:
            print("corrupted dist")
            corrupted_package(_dependency)
            continue


Dependency = namedtuple("Dependency", ["module", "package", "name", "pkg"])
required_dependencies = (
    # # gets properly installed by mediapipe package
    # Dependency(module="numpy", package=None, name="numpy", pkg="numpy"),
    # Dependency(module="absl-py", package=None, name="absl", pkg="absl_py"),
    # Dependency(module="attrs>=19.1.0", package=None, name="attrs", pkg="attrs"),
    # Dependency(module="matplotlib", package=None, name="matplotlib", pkg="matplotlib"),
    Dependency(module="opencv-contrib-python>=4.5.5.64", package=None, name="cv2", pkg="opencv_contrib_python"),
    Dependency(module="protobuf>=3.11.4,<=3.20.0", package=None, name="google.protobuf", pkg="protobuf"),
    Dependency(module="mediapipe>=0.8.10", package=None, name="mediapipe", pkg="mediapipe"),
    )

python_exe = get_python_exe()
dependencies_installed = True
corrupted_dependencies = None
if corrupted_dependencies is None:
    corrupted_dependencies = []

for is_installed, corrupted_dependency in analyze_dependencies(required_dependencies):
    dependencies_installed = is_installed
    if len(corrupted_dependency) != 0:
        corrupted_dependencies += corrupted_dependency

if len(corrupted_dependencies) != 0:
    print("CORRUPTED DEPENDENCIES OR DEPENDENCY CONFLICTS FOUND\n", corrupted_dependencies)
    print("PLEASE UNINSTALL DEPENDENCIES USING THE ADD-ON SETTINGS")
