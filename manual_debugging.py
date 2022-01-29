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
    "name": "BlendArMocap",
    "description": "Mediapipe implementation for Blender 2.9+.",
    "author": "cgtinker",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
    "location": "3D View > Tool",
    "warning": "",
    "wiki_url": "https://github.com/cgtinker/BlendArMocap",
    "tracker_url": "https://github.com/cgtinker/BlendArMocap/issues",
    "category": "Development"
}

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
    print("RUNNING MANUAL DEBUGGING IN EDITOR")

from utils import log
from blender.interface import registration
import importlib

importlib.reload(log)
importlib.reload(registration)


def register():
    registration.manual_test_registration()


def unregister():
    registration.unregister()


if __name__ == '__main__':
    # log.init_logger()
    register()
