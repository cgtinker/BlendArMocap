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
    "version":     (1, 0, 0),
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

import bpy

# getting access to the current dir - necessary to access blender file location
try:
    blend_dir = os.path.dirname(bpy.data.filepath)
    if blend_dir not in sys.path:
        sys.path.append(blend_dir)

    # append sys path to dir
    main_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'module')
    sys.path.append(main_dir)
    print("MANUAL ADDON INITIALIZATION")

except AttributeError:
    # already appended
    print("RUNNING MANUAL DEBUGGING IN EDITOR")


class ModuleManager:
    PACKAGE = "mediapipe_ml"
    reload_list = None
    load_order = {
        'init':    [
            'cgt_naming',
            'blender.interface.ui_registration',
            'blender.cgt_rig',
            'blender.input_manager',
            'blender.interface',
            'blender'
        ],
        'core': [
            'utils.open_cv',
            'utils',
            'ml_detection',
            'management',
            'bridge',
        ],
    }

    def __init__(self, module_type):
        self.module_type = module_type

    def get_loaded_modules(self):
        prefix = self.PACKAGE + '.blender'
        return [name for name in sys.modules if name.startswith(prefix)]

    def reload_modules(self):
        fixed_modules = set(self.reload_list)

        for name in self.get_loaded_modules():
            if name not in fixed_modules:
                print("Deleting module:", name)
                del sys.modules[name]

        for name in self.reload_list:
            importlib.reload(sys.modules[name])

    def load_initial_modules(self):
        load_list = [self.PACKAGE + '.' + name for name in self.load_order[self.module_type]]
        for i, name in enumerate(load_list):
            importlib.import_module(name)

        return load_list

    def execute(self):
        if self.PACKAGE in locals():
            print(f'{self.PACKAGE}: Reloading package...')
            self.reload_modules()
        else:
            print(f'{self.PACKAGE}: Initial package loading... ')

            load_list = self.load_initial_modules()
            self.reload_list = self.load_order[self.module_type] = self.get_loaded_modules()
            print("\nload list:", load_list)
            print("\nreload_list", self.reload_list)


importer = ModuleManager("init")
importer.execute()

# custom top level import
from mediapipe_ml.blender.interface import ui_registration  # noqa


def register():
    ui_registration.manual_test_registration(importer)


def unregister():
    ui_registration.manual_unregistration()


if __name__ == '__main__':
    try:
        register()
    except ValueError:
        unregister()
        register()
