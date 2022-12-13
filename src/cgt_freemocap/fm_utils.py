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

import logging
import bpy
from pathlib import Path


def is_valid_session_directory(path):
    """ TODO: Improve directory validation. """
    freemocap_session_path = Path(bpy.path.abspath(path)).parent
    if not Path(freemocap_session_path).is_dir():
        logging.error(f"Given path doesn't point to a directory containing freemocap session data {freemocap_session_path}.")
        return False
    logging.debug(f"Path to freemocap session: {freemocap_session_path}")
    return True
