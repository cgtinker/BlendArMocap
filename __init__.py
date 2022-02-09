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
    "blender":     (2, 90, 0),
    "location":    "3D View > Tool",
    "warning":     "",
    "wiki_url":    "https://github.com/cgtinker/BlendArMocap",
    "tracker_url": "https://github.com/cgtinker/BlendArMocap/issues",
    "category":    "Development"
}
import importlib
import os
import sys

PACKAGE = os.path.basename(os.path.dirname(__file__))
print(__file__)
print(__name__)
print(PACKAGE)
load_order = {
    'init':    [
        'blender.interface.ui_registration',
        'blender.interface.ui_panels',
        'blender.interface.ui_preferences',
        'blender.interface.ui_properties',
        'blender.interface.install_dependencies',
        'blender.interface.stream_detection_operator',
        'blender.interface',
        'cgt_naming'
    ],
    'modules': [
        'utils.filter',
        'utils.open_cv',
        'utils.writer'
        'utils',
        'ml_detection',
        'management',
        'bridge',
        'blender.cgt_rig'
        'blender.utils'
    ],
}

utils_module_name = PACKAGE + '.blender'


def get_loaded_modules():
    prefix = PACKAGE + '.blender'
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


def compare_module_list(a, b):
    # Allow 'utils' to move around
    a_copy = list(a)
    a_copy.remove(utils_module_name)
    b_copy = list(b)
    b_copy.remove(utils_module_name)
    return a_copy == b_copy


def load_initial_modules():
    # gets initial load order
    load_list = [PACKAGE + '.' + name for name in load_order['init']]

    for i, name in enumerate(load_list):
        print(name)
        # import modules
        importlib.import_module(name)
        # compare with loaded modules
        module_list = get_loaded_modules()
        # min loaded vs max loaded
        expected_list = load_list[0: max(7, i + 1)]

        if not compare_module_list(module_list, expected_list):
            print(f'{PACKAGE}: initial load order mismatch after {name} '
                  f'- expected: \n, {expected_list} '
                  f'\nGot:\n, {module_list}')

    return load_list


# PASS OUT TRY EXCEPT
try:
    if PACKAGE in locals():
        print(f'{PACKAGE}: Reloading package...')
        reload_modules()
    else:
        print(f'{PACKAGE}: Initially loading package... ')

        load_list = load_initial_modules()
        reload_list = load_order['init'] = get_loaded_modules()

        if not compare_module_list(reload_list, load_list):
            print('!!! BlendArMocap: initial load order mismatch - expected: \n', load_list, '\nGot:\n', reload_list)
    import_succeeded = True
except ModuleNotFoundError as e:
    print(f'{PACKAGE}: ModuleNotFoundError occurred when trying to enable add-on.')
    print(e)
except Exception as e:
    print(f'{PACKAGE}: Unexpected Exception occurred when trying to enable add-on.')
    print(e)

from blender.interface import ui_registration


def register():
    ui_registration.register()


def unregister():
    ui_registration.unregister()


if __name__ == '__main__':
    register()
