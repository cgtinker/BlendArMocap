'''
Copyright (C) Denys Hsu, cgtinker.com, hello@cgtinker.com

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


# BlendArMocap is split into separated parts.
# Every module has to be registered to be active.

from .cgt_core.cgt_interface import cgt_core_registration
from .cgt_mediapipe import cgt_mp_registration
from .cgt_core.cgt_transfer import cgt_transfer_registration
from .cgt_freemocap import fm_registration


modules = [
    cgt_core_registration,
    cgt_mp_registration,
    fm_registration,
    cgt_transfer_registration,
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()