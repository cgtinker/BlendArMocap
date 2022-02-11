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

dir_layout = {
    "cgt_blender": [

    ]
}

def reload_modules(name):
    """
    This makes sure all modules are reloaded from new files, when the addon is removed and a new version is installed in the same session,
    or when Blender's 'Reload Scripts' operator is run manually.
    It's important, that utils modules are reloaded first, as operators and menus import from them
    """

    import os
    import importlib

    # first fetch and reload all utils modules
    print(__file__)
    package_dir = os.path.dirname(__file__)
    print(os.listdir(os.path.join(package_dir, "cgt_blender")))
    print(os.listdir(package_dir))
    #ld = os.listdir(os.path.join(__file__[0]))
    #print(ld)
    return
    utils_modules = sorted([name[:-3] for name in os.listdir(os.path.join(__path__[0], "utils")) if name.endswith('.py')])
    print(utils_modules)
    for module in utils_modules:
        impline = "from . utils import %s" % (module)

        print("reloading %s" % (".".join([name] + ['utils'] + [module])))

        exec(impline)
        importlib.reload(eval(module))

    # then update the classes and keys dicts
    #from . import dicts
    #importlib.reload(dicts)

    # and based on that, reload the modules containing operator and menu classes
    modules = []

    for label in dicts.classes:
        entries = dicts.classes[label]
        for entry in entries:
            path = entry[0].split('.')
            module = path.pop(-1)

            if (path, module) not in modules:
                modules.append((path, module))

    for path, module in modules:
        if path:
            impline = "from . %s import %s" % (".".join(path), module)
        else:
            impline = "from . import %s" % (module)

        print("reloading %s" % (".".join([name] + path + [module])))

        exec(impline)
        importlib.reload(eval(module))


if 'bpy' in locals():
    reload_modules(__name__)
reload_modules("mediapipe_ml")


"""
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
        'cgt_blender'
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
"""
# from .cgt_blender.interface import ui_registration
#
#
# def register():
#     ui_registration.register()
#
#
# def unregister():
#     ui_registration.unregister()
#
#
# if __name__ == '__main__':
#     register()
