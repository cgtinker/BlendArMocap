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
    bl_label = "Freemocap Import"
    bl_parent_id = "OBJECT_PT_cgt_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def draw(self, context):
        self.layout.label(text="Imports Freemocap Session Folder")
        user = context.scene.m_cgtinker_mediapipe  # noqa
        box0 = self.layout.box()
        box0.row().prop(user, "freemocap_session_path")

        if user.modal_active:
            box0.row().operator("wm.cgt_load_freemocap_operator", text="Break")
        else:
            box0.row().operator("wm.cgt_load_freemocap_operator", text="Import Session")

        box0.row().operator("wm.fmc_load_synchronized_videos", text="Load synchronized videos")
        box1 = self.layout.box()
        box1.row().operator("wm.fmc_bind_freemocap_data_to_skeleton", text="Bind to rig")
