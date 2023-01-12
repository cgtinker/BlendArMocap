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
import bpy


class UI_PT_CGT_Properties_Freemocap(bpy.types.PropertyGroup):
    freemocap_session_path: bpy.props.StringProperty(
        name="Path",
        description="Directory path to freemocap session.",
        options={'HIDDEN'},
        maxlen=1024,
        subtype='DIR_PATH'
    )
    modal_active: bpy.props.BoolProperty(default=False)


class UI_PT_CGT_Panel_Freemocap(bpy.types.Panel):
    bl_label = "Freemocap"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def draw(self, context):
        layout = self.layout

        user = context.scene.cgt_freemocap  # noqa
        layout.row().prop(user, "freemocap_session_path")

        if user.modal_active:
            layout.row().operator("wm.cgt_load_freemocap_operator", text="Stop Import", icon='CANCEL')
        else:
            layout.row().operator("wm.cgt_load_freemocap_operator", text="Import Session Folder", icon='IMPORT')
        layout.row().operator("wm.fmc_load_synchronized_videos", text="Load synchronized videos", icon='IMAGE_PLANE')
        # layout.separator()
        # layout.row().operator("wm.fmc_bind_freemocap_data_to_skeleton", text="Bind to rig (Preview)")


classes = [
    UI_PT_CGT_Properties_Freemocap,
    UI_PT_CGT_Panel_Freemocap,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgt_freemocap = bpy.props.PointerProperty(type=UI_PT_CGT_Properties_Freemocap)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cgt_freemocap # noqa


if __name__ == '__main__':
    try:
        unregister()
    except RuntimeError:
        pass

    register()
