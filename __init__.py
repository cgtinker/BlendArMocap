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
    "name": "BpyMediapipe",
    "description": "Mediapipe implementation for Blender 2.9+.",
    "author": "cgtinker",
    "version": (1, 0, 0),
    "blender": (2, 90, 0),
    "location": "3D View > Tool",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

from utils import log
from interface import Registration
import importlib

importlib.reload(log)
importlib.reload(Registration)


def register():
    Registration.register()


def unregister():
    Registration.unregister()


if __name__ == '__main__':
    log.init_logger()
    register()
