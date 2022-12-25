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

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from . import ui_properties, cgt_panels, ui_operators, cgt_transfer_props
from .. import cgt_rigify_transfer_preferences
# from ...cgt_mediapipe import pref_operators, pref_panels

modules = (
    cgt_rigify_transfer_preferences,
    ui_operators,
    cgt_panels,
    cgt_transfer_props,
)


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()
