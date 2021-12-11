import bpy


class UI_detection_button(bpy.types.Operator):
    bl_label = "Start Detection"
    bl_idname = "button.detection_button"
    bl_description = "Detect solution in Stream."

    def execute(self, context):
        user = context.scene.m_cgtinker_mediapipe
        if user.enum_synchronize == 'SYNC':
            bpy.ops.wm.feature_detection_modal('EXEC_DEFAULT')
        elif user.enum_synchronize == 'ASYNC':
            pass
        return {'FINISHED'}


class UI_add_rig_button(bpy.types.Operator):
    bl_label = "Add Rig"
    bl_idname = "button.add_rig"
    bl_description = "Add a rig for motion tracking transfer"

    def execute(self, context):
        # TODO: Management exec path
        return {'FINISHED'}
