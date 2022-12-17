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
import json


class JsonData(object):
    """ Import json data, preferably as dict.
        Can load lists, will store them as dict with "data" as key. """
    data: dict = None

    def __init__(self, path: str = None, **data):
        if path:
            with open(path, 'rb') as jsonFile:
                data = json.load(jsonFile)

                if isinstance(data, dict):
                    self.__dict__.update((), **data)
                elif isinstance(data, list):
                    self.__dict__.update((), **{"data": data})
                else:
                    assert TypeError
        else:
            self.__dict__.update((), **data)

    def save(self, path: str = None):
        assert path is not None
        with open(path, "w", encoding='utf-8') as jsonFile:
            json.dump(self.__dict__, jsonFile, ensure_ascii=False, indent=4, separators=(',', ':'), sort_keys=False)

    def __str__(self):
        return f'{self.__dict__}'

    def __call__(self):
        return self.data
