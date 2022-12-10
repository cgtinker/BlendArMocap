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

from bpy.types import Panel


class PT_CGT_main_panel(Panel):
    bl_label = "BlendFreemocap"
    bl_idname = "OBJECT_PT_cgt_freemocap_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        box = self.layout.box()
        box.row().prop(user, "freemocap_session_path")

        if user.modal_active:
            box.row().operator("wm.cgt_load_freemocap_operator", text="Stop Detection")
        else:
            box.row().operator("wm.cgt_load_freemocap_operator", text=user.button_start_detection)

