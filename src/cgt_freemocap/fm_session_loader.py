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
from pathlib import Path
import numpy as np
import multiprocessing as mp
from ..cgt_core.cgt_core_chains import HolisticNodeChainGroup
from ..cgt_core.cgt_bpy import fc_actions, cgt_bpy_utils
from ..cgt_core.cgt_calculators_nodes import calc_face_rot, calc_pose_rot, calc_hand_rot
from ..cgt_core.cgt_utils.cgt_timers import timeit
from ..cgt_core.cgt_utils.cgt_json import JsonData


class FreemocapLoader:
    mediapipe3d_frames_trackedPoints_xyz: np.array = None
    number_of_frames: int = -1
    number_of_tracked_points: int = -1

    first_body_point: int = 0
    first_left_hand_point: int = 33
    first_right_hand_point: int = 54
    first_face_point: int = 75

    def __init__(self, session_path: str, flag=True):
        """ Load the 3d mediapipe skeleton data from a freemocap session
            (not implemented) `reprojection_error_threshold:float` = filter data 
            by removing dottos with high reprojection error. I think for now I'll 
            just do a mean+2*standard_deviation cut-off that leaves in 95% of the data 
            (if stupidly assuming normal distribution) or something TODO: - do this better and smarter lol """
        self.frame = 0

        freemocap_session_path = Path(session_path)
        logging.debug(f"Loading FREEMOCAP data...\n{freemocap_session_path}")

        # data paths
        data_arrays_path = freemocap_session_path / 'DataArrays'
        mediapipe3d_xyz_npy_path = data_arrays_path / 'mediaPipeSkel_3d_smoothed.npy'
        mediapipe3d_reprojectionError_npy_path = data_arrays_path / 'mediaPipeSkel_reprojErr.npy'

        # session data
        self.mediapipe3d_frames_trackedPoints_xyz = np.load(str(mediapipe3d_xyz_npy_path)) / 1000  # convert to meters
        mediapipe3d_frames_trackedPoints_reprojectionError = np.load(str(mediapipe3d_reprojectionError_npy_path))
        self.number_of_frames = self.mediapipe3d_frames_trackedPoints_xyz.shape[0]
        self.number_of_tracked_points = self.mediapipe3d_frames_trackedPoints_xyz.shape[1]

        # init calculator node chain
        if flag:
            self.node_chain = HolisticNodeChainGroup()

    def update(self):
        """ Provides holistic data for each (prerecorded) frame. """
        if self.frame < self.number_of_frames:
            holistic_data = self.get_freemocap_session_data(self.frame)
            if holistic_data is None:
                return False

            self.frame += 1
            self.node_chain.update(holistic_data, self.frame)

            return True
        return False

    @timeit
    def quickload_raw(self):
        """ Quickload raw data. """
        path = Path(__file__).parent.parent / 'cgt_core/cgt_defaults.json'
        json = JsonData(str(path))

        objs = []
        for i in range(0, self.first_left_hand_point):
            ob = cgt_bpy_utils.add_empty(0.01, 'cgt_'+json.pose[str(i)])
            objs.append(ob)
        for i in range(self.first_left_hand_point, self.first_right_hand_point):
            ob = cgt_bpy_utils.add_empty(0.01, 'cgt_'+json.hand[str(i-self.first_left_hand_point)]+'.L')
            objs.append(ob)
        for i in range(self.first_right_hand_point, self.first_face_point):
            ob = cgt_bpy_utils.add_empty(0.01, 'cgt_'+json.hand[str(i-self.first_right_hand_point)]+'.R')
            objs.append(ob)
        for i in range(self.first_face_point, self.mediapipe3d_frames_trackedPoints_xyz.shape[1]):
            ob = cgt_bpy_utils.add_empty(0.01, f'cgt_face_vertex_{str(i-self.first_face_point)}')
            objs.append(ob)

        frames = list(range(self.number_of_frames))
        for i in range(self.mediapipe3d_frames_trackedPoints_xyz.shape[1]):
            ob = objs[i]
            helper = fc_actions.create_actions([ob])[0]
            obj_data = self.mediapipe3d_frames_trackedPoints_xyz[:, i]
            x, y, z = obj_data[:, 0], obj_data[:, 1], obj_data[:, 2]
            helper.foreach_set('location', frames, x, y, z)

    @timeit
    def quickload_processed(self):
        # deploy calculators
        calc_face = calc_face_rot.FaceRotationCalculator()
        calc_pose = calc_pose_rot.PoseRotationCalculator()
        calc_hand = calc_hand_rot.HandRotationCalculator()

        # prepare tracking data
        frames = list(range(self.number_of_frames))
        np.multiply(self.mediapipe3d_frames_trackedPoints_xyz, -1)
        hand_data, face_data, pose_data = [], [], []
        idx = np.array([0, 2, 1])
        for frame in frames:
            tracked_points = self.mediapipe3d_frames_trackedPoints_xyz[frame, :, :]
            tracked_points = [point[idx] for point in tracked_points]

            this_frame_body_data = list(enumerate(tracked_points[0:self.first_left_hand_point]))
            this_frame_left_hand_data = list(enumerate(tracked_points[self.first_left_hand_point:self.first_right_hand_point]))
            this_frame_right_hand_data = list(enumerate(tracked_points[self.first_right_hand_point:self.first_face_point]))
            this_frame_face_data = list(enumerate(tracked_points[self.first_face_point:]))

            hand_data.append([[this_frame_left_hand_data], [this_frame_right_hand_data]])
            pose_data.append(this_frame_body_data)
            face_data.append([this_frame_face_data])

        # calculate rotations
        with mp.Pool(processes=mp.cpu_count()) as pool:
            res_a = pool.map(calc_hand.update, hand_data)
            res_b = pool.map(calc_face.update, face_data)
            res_c = pool.map(calc_pose.update, pose_data)

    def get_freemocap_session_data(self, frame: int):
        """ Gets data from frame. Splits to default mediapipe formatting. """
        if self.frame == self.number_of_frames - 1:
            return None

        tracked_points = self.mediapipe3d_frames_trackedPoints_xyz[frame, :, :]
        tracked_points = np.array([[-x, -z, -y] for x, y, z in tracked_points])

        this_frame_body_data = tracked_points[0:self.first_left_hand_point]
        this_frame_left_hand_data = tracked_points[self.first_left_hand_point:self.first_right_hand_point]
        this_frame_right_hand_data = tracked_points[self.first_right_hand_point:self.first_face_point]
        this_frame_face_data = tracked_points[self.first_face_point:]

        this_frame_body_data = list(enumerate(this_frame_body_data))
        this_frame_left_hand_data = list(enumerate(this_frame_left_hand_data))
        this_frame_right_hand_data = list(enumerate(this_frame_right_hand_data))
        this_frame_face_data = list(enumerate(this_frame_face_data))

        holistic_data = [[[this_frame_left_hand_data], [this_frame_right_hand_data]],
                         [this_frame_face_data], this_frame_body_data]
        return holistic_data


def main():
    path = '/Users/Scylla/Downloads/sesh_2022-09-19_16_16_50_in_class_jsm/'
    loader = FreemocapLoader(path, False)
    loader.quickload_processed()
    pass


if __name__ == '__main__':
    main()
