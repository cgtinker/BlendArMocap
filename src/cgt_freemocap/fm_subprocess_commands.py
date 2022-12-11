import bpy
import logging
import time

""" Interfaces for freemocap subprocess commands. """


def import_freemocap_session(
        session_directory: str,
        bind_to_rig: bool = False,
        load_synch_videos: bool = False,
        timeout: int = None):

    logging.debug("Called import freemocap session.")
    if "m_cgtinker_mediapipe" not in bpy.context.scene:
        bpy.context.scene["m_cgtinker_mediapipe"] = {}
        bpy.context.scene["m_cgtinker_mediapipe"]["freemocap_session_path"] = ""
        bpy.context.scene["m_cgtinker_mediapipe"]["modal_active"] = False

    user = bpy.context.scene.m_cgtinker_mediapipe
    user.freemocap_session_path = session_directory
    bpy.ops.wm.cgt_load_freemocap_operator()

    # if timeout is not None:
    #     start = time.time()
    #     while True:
    #         if not user.modal_active:
    #             break
    #         if time.time() - start >= timeout:
    #             user.modal_active = False
    #             logging.warning("Import timed out")
    #             break
    # time.sleep(0.5)

    if bind_to_rig:
        bpy.ops.wm.fmc_bind_freemocap_data_to_skeleton()
    if load_synch_videos:
        bpy.ops.wm.fmc_load_synchronized_videos()
    logging.debug("Finished freemocap session import.")
