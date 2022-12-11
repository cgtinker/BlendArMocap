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

import logging
from ..cgt_detection import realtime_data_provider_interface
from pathlib import Path
import numpy as np
import bpy


class FreemocapLoader(realtime_data_provider_interface.RealtimeDataProvider):
    mediapipe3d_frames_trackedPoints_xyz: np.array = None
    number_of_frames: int = -1
    number_of_tracked_points: int = -1

    first_body_point: int = 0
    first_left_hand_point: int = 33
    first_right_hand_point: int = 54
    first_face_point: int = 75

    mp_res = None

    def frame_detection_data(self):
        """ Provides holistic data for each (prerecorded) frame. """
        while self.frame < self.number_of_frames:
            holistic_data = self.get_detection_results()
            self.listener.data = holistic_data
            self.update_listeners()
            return True
        return False

    def initialize_model(self):
        """Load the 3d mediapipe skeleton data from a freemocap session
        (not implemented) `reprojection_error_threshold:float` = filter data by removing dottos with high reprojection error. I think for now I'll just do a mean+2*standard_deviation cut-off that leaves in 95% of the data (if stupidly assuming normal distribution) or something TODO - do this better and smarter lol
        """
        freemocap_session_path = Path(bpy.context.scene.m_cgtinker_mediapipe.freemocap_session_path)
        logging.debug(f"Loading FREEMOCAP data...\n{freemocap_session_path}")

        data_arrays_path = freemocap_session_path / 'DataArrays'
        mediapipe3d_xyz_npy_path = data_arrays_path / 'mediaPipeSkel_3d_smoothed.npy'
        mediapipe3d_reprojectionError_npy_path = data_arrays_path / 'mediaPipeSkel_reprojErr.npy'

        self.mediapipe3d_frames_trackedPoints_xyz = np.load(str(mediapipe3d_xyz_npy_path)) / 1000  # convert to meters
        mediapipe3d_frames_trackedPoints_reprojectionError = np.load(str(mediapipe3d_reprojectionError_npy_path))

        self.number_of_frames = self.mediapipe3d_frames_trackedPoints_xyz.shape[0]
        self.number_of_tracked_points = self.mediapipe3d_frames_trackedPoints_xyz.shape[1]

    def get_detection_results(self, mp_res=None):
        # TODO: Data is rotated
        if self.frame == self.number_of_frames - 1:
            return None
        tracked_points = self.mediapipe3d_frames_trackedPoints_xyz[self.frame, :, :]
        tracked_points = np.array([[-x, -z, -y] for x, y, z in tracked_points])

        this_frame_body_data = tracked_points[0:self.first_left_hand_point]
        this_frame_left_hand_data = tracked_points[self.first_left_hand_point:self.first_right_hand_point]
        this_frame_right_hand_data = tracked_points[self.first_right_hand_point:self.first_face_point]
        this_frame_face_data = tracked_points[self.first_face_point:]

        this_frame_body_data = [[i, p] for i, p in enumerate(this_frame_body_data)]
        this_frame_left_hand_data = [[i, p] for i, p in enumerate(this_frame_left_hand_data)]
        this_frame_right_hand_data = [[i, p] for i, p in enumerate(this_frame_right_hand_data)]
        this_frame_face_data = [[i, p] for i, p in enumerate(this_frame_face_data)]

        holistic_data = [[[this_frame_left_hand_data], [this_frame_right_hand_data]],
                         [this_frame_face_data], this_frame_body_data]
        return holistic_data

    def contains_features(self, mp_res):
        pass

    def draw_result(self, s, mp_res, mp_drawings):
        pass