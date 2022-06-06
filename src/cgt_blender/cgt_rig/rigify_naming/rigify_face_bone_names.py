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

from . import bone_name_provider


class RigifyBoneNameProvider(bone_name_provider.BoneNameProvider):
    head = "head"
    jaw = "jaw_master"

    upper_lid_r = "lid.T.R.002"
    lower_lid_r = "lid.B.R.002"
    upper_lid_l = "lid.T.L.002"
    lower_lid_l = "lid.B.L.002"

    lip_t = "lip.T"
    lip_b = "lip.B"
    lip_r = "lips.R"
    lip_l = "lips.L"

    brow_in_r = "brow.T.R.003"
    forehead_in_r = "DEF-forehead.R"
    brow_mid_r = "brow.T.R.002"
    forehead_mid_r = "DEF-forehead.R.001"
    brow_out_r = "brow.T.R.001"
    forehead_out_r = "DEF-forehead.R.002"

    brow_in_l = "brow.T.L.003"
    forehead_in_l = "DEF-forehead.L"
    brow_mid_l = "brow.T.L.002"
    forehead_mid_l = "DEF-forehead.L.001"
    brow_out_l = "brow.T.L.001"
    forehead_out_l = "DEF-forehead.L.002"

    def set_rv65_bone_names(self):
        pass



