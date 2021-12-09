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

bl_info = {
    "name": "ml_rt_detector",
    "description": "desc",
    "author": "cgtinker",
    "version": (2, 0, 0),
    "blender": (2, 90, 0),
    "location": "3D View > Tool",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}


import os
import sys
import bpy
# getting access to the current dir - necessary to access blender file location
blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

# append sys path to dir
main_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'module')
sys.path.append(main_dir)

#from ml_detection.stream import hand
from utils import log
from utils.open_cv import stream
from bridge import events, mp_hand_op
from custom_data import cd_hand
import importlib

#importlib.reload(hand)
importlib.reload(log)
importlib.reload(stream)
importlib.reload(events)
importlib.reload(cd_hand)
importlib.reload(mp_hand_op)

def main():
    # hand = cd_hand.Hand()
    
    log.init_logger('debug')
    s = stream.Webcam()

    # observe data
    _observer = events.BpyHandUpdateReceiver()
    _listener = events.UpdateListener()
    _listener.attach(_observer)

    # hand.main(s, _listener)
    del s
    

def register():
    bpy.utils.register_class(mp_hand_op.FeatureDetectionModal)


def unregister():
    bpy.utils.unregister_class(mp_hand_op.FeatureDetectionModal)

    
if __name__ == '__main__':
    register()
    # test call
    bpy.ops.wm.feature_detection_modal()

