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
    "version":     (1, 2, 2),
    "blender":     (2, 90, 0),
    "location":    "3D View > Tool",
    "warning":     "Requires external packages and elevated privileges",
    "wiki_url":    "https://github.com/cgtinker/BlendArMocap",
    "tracker_url": "https://github.com/cgtinker/BlendArMocap/issues",
    "support":     "COMMUNITY",
    "category":    "Development"
}


def reload_modules():
    from .src import cgt_imports
    cgt_imports.manage_imports(True)


if "bl_info" in locals():
    reload_modules()

from .src.cgt_blender.interface import ui_registration


def register():
    ui_registration.register()


def unregister():
    ui_registration.unregister()


if __name__ == '__main__':
    register()
