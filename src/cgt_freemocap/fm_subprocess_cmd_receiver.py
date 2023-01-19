import bpy
import logging
import time
from . import fm_utils, fm_session_loader

""" Interfaces for freemocap subprocess commands. """


class LoadFreemocapSession:
    user = freemocap_session_path = timeout = processing_manager = None
    log_step = 25

    def __init__(self, session_path: str, timeout: int = None):
        """ Loads Freemocap data from session directory.
            Attention: May not use the WM_Load_Freemocap_Operator.
            Modal operations deliver unexpected results when blender is in background. """

        # set timeout
        self.timeout = timeout
        if timeout is None:
            self.timeout = float('inf')

        # set session path
        self.user = bpy.context.scene.cgtinker_freemocap
        self.user.freemocap_session_path = session_path

    def quickload(self):
        self.user.quickload = True
        self.user.load_raw = True
        bpy.ops.wm.cgt_quickload_freemocap_operator()

    def quickload_processed(self):
        self.user.quickload = True
        self.user.load_raw = False
        bpy.ops.wm.cgt_quickload_freemocap_operator()

    def run_modal(self):
        """ Imports the data, breaks if timeout is reached or import finished. """
        self.user.load_raw = False
        self.user.modal_active = False
        self.user.quickload = False

        print("Start running modal")
        bpy.ops.wm.cgt_load_freemocap_operator()

        start = time.time()
        while time.time() - start <= self.timeout and self.user.modal_active:
            pass

        self.user.modal_active = False
        logging.info("Stopped importing data.")


def import_freemocap_session(
        session_directory: str,
        bind_to_rig: bool = False,
        load_synch_videos: bool = False,
        timeout: int = None,
        load_raw: bool = False,
        load_quick: bool = False):

    logging.debug("Called import freemocap session.")

    if not hasattr(bpy.context.scene, 'cgtinker_freemocap'):
        logging.error("Aborted, BlendArMocap Add-On might not be registered.")
        return 0

    if not fm_utils.is_valid_session_directory(session_directory):
        logging.error("Aborted, session path not valid.")
        return 0

    # import data
    importer = LoadFreemocapSession(session_directory, timeout)
    if load_raw and load_quick:
        importer.quickload()
    elif load_quick:
        importer.quickload_processed()
    else:
        importer.run_modal()

    if bind_to_rig:
        bpy.ops.wm.fmc_bind_freemocap_data_to_skeleton()

    if load_synch_videos:
        bpy.ops.wm.fmc_load_synchronized_videos()

    logging.info("Finished freemocap session import.")
    return 1
