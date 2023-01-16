import bpy
import logging
import time
from . import fm_utils, fm_session_loader

""" Interfaces for freemocap subprocess commands. """


class LoadFreemocapSession:
    user = freemocap_session_path = timeout = processing_manager = None
    log_step = 25

    def __init__(self, session_path: str, timeout: int = None, load_raw: bool = False):
        """ Loads Freemocap data from session directory.
            Attention: May not use the WM_Load_Freemocap_Operator.
            Modal operations deliver unexpected results when blender is in background. """

        # set timeout
        self.timeout = timeout
        if timeout is None:
            self.timeout = float('inf')

        # set session path
        self.user = bpy.context.scene.cgt_freemocap
        self.user.freemocap_session_path = session_path
        self.user.load_raw = load_raw
        if fm_utils.is_valid_session_directory(session_path):
            self.loader = fm_session_loader.FreemocapLoader(session_path)

    def quickload(self):
        self.loader.quickload_raw()

    def run_modal(self):
        """ Imports the data, breaks if timeout is reached or import finished. """
        start = time.time()
        while time.time() - start <= self.timeout:
            if self.loader.frame % self.log_step == 0:
                self.log_step *= 2
                logging.debug(f"{self.processing_manager.realtime_data_provider.frame}/"
                              f"{self.processing_manager.realtime_data_provider.number_of_frames}")

            running = self.loader.update()
            if not running:
                break
        logging.debug("Stopped importing data.")


def import_freemocap_session(
        session_directory: str,
        bind_to_rig: bool = False,
        load_synch_videos: bool = False,
        timeout: int = None,
        load_raw: bool = False,
        background: bool = True):

    logging.debug("Called import freemocap session.")
    if "cgt_freemocap" not in bpy.context.scene:
        bpy.context.scene["cgt_freemocap"] = {}
        bpy.context.scene["cgt_freemocap"]["freemocap_session_path"] = ""
        bpy.context.scene["cgt_freemocap"]["load_raw"] = False

    if not fm_utils.is_valid_session_directory(session_directory):
        logging.error("Aborted, session path not valid.")
        return -1

    # import data
    importer = LoadFreemocapSession(session_directory, timeout)
    if load_raw:
        importer.quickload()
    else:
        importer.run_modal()

    if bind_to_rig:
        bpy.ops.wm.fmc_bind_freemocap_data_to_skeleton()

    if load_synch_videos:
        bpy.ops.wm.fmc_load_synchronized_videos()

    logging.debug("Finished freemocap session import.")
