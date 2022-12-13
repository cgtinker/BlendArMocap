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

from __future__ import annotations
import bpy


def mute_driver(ob: bpy.types.Object, mute: bool = False):
    try:
        drivers = ob.animation_data.drivers
        for d in drivers:
            d.mute = mute
        return True
    except Exception:
        return False


def remove_drivers(ob: bpy.types.Object):
    try:
        preassigned = ob.animation_data.drivers
        for i, d in enumerate(preassigned):
            ob.animation_data.drivers.remove(d)
        return True
    except Exception:
        return False
