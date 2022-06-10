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
    wrist = "hand_ik"
    thumb_cmc = "thumb.01"
    thumb_mcp = "thumb.02"
    thumb_ip = "thumb.03"
    thumb_tip = "thumb.01"
    index_mcp = "f_index.01"
    index_pip = "f_index.02"
    index_dip = "f_index.03"
    index_tip = "f_index.01"
    middle_mcp = "f_middle.01"
    middle_pip = "f_middle.02"
    middle_dip = "f_middle.03"
    middle_tip = "f_middle.01"
    ring_mcp = "f_ring.01"
    ring_pip = "f_ring.02"
    ring_dip = "f_ring.03"
    ring_tip = "f_ring.01"
    pinky_mcp = "f_pinky.01"
    pinky_pip = "f_pinky.02"
    pinky_dip = "f_pinky.03"
    pinky_tip = "f_pinky.01"

    r_wrist = "hand_ik.R"
    r_thumb_cmc = "thumb.01.R"
    r_thumb_mcp = "thumb.02.R"
    r_thumb_ip = "thumb.03.R"
    r_thumb_tip = "thumb.01.R.001"
    r_index_mcp = "f_index.01.R"
    r_index_pip = "f_index.02.R"
    r_index_dip = "f_index.03.R"
    r_index_tip = "f_index.01.R.001"
    r_middle_mcp = "f_middle.01.R"
    r_middle_pip = "f_middle.02.R"
    r_middle_dip = "f_middle.03.R"
    r_middle_tip = "f_middle.01.R.001"
    r_ring_mcp = "f_ring.01.R"
    r_ring_pip = "f_ring.02.R"
    r_ring_dip = "f_ring.03.R"
    r_ring_tip = "f_ring.01.R.001"
    r_pinky_mcp = "f_pinky.01.R"
    r_pinky_pip = "f_pinky.02.R"
    r_pinky_dip = "f_pinky.03.R"
    r_pinky_tip = "f_pinky.01.R.011"

    l_wrist = "hand_ik.L"
    l_thumb_cmc = "thumb.01.L"
    l_thumb_mcp = "thumb.02.L"
    l_thumb_ip = "thumb.03.L.001"
    l_thumb_tip = "thumb.01.L"
    l_index_mcp = "f_index.01.L"
    l_index_pip = "f_index.02.L"
    l_index_dip = "f_index.03.L"
    l_index_tip = "f_index.01.L.001"
    l_middle_mcp = "f_middle.01.L"
    l_middle_pip = "f_middle.02.L"
    l_middle_dip = "f_middle.03.L"
    l_middle_tip = "f_middle.01.L.001"
    l_ring_mcp = "f_ring.01.L"
    l_ring_pip = "f_ring.02.L"
    l_ring_dip = "f_ring.03.L"
    l_ring_tip = "f_ring.01.L.001"
    l_pinky_mcp = "f_pinky.01.L"
    l_pinky_pip = "f_pinky.02.L"
    l_pinky_dip = "f_pinky.03.L"
    l_pinky_tip = "f_pinky.01.L.001"

    def set_rv65_bone_names(self):
        pass
