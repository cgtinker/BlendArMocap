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

from abc import ABC, abstractmethod
import enum
from pathlib import Path
import numpy as np
from mediapipe import solutions
from ..cgt_patterns import observer_pattern


class RealtimeDetector(ABC):
    stream = None
    input_type = 0
    observer, listener, _timer = None, None, None
    solution = None
    drawing_utils, drawing_style, = None, None

    key_step = 4
    frame = None

    def __init__(self, frame_start: int = 0, key_step: int = 4, input_type: int = None):
        self.input_type = input_type  # stream or movie or freemocap (0/1/2)
        self.drawing_utils = solutions.drawing_utils
        self.drawing_style = solutions.drawing_styles
        self.frame = frame_start
        self.key_step = key_step

    @abstractmethod
    def image_detection(self):
        """ Run mediapipes detection on an image using the active model. """
        pass

    def init_bridge(self, observer: observer_pattern.Observer, listener: observer_pattern.Listener, ):
        """ Set up the data bridge to blender or to prints for debugging purposes. """
        self.observer = observer
        self.listener = listener
        self.listener.attach(self.observer)

    @abstractmethod
    def initialize_model(self):
        pass

    @abstractmethod
    def get_detection_results(self, mp_res):
        pass

    @abstractmethod
    def contains_features(self, mp_res):
        pass

    @abstractmethod
    def draw_result(self, s, mp_res, mp_drawings):
        pass

    def exec_detection(self, mp_lib):
        self.stream.update()
        updated = self.stream.updated

        if not updated and self.input_type == 0:
            # ignore if an update fails while stream detection
            return True

        elif not updated and self.input_type == 1:
            # stop detection if update fails while movie detection
            return False

        if self.stream.frame is None:
            # ignore frame if not available
            return True

        # detect features in frame
        self.stream.frame.flags.writeable = False
        self.stream.set_color_space('rgb')
        mp_res = mp_lib.process(self.stream.frame)
        self.stream.set_color_space('bgr') 

        # proceed if contains features
        if not self.contains_features(mp_res):
            self.stream.draw()
            if self.stream.exit_stream():
                return False
            return True

        # draw results
        self.draw_result(self.stream, mp_res, self.drawing_utils)
        self.stream.draw()

        # update listeners
        # JSM NOTE - this is where the Mediapipe data goes into Blender!
        self.listener.data = self.get_detection_results(mp_res)
        self.update_listeners()

        # exit stream
        if self.stream.exit_stream():
            return False
        return True

    def load_freemocap_mediapipe3d_data(self, freemocap_session_path:Path):
        """Load the 3d mediapipe skeleton data from a freemocap session
        (not implemented) `reprojection_error_threshold:float` = filter data by removing dottos with high reprojection error. I think for now I'll just do a mean+2*standard_deviation cut-off that leaves in 95% of the data (if stupidly assuming normal distribution) or something TODO - do this better and smarter lol
        """
        data_arrays_path = freemocap_session_path / 'DataArrays'
        
        mediapipe3d_xyz_npy_path = data_arrays_path / 'mediaPipeSkel_3d_smoothed.npy'
        mediapipe3d_reprojectionError_npy_path = data_arrays_path / 'mediaPipeSkel_reprojErr.npy'
        
        mediapipe3d_frames_trackedPoints_xyz = np.load(str(mediapipe3d_xyz_npy_path))/1000 #convert to meters
        mediapipe3d_frames_trackedPoints_reprojectionError = np.load(str(mediapipe3d_reprojectionError_npy_path))
        
        # figure out unfiltered first before getting stuck on filtering the data, dummy ;-*
        # mediapipe3d_frames_trackedPoints_xyz = self.filter_dottos_by_reprojection_error(mediapipe3d_frames_trackedPoints_xyz,mediapipe3d_frames_trackedPoints_reprojectionError,)
        
        number_of_frames = mediapipe3d_frames_trackedPoints_xyz.shape[0]
        number_of_tracked_points = mediapipe3d_frames_trackedPoints_xyz.shape[1]
        number_of_body_pose_points = 33
        number_of_hand_points = 21
        # number_of_face_points = 468 
        


        
        for this_frame_number in range(number_of_frames):
            #per frame
            this_frame_body_data = []
            this_frame_right_hand_data = []
            this_frame_left_hand_data = []
            this_frame_face_data = []

            first_body_point = 0
            first_left_hand_point = number_of_body_pose_points
            first_right_hand_point = number_of_body_pose_points + number_of_hand_points
            first_face_point = number_of_body_pose_points + (number_of_hand_points*2)
            

            this_frame_trackedPoint_xyz = mediapipe3d_frames_trackedPoints_xyz[this_frame_number,:,:]
            for this_tracked_point_number, this_tracked_point_xyz in enumerate(this_frame_trackedPoint_xyz):
                #per tracked_point

                this_tracked_point_xyz_list = this_frame_trackedPoint_xyz[this_tracked_point_number,:].tolist()

                if this_tracked_point_number < first_left_hand_point: # body/pose points
                    this_frame_body_data.append([this_tracked_point_number, this_tracked_point_xyz_list])

                elif this_tracked_point_number < first_right_hand_point: # left_hand points
                    this_frame_left_hand_data.append([this_tracked_point_number-first_left_hand_point, this_tracked_point_xyz_list])

                elif this_tracked_point_number < first_face_point: # right_hand points
                    this_frame_right_hand_data.append([this_tracked_point_number-first_right_hand_point, this_tracked_point_xyz_list])
                
                else: # face points
                    this_frame_face_data.append([this_tracked_point_number-first_face_point, this_tracked_point_xyz_list])

            this_frame_holistic_data = [[[this_frame_left_hand_data], [this_frame_right_hand_data]], [this_frame_face_data], this_frame_body_data]
                
            #JSM NOTE - spoofing the method in `self.exec_detection`
            self.listener.data = this_frame_holistic_data
            self.update_listeners()

    def filter_dottos_by_reprojection_error(self,
     mediapipe3d_frames_trackedPoints_xyz:np.ndarray,
     mediapipe3d_frames_trackedPoints_reprojectionError:np.ndarray,
     reprojection_error_cuttoff:float = 15.0,):
    #  """default cut-off based on `freemocap\dev_scratchpad\examine_reprojection_error.ipynb` TODO - do this in a better and more smarter like way :thumb: """

        # mean_reprojection_error = np.nanmean(mediapipe3d_frames_trackedPoints_reprojectionError)
        # standard_deviation_reprojection_error = np.nanstd(mediapipe3d_frames_trackedPoints_reprojectionError)
        # confidence_interval_99_cutoff = mean_reprojection_error + (3*standard_deviation_reprojection_error)

        bad_dottos_mask = mediapipe3d_frames_trackedPoints_reprojectionError<reprojection_error_cuttoff
        mediapipe3d_frames_trackedPoints_xyz[bad_dottos_mask] = np.nan

    def update_listeners(self):
        self.frame += self.key_step
        self.listener.frame = self.frame
        self.listener.notify()

    def cvt2landmark_array(self, landmark_list):
        """landmark_list: A normalized landmark list proto message to be annotated on the image."""
        return [[idx, [landmark.x, landmark.y, landmark.z]] for idx, landmark in enumerate(landmark_list.landmark)]

    def __del__(self):
        try:
            self.listener.detach(self.observer)
            del self.observer
            del self.listener
            del self.stream
        except:
            print("it's probably fine lol")
