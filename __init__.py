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

bl_info = {
    "name":        "BlendArMocap",
    "description": "Mediapipe implementation for Blender 2.9+.",
    "author":      "cgtinker",
    "version":     (1, 2, 0),
    "blender":     (2, 90, 0),
    "location":    "3D View > Tool",
    "warning":     "Requires external packages and elevated privileges",
    "wiki_url":    "https://github.com/cgtinker/BlendArMocap",
    "tracker_url": "https://github.com/cgtinker/BlendArMocap/issues",
    "support":     "COMMUNITY",
    "category":    "Development"
}

import importlib
import os
import sys

SUB_DIRS = ['cgt_blender', 'cgt_bridge', 'cgt_detection', 'cgt_utils']
INIT_MODULES = [
    'cgt_naming',
    'cgt_blender.interface.ui_properties',
    'cgt_blender.interface.ui_registration',
    'cgt_blender.input_manager',
    'cgt_blender.interface',
    'cgt_blender.utils.install_dependencies',

]


def reload_modules():
    """
    This makes sure all modules are reloaded from new files, when the addon is removed and a new version is installed in the same session,
    or when Blender's 'Reload Scripts' operator is run manually.
    """

    def import_module(module):
        importlib.import_module(f"{__name__}.{module}")

    def reload_module(module):
        import_module(module)
        importlib.reload(sys.modules[f"{__name__}.{module}"])

    def get_reload_list(sub_dirs):
        reload_list = []

        for sub_dir in sub_dirs:
            for root, sub_dir, files in os.walk(sub_dir):
                # get all python modules files for the import
                sub_path = root.replace(os.path.dirname(__file__) + "/", "")
                sub_path = sub_path.replace("/", ".")
                modules = [f"{file.replace('.py', '')}" for file in files
                           if file.endswith('.py') if file != '__init__.py']

                for module in modules:
                    m_module = f"{sub_path}.{module}"
                    reload_list.append(m_module)

        return reload_list

    # first reload the required modules to activate the UI
    for module in INIT_MODULES:
        import_module(module)

    from .cgt_blender.utils import install_dependencies
    if install_dependencies.dependencies_installed:
        print(f"Attempt to reload {__name__}")
        package = os.path.dirname(__file__)
        sub_dirs = [os.path.join(package, sub_dir) for sub_dir in SUB_DIRS]
        reload_list = get_reload_list(sub_dirs)

        for module in reload_list:
            reload_module(module)
        print(f"Reloaded {__name__} successfully")


if "INIT_MODULES" in locals():
    reload_modules()

from .cgt_blender.interface import ui_registration


def register():
    ui_registration.register()


def unregister():
    ui_registration.unregister()


if __name__ == '__main__':
    register()
