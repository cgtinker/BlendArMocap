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

from dataclasses import dataclass


@dataclass(repr=True)
class Slope:
    """ Slope / Gradient gets used to change mapping ranges. """
    slope: float
    max_in: float
    max_out: float
    min_in: float
    min_out: float
    name: str

    def __init__(self, min_in, max_in, min_out, max_out, name=""):
        self.slope = (max_out - min_out) / (max_in - min_in)
        self.min_in = min_in
        self.min_out = min_out
        self.max_in = max_in
        self.max_out = max_out
        self.name = name


def remap(value, min_in, max_in, min_out, max_out):
    slope = (max_out - min_out) / (max_in - min_in)
    offset = min_out - slope * min_in
    return slope * value + offset
