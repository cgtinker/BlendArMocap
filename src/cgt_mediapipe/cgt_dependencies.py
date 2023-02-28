import os
import sys

import importlib
import platform

import subprocess
import logging

import bpy
import warnings
import site

from typing import Tuple
from collections import namedtuple
from pathlib import Path


Dependency = namedtuple("Dependency", ["module", "name", "pkg", "args"])


# region get internal python paths
def get_python_exe():
    """ Get path of blender internal python executable. """
    if bpy.app.version < (2, 91, 0):
        executable = bpy.app.binary_path_python
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            executable = sys.executable

    # some version the path points to the binary path instead of the py executable
    if executable == bpy.app.binary_path or executable == None:
        py_path = Path(sys.prefix) / "bin"
        py_exec = next(py_path.glob("python*"))  # first file that starts with "python" in "bin" dir
        executable = str(py_exec)

    print(f"{bpy.app.version} Python Executable: {executable}.")
    return executable


def get_site_packages_path():
    """ Get path of blender internal site packages. """
    # get path to site packages using site
    site_package_path = site.getsitepackages()
    if isinstance(site_package_path, str):
        if Path(site_package_path).is_dir():
            return site_package_path
    elif isinstance(site_package_path, list):
        if len(site_package_path) >= 1 and (Path(site_package_path[0]).is_dir()):
            return site.getsitepackages()[0]

    # recv search for site packages
    if bpy.app.version >= (3, 0, 0):
        python_directory = Path(bpy.utils.system_resource('PYTHON'))
        site_package_path = [path for path in python_directory.rglob('site-packages')]
        if len(site_package_path) >= 1:
            return str(site_package_path[0])

    # return script path and hope for the best
    return bpy.utils.script_paths()


def clear_user_site():
    """ Clear python site packages to avoid user site packages. """
    # Depreciated: --target flag seems to deliver better results
    # Disallow pip from checking the user site-package
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "-1"
    return environ_copy
# endregion


# region commands
def run_command(*args: str, module: str) -> bool:
    """ Run command. Return True on successful execution. """
    cmds = [cmd for cmd in args if cmd is not None]
    cmd = [python_binary, "-m", module, *cmds]
    print(*cmd, sep=' ')
    # environ_copy = clear_user_site()
    return subprocess.call(cmd) == 0  # , env=environ_copy) == 0


def install_dependency(self: bpy.types.Operator, dependency: Dependency, local_user: bool) -> bool:
    """ Install a dependency using pip. """
    import socket

    # expect socket to time out due to bad connection or vpn usage
    try:
        sub_cmds = []
        if dependency.args is not None:
            sub_cmds = [cmd for cmd in dependency.args if isinstance(cmd, str)]

        if local_user:
            successfully_installed = run_command('install', dependency.module, '--user', *sub_cmds, module='pip')
        else:
            successfully_installed = run_command('install', dependency.module, '--target', site_packages, *sub_cmds, module='pip')

        if successfully_installed:
            import_module(dependency)
            return True
        else:
            self.report({'ERROR'}, f"Installation of {dependency.pkg} failed. Check system console output.")
            return False

    except socket.timeout:
        self.report({'ERROR'}, "Ensure you are connected to the internet and no VPN is running.")
        return False
# endregion


# region delete
def uninstall_dependency(self: bpy.types.Operator, dependency: Dependency) -> bool:
    """ Moves dependency to custom trash location to remove it on start up.
        Removing dependencies via pip leaves random artifacts.
        https://developer.blender.org/T7783 """
    # run_command('uninstall', dependency.pkg, '-y', module='pip')
    import re
    logging.info(f"Moving package to custom trash folder for removal upon restart. {dependency}")

    def canonize_path(name):
        # pip/src/pip/_vendor/packaging/utils.py
        _canonicalize_regex = re.compile(r"[-_.]+")
        value = _canonicalize_regex.sub("-", name).lower()
        return value

    # find package dist
    import pkg_resources
    try:
        dist_info = pkg_resources.get_distribution(dependency.pkg)
    except pkg_resources.DistributionNotFound:
        return False

    # path to dist info
    tmp_dist_path = Path(dist_info.location) / f"{dist_info.project_name}-{dist_info.version}.dist-info"
    canonize_dist = canonize_path(str(tmp_dist_path))

    # path to package
    other_package_path = None
    try:
        package_init = importlib.import_module(dependency.name).__file__
        package_path = Path(package_init).parent

        # don't delete site packages by accident
        if str(package_path.stem).startswith('site'):
            package_path = Path(package_init)

        # customs as weird packaging
        if dependency.pkg == 'protobuf':
            package_path = package_path.parent
        if dependency.pkg == 'attrs':
            other_package_init = importlib.import_module('attr').__file__
            other_package_path = Path(other_package_init).parent

    except Exception as e:
        # trying to create name based on module name (might fail)
        package_path = Path(site_packages) / dependency.name

    # compare to dists in site packages
    dist_path = None
    for dist in Path(site_packages).iterdir():
        tmp_canonize_dist = canonize_path(str(dist))
        if canonize_dist == tmp_canonize_dist:
            dist_path = dist
            break

    # check if .pth file in site packages
    pth_file = None
    for path in Path(site_packages).iterdir():
        if not path.suffix == '.pth':
            continue
        if canonize_path(path.stem).startswith(canonize_path(dependency.pkg)):
            pth_file = path

    # path to custom trash
    file = Path(__file__).parent.parent
    trash = file / "trash"
    trash.mkdir(parents=True, exist_ok=True)

    # move directories to custom trash folder to delete on restart
    import shutil
    successfully_moved = []
    for r_path in [dist_path, package_path, pth_file, other_package_path]:
        if r_path is None:
            continue
        shutil.move(str(r_path), str(trash))
        logging.info(f"Successfully moved package for further removal:\nFrom: {str(r_path)}\nTo: {str(trash)}")
        successfully_moved.append(True)
    # return if moving dirs was successful
    return all(successfully_moved)


def remove_dependency_remains():
    """ Removing dependencies via pip leaves random artifacts.
        Deleting dependency remains in custom trash.
        https://developer.blender.org/T7783 """
    m_dir = Path(__file__).parent.parent
    trash = m_dir / "trash"
    trash.mkdir(parents=True, exist_ok=True)
    import shutil
    for file in trash.iterdir():
        try:
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()

        except (PermissionError, NotADirectoryError) as e:
            print(e)
            print("\n\nRestart Blender to remove files")
# endregion


# region pip
def ensure_pip(self: bpy.types.Operator) -> bool:
    """ Runs ensure pip bootstrap if pip is not installed. Returns True if pip is available. """
    if is_installed(Dependency("pip", "pip", "pip", "pip")):
        return True

    logging.info(f"Attempt to install pip.")
    try:
        # https://github.com/robertguetzkow/blender-python-examples/blob/master/add-ons/install-dependencies/install-dependencies.py
        import ensurepip
        ensurepip.bootstrap()
        os.environ.pop("PIP_REQ_TRACKER", None)
        return True

    except Exception as e:
        logging.warning(f"Bootstrap failed: {e}\n\nManual call ensure pip.")
        if run_command('--default-pip', module='ensurepip'):
            return True

    self.report({'ERROR'}, "Installation of pip failed.")
    return False


def update_pip(self: bpy.types.Operator) -> bool:
    """ Updates pip - depreciated. """
    # https://github.com/pypa/pip/issues/5599
    if run_command("install", "--upgrade", "pip", module='pip'):
        return True

    self.report({'ERROR'}, "Update failed")
    return False
# endregion


# region package import and info
def import_module(dependency: Dependency) -> bool:
    """ Attempt to import module and assign it to the globals dictionary.
        May only be used with properly installed dependencies. """
    if not is_installed(dependency):
        return False

    try:
        # reload dependency if it's in globals
        if dependency.name in globals():
            importlib.reload(globals()[dependency.name])
            return True

        # import dependency and add it to globals
        module = importlib.import_module(dependency.name)
        globals()[dependency.name] = module
        return True

    except ModuleNotFoundError as e:
        logging.error(e)
        return False


def get_package_info(dependency: Dependency) -> Tuple[str, str]:
    """ Get info of installed package in Blender. """
    import pkg_resources
    try:
        # get version and path of the package
        dist_info = pkg_resources.get_distribution(dependency.pkg)
        version = dist_info.version

        path = Path(dist_info.location) / dist_info.project_name
        path = str(path)

    except pkg_resources.DistributionNotFound as e:
        logging.warning(e)
        version, path = None, None
    return version, path


def is_installed(dependency: Dependency) -> bool:
    """ Checks if dependency is installed. """
    try:
        spec = importlib.util.find_spec(dependency.name)
    except (ModuleNotFoundError, ValueError, AttributeError):
        return False

    # only accept it as valid if there is a source file for the module - not bytecode only.
    if issubclass(type(spec), importlib.machinery.ModuleSpec):
        return True
    return False
# endregion


if sys.platform == 'darwin' and platform.processor() == 'arm':
    required_dependencies = [
        Dependency(module="opencv-contrib-python==4.7.0.68", name="cv2", pkg="opencv_contrib_python", args=None),
        Dependency(module="protobuf==3.20.3", name="google.protobuf", pkg="protobuf", args=None),
        Dependency(module="mediapipe-silicon==0.8.11", name="mediapipe", pkg="mediapipe-silicon", args=None)
    ]

elif sys.platform == 'win32':
    required_dependencies = [
        Dependency(module="opencv-contrib-python==4.7.0.68", name="cv2", pkg="opencv_contrib_python", args=None),
        Dependency(module="protobuf==3.20.3", name="google.protobuf", pkg="protobuf", args=None),
        Dependency(module="mediapipe==0.9.0.1", name="mediapipe", pkg="mediapipe", args=None)
    ]

elif sys.platform == 'linux':
    required_dependencies = [
        Dependency(module="opencv-contrib-python==4.5.5.64", name="cv2", pkg="opencv_contrib_python", args=None),
        Dependency(module="protobuf==3.20.3", name="google.protobuf", pkg="protobuf", args=None),
        Dependency(module="mediapipe==0.9.0.1", name="mediapipe", pkg="mediapipe", args=None)
    ]

# legacy mac
elif sys.platform == 'darwin':
    # Manual setup of mediapipes dependency tree as the package deps may contains internal conflicts.
    required_dependencies = [
        Dependency(module="absl_py", name="absl", pkg="absl-py", args=None),
        Dependency(module="attrs==22.2.0", name="attrs", pkg="attrs", args=None),

        # matplotlib deps
        # Numpy is preinstalled in Blender (should not be overwritten)
        Dependency(module="six>=1.6", name="six", pkg="six", args=None),
        Dependency(module="python-dateutil>=2.7", name="dateutil", pkg="python_dateutil", args=["--no-deps"]),
        Dependency(module="pyparsing>=2.2.1", name="pyparsing", pkg="pyparsing", args=None),
        Dependency(module="pillow>=6.2", name="PIL", pkg="Pillow", args=['--upgrade']),
        Dependency(module="packaging>=20.0", name="packaging", pkg="packaging", args=None),
        Dependency(module="kiwisolver>=1.0.1", name="kiwisolver", pkg="kiwisolver", args=None),
        Dependency(module="fonttools>=4.22.0", name="fontTools", pkg="fonttools", args=None),
        Dependency(module="cycler>=0.10", name="cycler", pkg="cycler", args=None),
        Dependency(module="contourpy>=1.0.1", name="contourpy", pkg="contourpy", args=["--no-deps"]),

        # mediapipe deps
        Dependency(module="matplotlib", name="matplotlib", pkg="matplotlib", args=["--no-deps"]),
        Dependency(module="opencv-contrib-python==4.5.5.64", name="cv2", pkg="opencv_contrib_python", args=None),
        Dependency(module="protobuf==3.20.2", name="google.protobuf", pkg="protobuf", args=None),
        Dependency(module="mediapipe==0.8.10", name="mediapipe", pkg="mediapipe", args=["--no-deps"]),
    ]


from ..cgt_core.cgt_utils import cgt_user_prefs
stored_prefs = cgt_user_prefs.get_prefs(local_user=False)

user_site = site.getusersitepackages()
if user_site not in sys.path and stored_prefs.get("local_user", False):
    logging.info("Adding user site packages.")
    sys.path.append(user_site)
site_packages = get_site_packages_path()
python_binary = get_python_exe()
print(site_packages, python_binary)
# remove_dependency_remains()

for dep in required_dependencies:
    info = get_package_info(dep)
    logging.debug(str(info))
dependencies_installed = [is_installed(dependency) for dependency in required_dependencies]
