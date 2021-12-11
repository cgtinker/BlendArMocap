import bpy
from management import input_manager


class UI_detection_button(bpy.types.Operator):
    bl_label = "Start Detection"
    bl_idname = "button.detection_button"
    bl_description = "Detect solution in Stream."

    def execute(self, context):
        input_manager.start_detection()
        return {'FINISHED'}


class UI_add_rig_button(bpy.types.Operator):
    bl_label = "Add Rig"
    bl_idname = "button.add_rig"
    bl_description = "Add a rig for motion tracking transfer"

    def execute(self, context):
        input_manager.add_rig()
        return {'FINISHED'}
