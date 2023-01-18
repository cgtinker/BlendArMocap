import logging
from pathlib import Path
from typing import List, Any
import numpy as np
from ..cgt_core.cgt_core_chains import HolisticNodeChainGroup
from ..cgt_core.cgt_bpy import cgt_fc_actions, cgt_bpy_utils
from ..cgt_core.cgt_calculators_nodes import mp_calc_face_rot, mp_calc_pose_rot, mp_calc_hand_rot
from ..cgt_core.cgt_utils.cgt_timers import timeit
from ..cgt_core.cgt_utils.cgt_json import JsonData
from ..cgt_core.cgt_output_nodes import mp_hand_out, mp_face_out, mp_pose_out


class FreemocapLoader:
    mediapipe3d_frames_trackedPoints_xyz: np.array = None
    number_of_frames: int = -1
    number_of_tracked_points: int = -1

    first_body_point: int = 0
    first_left_hand_point: int = 33
    first_right_hand_point: int = 54
    first_face_point: int = 75

    def __init__(self, session_path: str, modal_operation=True, raw=False):
        """ Load the 3d mediapipe skeleton data from a freemocap session
            (not implemented) `reprojection_error_threshold:float` = filter data 
            by removing dottos with high reprojection error. I think for now I'll 
            just do a mean+2*standard_deviation cut-off that leaves in 95% of the data 
            (if stupidly assuming normal distribution) or something TODO: - do this better and smarter lol """
        self.frame = 0

        freemocap_session_path = Path(session_path)

        # data paths
        data_arrays_path = freemocap_session_path / 'DataArrays'
        mediapipe3d_xyz_npy_path = data_arrays_path / 'mediaPipeSkel_3d_smoothed.npy'
        mediapipe3d_reprojectionError_npy_path = data_arrays_path / 'mediaPipeSkel_reprojErr.npy'

        # session data
        self.mediapipe3d_frames_trackedPoints_xyz = np.load(str(mediapipe3d_xyz_npy_path)) / 1000  # convert to meters
        mediapipe3d_frames_trackedPoints_reprojectionError = np.load(str(mediapipe3d_reprojectionError_npy_path))
        self.number_of_frames = self.mediapipe3d_frames_trackedPoints_xyz.shape[0]
        self.number_of_tracked_points = self.mediapipe3d_frames_trackedPoints_xyz.shape[1]

        if not raw:
            index_order = np.array([0, 2, 1])
            mirrored_xyz = np.multiply(self.mediapipe3d_frames_trackedPoints_xyz, -1)
            indexed_xyz = np.array([[point[index_order] for point in subarray] for subarray in mirrored_xyz])
            self.mediapipe3d_frames_trackedPoints_xyz = indexed_xyz

            # init calculator node chain
        if modal_operation:
            self.node_chain = HolisticNodeChainGroup()

    def update(self):
        """ Provides holistic data for each (prerecorded) frame.
            Gets called on modal operation whenever blenders window manager updates. """
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
        """ Quickload raw data to f-curvers. Data may not be applied to rigs. """
        path = Path(__file__).parent.parent / 'cgt_core/cgt_defaults.json'
        json = JsonData(str(path))

        objs = []
        for i in range(0, self.first_left_hand_point):
            ob = cgt_bpy_utils.add_empty(0.01, 'cgt_' + json.pose[str(i)])
            objs.append(ob)
        for i in range(self.first_left_hand_point, self.first_right_hand_point):
            ob = cgt_bpy_utils.add_empty(0.01, 'cgt_' + json.hand[str(i - self.first_left_hand_point)] + '.L')
            objs.append(ob)
        for i in range(self.first_right_hand_point, self.first_face_point):
            ob = cgt_bpy_utils.add_empty(0.01, 'cgt_' + json.hand[str(i - self.first_right_hand_point)] + '.R')
            objs.append(ob)
        for i in range(self.first_face_point, self.mediapipe3d_frames_trackedPoints_xyz.shape[1]):
            ob = cgt_bpy_utils.add_empty(0.01, f'cgt_face_vertex_{str(i - self.first_face_point)}')
            objs.append(ob)

        frames = list(range(self.number_of_frames))
        for i in range(self.mediapipe3d_frames_trackedPoints_xyz.shape[1]):
            ob = objs[i]
            helper = cgt_fc_actions.create_actions([ob])[0]
            obj_data = self.mediapipe3d_frames_trackedPoints_xyz[:, i]
            x, y, z = obj_data[:, 0], obj_data[:, 1], obj_data[:, 2]
            helper.foreach_set('location', frames, x, y, z)

    @timeit
    def quickload_processed(self):
        """ Quickload data and calculate rotation data. Data may be applied to rigs. """
        logging.info("Started quickload process.")
        # deploy calculators
        calc_face = mp_calc_face_rot.FaceRotationCalculator()
        calc_pose = mp_calc_pose_rot.PoseRotationCalculator()
        calc_hand = mp_calc_hand_rot.HandRotationCalculator()

        # prepare tracking data
        frames = list(range(self.number_of_frames))
        hand_data, face_data, pose_data = [], [], []
        for frame in frames:
            this_frame_hand_data, this_frame_face_data, this_frame_pose_data = self.get_freemocap_session_data(frame)
            hand_data.append(this_frame_hand_data)
            pose_data.append(this_frame_pose_data)
            face_data.append(this_frame_face_data)

        # calc rotations and additional locations
        logging.info("Calculating additional rotations and locations for hands.")
        hand_results = np.array([calc_hand.update(data, frame) for data, frame in zip(hand_data, frames)], dtype=object)
        logging.info("Calculating additional rotations and locations for pose.")
        pose_results = np.array([calc_pose.update(data, frame) for data, frame in zip(pose_data, frames)], dtype=object)
        logging.info("Calculating additional rotations and locations for face.")
        face_results = np.array([calc_face.update(data, frame) for data, frame in zip(face_data, frames)], dtype=object)

        def split_transform_data(transform, m_frame):
            """ Returns locs and rots [[n (objs)], [x, y, z, idx, frame]] """
            if not len(transform.shape) > 1:
                return np.array([])
            return np.array([np.array([*x, i, m_frame]) for x, i in zip(transform[:, 1], transform[:, 0])])

        def flatten_generic_tracking_data(results):
            """ Returns locs and rots [[n], [n (objs)], [x, y, z, idx, frame]] for pose or face. """
            locations, rotations = [], []

            for _tuple, m_frame in results:
                loc, rot, _ = _tuple

                if len(loc) > 0:
                    locations.append(split_transform_data(np.array(loc, dtype=object), m_frame))
                if len(rot) > 0:
                    rotations.append(split_transform_data(np.array(rot, dtype=object), m_frame))

            return [np.array(locations, dtype=object), np.array(rotations, dtype=object)]

        def flatten_hand_tracking_data(results):
            """ Returns locs and rots [[n], [n (objs)], [x, y, z, idx, frame]] for left and right hand. """
            transform_arrays = [[], [], [], []]

            for _tuple, m_frame in results:
                locations, rotations, _ = _tuple

                left_loc_data, right_loc_data = np.array(locations, dtype=object)
                left_rot_data, right_rot_data = np.array(rotations, dtype=object)

                transform_data = [left_loc_data, right_loc_data, left_rot_data, right_rot_data]
                for arr, data in zip(transform_arrays, transform_data):
                    if not len(data) > 0:
                        continue
                    arr.append(split_transform_data(data, m_frame))

            return [np.array(arr, dtype=object) for arr in transform_arrays]

        # f-curves require raveled locations therefore flatten shapes or the tracking results
        pose_locations, pose_rotations = flatten_generic_tracking_data(pose_results)
        left_hand_locs, right_hand_locs, left_hand_rots, right_hand_rots = flatten_hand_tracking_data(hand_results)
        face_locations, face_rotations = flatten_generic_tracking_data(face_results)

        def apply_data_to_fcurves(data, objects: List[Any], data_path: str = 'location'):
            """ Applies data directly to fcurvers to prevent recalculation of fcurves. """
            if len(data.shape) != 3 or (data.shape[2] != 5):
                logging.error(f"Shape of data doesn't match {data.shape} - expected (n, n, 5).")
                return

            for object_idx in range(data.shape[1]):
                ob_data = data[:, object_idx]
                x, y, z, idx, frames = ob_data[:, 0], ob_data[:, 1], ob_data[:, 2], ob_data[:, 3], ob_data[:, 4]
                ob = objects[int(idx[0])]

                # overwrite action by default
                if data_path == "rotation_euler":
                    helper = cgt_fc_actions.create_actions([ob], overwrite=False)[0]
                else:
                    helper = cgt_fc_actions.create_actions([ob])[0]

                helper.foreach_set(data_path, frames, x, y, z)

        # apply data to blender
        logging.info("Create new f-curves and apply data.")
        hand_output = mp_hand_out.CgtMPHandOutNode()
        apply_data_to_fcurves(left_hand_locs, hand_output.left_hand, 'location')
        apply_data_to_fcurves(right_hand_locs, hand_output.right_hand, 'location')
        apply_data_to_fcurves(left_hand_rots, hand_output.left_hand, 'rotation_euler')
        apply_data_to_fcurves(right_hand_rots, hand_output.right_hand, 'rotation_euler')

        pose_output = mp_pose_out.MPPoseOutputNode()
        apply_data_to_fcurves(pose_locations, pose_output.pose, 'location')
        apply_data_to_fcurves(pose_rotations, pose_output.pose, 'rotation_euler')

        face_output = mp_face_out.MPFaceOutputNode()
        apply_data_to_fcurves(face_locations, face_output.face, 'location')
        apply_data_to_fcurves(face_rotations, face_output.face, 'rotation_euler')

    def get_freemocap_session_data(self, frame: int):
        """ Gets data from frame. Splits to default mediapipe formatting. """
        if self.frame == self.number_of_frames - 1:
            return None

        tracked_points = self.mediapipe3d_frames_trackedPoints_xyz[frame, :, :]

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
