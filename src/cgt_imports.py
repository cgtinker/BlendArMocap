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

import importlib
import sys
from pathlib import Path

"""
This makes sure all modules are reloaded from new files, when the addon is removed and a new version is installed in the same session,
or when Blender's 'Reload Scripts' operator is run manually.
"""


SUB_DIRS = ['src/cgt_blender', 'src/cgt_processing', 'src/cgt_detection',
            'src/cgt_utils', 'src/cgt_bridge', 'src/cgt_patterns']

INIT_MODULES = [
    '.src.cgt_imports',
    '.src.cgt_naming',
    '.src.cgt_blender.interface.ui_properties',
    '.src.cgt_blender.interface.ui_registration',
    '.src.cgt_blender.interface',
    '.src.cgt_blender.utils.dependencies',
]

FILE = Path(__file__)
PACKAGE_PATH = FILE.parent.parent
PACKAGE_NAME = PACKAGE_PATH.name


def import_module(module):
    # print(f"importing {PACKAGE_NAME}{module}...")
    importlib.import_module(f"{PACKAGE_NAME}{module}")


def reload_module(module):
    # print(f"reloading {PACKAGE_NAME}{module}...")
    importlib.reload(sys.modules[f"{PACKAGE_NAME}{module}"])


def get_reload_list(sub_dirs):
    reload_list = []

    for sub_dir in sub_dirs:
        files = [p for p in sub_dir.rglob("*.py") if p.stem != '__init__']
        for file in files:
            parents = get_parents(file, [])
            imp_path = ""
            for parent in reversed(parents):
                imp_path += f".{parent}"
            imp_path += f".{file.stem}"
            reload_list.append(imp_path)
    return reload_list


def get_parents(file: Path, parents: list):
    if file.parent.name != PACKAGE_NAME:
        parents.append(file.parent.name)
        get_parents(file.parent, parents)
    return parents


def manage_imports(reload: bool = False, force: bool = False):
    # from .cgt_blender.interface import ui_registration
    # ui_registration.unregister()
    for module in INIT_MODULES:
        import_module(module)

    from .cgt_blender.utils import dependencies
    # if reload:
    reload_module('.src.cgt_blender.utils.dependencies')
    print(f"{PACKAGE_NAME} - Dependencies installed: {dependencies.dependencies_installed}")

    # if dependencies.dependencies_installed is True or force is True:
    print(f"{PACKAGE_NAME} - Attempt to reload...")
    sub_dirs = [PACKAGE_PATH / sub_dir for sub_dir in SUB_DIRS]
    reload_list = get_reload_list(sub_dirs)

    for module in reload_list:
        if reload is True:
            import_module(module)
            reload_module(module)
        else:
            import_module(module)
    print(f"{PACKAGE_NAME} - Reload successful!")


if __name__ == '__main__':
    addons_folder = str(PACKAGE_PATH)
    sys.path.append(addons_folder)

    # reload modules besides bpy
    sub_dirs = [PACKAGE_PATH / sub_dir for sub_dir in SUB_DIRS[1:]]
    print(sub_dirs)
    reload_list = get_reload_list(sub_dirs)
    print(reload_list)
    for module in reload_list:
        print(f"importing {module}...")
        import_module(module)
