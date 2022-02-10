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
    "version":     (1, 0, 2),
    "cgt_blender":     (2, 90, 0),
    "location":    "3D View > Tool",
    "warning":     "",
    "wiki_url":    "https://github.com/cgtinker/BlendArMocap",
    "tracker_url": "https://github.com/cgtinker/BlendArMocap/issues",
    "category":    "Development"
}
import importlib
import sys

load_order = {
    'init':    [
        'cgt_blender.interface.ui_registration',
        'cgt_blender.cgt_rig',
        'cgt_blender.input_manager',
        'cgt_blender.interface',
    ],
    'modules': [
        'cgt_utils.filter',
        'cgt_utils.open_cv',
        'cgt_utils.writer'
        'cgt_utils',
        'cgt_detection',
        'management',
        'cgt_bridge',
        'cgt_blender.cgt_rig'
        'cgt_blender.cgt_utils'
    ]
}

utils_module_name = __name__ + '.cgt_blender'


def get_loaded_modules():
    prefix = __name__ + '.cgt_blender'
    return [name for name in sys.modules if name.startswith(prefix)]


def reload_modules():
    fixed_modules = set(reload_list)

    for name in get_loaded_modules():
        print("loaded modules", name)
        if name not in fixed_modules:
            print("del stale module", name)
            del sys.modules[name]

    for name in reload_list:
        print("reloading", name)
        importlib.reload(sys.modules[name])


def load_initial_modules():
    load_list = [__name__ + '.' + name for name in load_order['init']]

    for i, name in enumerate(load_list):
        print("loading", name)
        importlib.import_module(name)

    return load_list


try:
    if __name__ in locals():
        print("blendarmocap locally")

    if __name__ in locals():
        print(f'{__name__}: Reloading package...')
        reload_modules()
    else:
        print(f'{__name__}: Initially loading package... ')

        load_list = load_initial_modules()
        reload_list = load_order['init'] = get_loaded_modules()
except ModuleNotFoundError as e:
    print(f'{__name__}: ModuleNotFoundError occurred when trying to enable add-on.')
    print(e)
except Exception as e:
    print(f'{__name__}: Unexpected Exception occurred when trying to enable add-on.')
    print(e)

from .cgt_blender.interface import ui_registration


def register():
    ui_registration.register()


def unregister():
    ui_registration.unregister()


if __name__ == '__main__':
    register()
