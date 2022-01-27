import importlib

import bpy

from management import input_manager

importlib.reload(input_manager)

"""
class UI_detection_button(bpy.types.Operator):
    bl_label = "Start Detection"
    bl_idname = "button.cgt_detection_button"
    bl_description = "Detect solution in Stream."

    def execute(self, context):
        input_manager.start_detection()
        return {'FINISHED'}
"""

class UI_transfer_anim_button(bpy.types.Operator):
    bl_label = "Transfer Animation"
    bl_idname = "button.cgt_transfer_animation_button"
    bl_description = "Transfer driver animation to rig"

    def execute(self, context):
        input_manager.transfer_animation()
        return {'FINISHED'}
