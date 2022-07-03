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

from . import detector_interface
from pathlib import Path
import numpy as np
import bpy


class FreemocapLoader(detector_interface.RealtimeDetector):
    mediapipe3d_frames_trackedPoints_xyz: np.array = None
    number_of_frames: int = -1
    number_of_tracked_points: int = -1

    first_body_point: int = 0
    first_left_hand_point: int = 33
    first_right_hand_point: int = 54
    first_face_point: int = 75

    mp_res = None

    def image_detection(self):
        while self.frame < self.number_of_frames:
            holistic_data = self.get_detection_results()
            # JSM NOTE - spoofing the method in `self.exec_detection`
            self.listener.data = holistic_data
            self.update_listeners()
            return True
        return False

    def initialize_model(self):
        """Load the 3d mediapipe skeleton data from a freemocap session
        (not implemented) `reprojection_error_threshold:float` = filter data by removing dottos with high reprojection error. I think for now I'll just do a mean+2*standard_deviation cut-off that leaves in 95% of the data (if stupidly assuming normal distribution) or something TODO - do this better and smarter lol
        """
        print("Loading FREEMOCAP data...")
        freemocap_session_path = Path(bpy.context.scene.m_cgtinker_mediapipe.freemocap_session_path)

        data_arrays_path = freemocap_session_path / 'DataArrays'
        mediapipe3d_xyz_npy_path = data_arrays_path / 'mediaPipeSkel_3d_smoothed.npy'
        mediapipe3d_reprojectionError_npy_path = data_arrays_path / 'mediaPipeSkel_reprojErr.npy'

        self.mediapipe3d_frames_trackedPoints_xyz = np.load(str(mediapipe3d_xyz_npy_path)) / 1000  # convert to meters
        mediapipe3d_frames_trackedPoints_reprojectionError = np.load(str(mediapipe3d_reprojectionError_npy_path))

        # figure out unfiltered first before getting stuck on filtering the data, dummy ;-*
        # mediapipe3d_frames_trackedPoints_xyz = self.filter_dottos_by_reprojection_error(mediapipe3d_frames_trackedPoints_xyz,mediapipe3d_frames_trackedPoints_reprojectionError,)
        self.number_of_frames = self.mediapipe3d_frames_trackedPoints_xyz.shape[0]
        self.number_of_tracked_points = self.mediapipe3d_frames_trackedPoints_xyz.shape[1]

        # remove?
        # number_of_body_pose_points = 33
        # number_of_hand_points = 21
        # number_of_face_points = 468
        # self.first_body_point = 0
        # self.first_left_hand_point = number_of_body_pose_points
        # self.first_right_hand_point = number_of_body_pose_points + number_of_hand_points
        # self.first_face_point = number_of_body_pose_points + (number_of_hand_points * 2)

    def get_detection_results(self, mp_res=None):
        if self.frame == self.number_of_frames - 1:
            return None
        tracked_points = self.mediapipe3d_frames_trackedPoints_xyz[self.frame, :, :]

        this_frame_body_data = tracked_points[0:self.first_left_hand_point]
        this_frame_left_hand_data = tracked_points[self.first_left_hand_point:self.first_right_hand_point]
        this_frame_right_hand_data = tracked_points[self.first_right_hand_point:self.first_face_point]
        this_frame_face_data = tracked_points[self.first_face_point:]

        this_frame_body_data = [[i, p] for i, p in enumerate(this_frame_body_data)]
        this_frame_left_hand_data = [[i, p] for i, p in enumerate(this_frame_left_hand_data)]
        this_frame_right_hand_data = [[i, p] for i, p in enumerate(this_frame_right_hand_data)]
        this_frame_face_data = [[i, p] for i, p in enumerate(this_frame_face_data)]

        # left seems to be missing data at idx 0
        print("LEFT", this_frame_left_hand_data, len(this_frame_left_hand_data))
        print("RIGHT", this_frame_right_hand_data, len(this_frame_right_hand_data))
        holistic_data = [[[this_frame_left_hand_data], [this_frame_right_hand_data]],
                         [this_frame_face_data], this_frame_body_data]
        return holistic_data

    def contains_features(self, mp_res):
        pass

    def draw_result(self, s, mp_res, mp_drawings):
        pass

