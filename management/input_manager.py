import bpy


def start_detection():
    """ Starts feature Detection
        - SYNC - via detection operator.
        - ASYNC - not implemented yet. """
    user = bpy.context.scene.m_cgtinker_mediapipe
    if user.enum_synchronize == 'SYNC':
        bpy.ops.wm.feature_detection_modal('EXEC_DEFAULT')
    elif user.enum_synchronize == 'ASYNC':
        pass


def add_rig():
    pass
