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
import sys

PACKAGE: str = __name__
reload_list: list = None
module_type: str = 'init'

load_order: dict = {
    'init':  [
        'cgt_naming',
        'cgt_blender.utils.install_dependencies',
        'cgt_blender.interface.ui_registration',
        'cgt_blender.cgt_rig',
        'cgt_blender.input_manager',
        'cgt_blender.interface',
        'cgt_blender',
        '__init__'
    ],
    'core':  [
        'cgt_utils.open_cv',
        'cgt_utils',
        'cgt_detection',
        'cgt_bridge.face_drivers',
        'cgt_bridge',
    ],
    'debug': [
        'cgt_naming',
        'cgt_blender',
        'cgt_bridge',
        'cgt_detection',
    ]
}


def get_loaded_modules():
    prefix = PACKAGE
    return [name for name in sys.modules if name.startswith(prefix)]


def reload_modules():
    fixed_modules = set(reload_list)
    for name in get_loaded_modules():
        if name not in fixed_modules:
            print("NAMING CONFLICT WHILE INITIALIZATION:", name)
    for name in reload_list:
        importlib.reload(sys.modules[name])


def load_initial_modules():
    load_list = [PACKAGE + '.' + name for name in load_order[module_type]]
    for i, name in enumerate(load_list):
        print("attempt to load:", i, name, "...")
        importlib.import_module(name)
    return load_list


def execute():
    if PACKAGE in locals():
        print(f'{PACKAGE}: Reloading package...')
        reload_modules()
    else:
        print(f'{PACKAGE}: Initial package loading... ')
        load_list = load_initial_modules()

    reload_list = load_order[module_type] = get_loaded_modules()
    if module_type == 'debug':
        for module_name in reload_list:
            module = importlib.import_module(module_name)
            importlib.reload(module)


execute()

from .cgt_blender.interface import ui_registration


def register():
    ui_registration.register()


def unregister():
    ui_registration.unregister()


if __name__ == '__main__':
    register()
