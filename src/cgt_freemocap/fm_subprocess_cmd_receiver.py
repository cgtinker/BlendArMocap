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
import logging
import time
from . import fm_utils

""" Interfaces for freemocap subprocess commands. """


class LoadFreemocapSession:
    user = freemocap_session_path = timeout = processing_manager = None
    step = 25

    def __init__(self, session_path: str, timeout: int = None):
        """ Loads Freemocap data from session directory.
            Attention: May not use the WM_Load_Freemocap_Operator.
            Modal operations deliver unexpected results when blender is in background. """
        self.timeout = timeout
        if timeout == None:
            self.timeout = float('inf')

        self.user = bpy.context.scene.m_cgtinker_mediapipe
        self.user.freemocap_session_path = session_path
        if session_path is not None:
            from src.cgt_core.mediapipe_processing_manager import RealtimeDataProcessingManager
            self.processing_manager = RealtimeDataProcessingManager("FREEMOCAP", "BPY")
            self.processing_manager.init_detector(input_type=2)
            self.processing_manager.init_bridge()

    def run(self):
        """ Imports the data, breaks if timeout is reached or import finished. """
        start = time.time()
        while time.time() - start <= self.timeout:
            if self.processing_manager.realtime_data_provider.frame % self.step == 0:
                self.step *= 2
                logging.debug(f"{self.processing_manager.realtime_data_provider.frame}/"
                              f"{self.processing_manager.realtime_data_provider.number_of_frames}")
            running = self.processing_manager.realtime_data_provider.get_data()
            if not running:
                break

        logging.debug("Stopped importing data.")
        del self.processing_manager


def import_freemocap_session(
        session_directory: str,
        bind_to_rig: bool = False,
        load_synch_videos: bool = False,
        timeout: int = None):

    logging.debug("Called import freemocap session.")
    if "m_cgtinker_mediapipe" not in bpy.context.scene:
        bpy.context.scene["m_cgtinker_mediapipe"] = {}
        bpy.context.scene["m_cgtinker_mediapipe"]["freemocap_session_path"] = ""

    if not fm_utils.is_valid_session_directory(session_directory):
        logging.error("Aborted, session path not valid.")
        return -1

    importer = LoadFreemocapSession(session_directory, timeout)
    importer.run()

    if bind_to_rig:
        bpy.ops.wm.fmc_bind_freemocap_data_to_skeleton()

    if load_synch_videos:
        bpy.ops.wm.fmc_load_synchronized_videos()
    logging.debug("Finished freemocap session import.")
