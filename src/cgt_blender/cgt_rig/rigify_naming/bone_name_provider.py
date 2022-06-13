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

from abc import ABC, abstractmethod
import bpy


class BoneNameProvider(ABC):
    def __init__(self):
        import rigify # noqa (internal addon)
        self.rigify_version = int(''.join(map(str, rigify.bl_info['version'])))
        self.bpy_version = int(''.join(map(str, bpy.app.version)))

    def update(self):
        if self.rigify_version >= 65:
            self.set_rv65_bone_names()

    @abstractmethod
    def set_rv65_bone_names(self):
        pass
