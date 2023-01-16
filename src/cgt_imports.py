'''
Copyright (C) Denys Hsu, cgtinker.com, hello@cgtinker.com

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
import logging
import sys
from pathlib import Path

# Ensure all modules are reloaded from new files,
# when the addon is removed and a new version is installed in the same session,
# or when Blender's 'Reload Scripts' operator has been called.


PACKAGE_PATH = Path(__file__).parent.parent.parent
PACKAGE_NAME = PACKAGE_PATH.name


def import_module(module):
    importlib.import_module(f"{PACKAGE_NAME}{module}")


def reload_module(module):
    importlib.reload(sys.modules[f"{PACKAGE_NAME}{module}"])


def get_reload_list(sub_dirs):
    reload_list = []

    for sub_dir in sub_dirs:
        files = [p for p in sub_dir.rglob("*.py") if not p.stem.startswith('_')]
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


def manage_imports(dirs: list = None):
    print("Reloading")
    if dirs is None:
        s = [PACKAGE_PATH / 'src']
    else:
        s = [PACKAGE_PATH / d for d in dirs]

    reload_list = get_reload_list(s)
    for module in reload_list:
        reload = True
        try:
            import_module(module)
        except (ModuleNotFoundError, ImportError) as e:
            reload = False
            logging.error(f"Import {module} failed: {e}")

        if reload:
            reload_module(module)

