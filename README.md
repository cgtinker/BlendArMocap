# BlendArMocap <br>
BlendArMocap is a Blender add-on to preform Hand, Face and Pose Detection in Blender using just a Webcam. 
The detected data can be easily transferred to rifigy rigs. <br>

<a href="http://www.youtube.com/watch?feature=player_embedded&v=pji6IHNCnAk
" target="_blank"><img src="http://img.youtube.com/vi/pji6IHNCnAk/0.jpg" 
alt="" width="240" height="180" border="10" /></a>


## Setup Instructions<br>
Blender has to be started with **elevated permissions** in order to install the required packages _opencv_ and _mediapipe_ via the add-ons preferences. 
Internet connection is required to install the required packages. To access the webcam feed blender has to be started with elevated permissions.<br><br>


### Starting Blender with elevated permissions<br>

**Windows**<br>
Right-click the blender application and choose: "Run as administrator"<br>

**Mac**<br>
Start Blender as admin by using the terminal:<br>
Navigate to Blender: `cd /Applications/Blender/Contents/MacOS`<br>
Run Blender as admin: `sudo ./Blender`<br>

**Linux**<br>
Start Blender as admin using the terminal:<br>
Navigate to Blender: `cd /usr/bin`<br>
Run Blender as admin: `sudo ./blender`<br>

When running Blender as admin using `sudo` in the terminal, it's required to enter the admin password. 
Once the add-on packages are installed and your terminal has the permission to access your camera, you can start Blender with just `./Blender`.<br>

## Capabilities<br>
BlendArMocap uses _opencv_ to access the users webcam and _mediapipe_ by google to preform **hand, face** and **pose detection** in blender.
The detected data can be used to drive a rigify rig.<br>

### Transferable data to rigify rigs
**Hands**<br>
- Hand rotation
- Finger x-angles

**Face**<br>
- Head rotation
- Open and close mouth 
- Open and close eyes

**Pose**<br>
- Hand position
- Hand orientation
- Elbow rotation
- Shoulder rotation
- Hip rotation

### Detection<br>
**Webcam Device Slot**<br>
If you have multiple webcam devices you may have to change the integer value until you find the device you want to use. <br>
Defaults the Webcam Device Slot should be **0**.

**Key Step**<br>
The Key Step determines the frequency of Keyframes made in Blender.
Adjust the Keyframe Step so the detection results in Blender match the recording speed. <br>

**Target**<br>
Select the detection target:
- Hands
- Face
- Pose

**Start Detection**<br>
When pressing the _Start Detection_ button a window will open which contains the webcam feed and detection results.
The detection results are recorded in Blender at runtime. You can modify the recording starting point by changing the keyframe start in Blender.<br>
May deactivate the rig while detecting if you have transferred animation results previously.
To finish the recording press 'Q', 'ESC' or the 'RIGHT MOUSE BUTTON'.

### Animation Transfer<br>
The detection results can be transferred to a generated _rigify_ rig.<br>
The _new rigify face_ is **not** supported yet.<br>

**Drivers**<br>
Select the driver collection you want to transfer.<br>
You can select the parent, or just the collection containing the drivers of your choice.<br>
_May not change the collection names nor the empty objects names._<br>

**Rig**<br>
Select the generated rigify rig you want to transfer to.<br>
_May not change the bone names of the rigify rig._<br>

**Start Transfer**<br>
Transfers detection results from the selected collection to the rigify rig.<br>
Once the transfer has taken place, new recordings will be applied instantly to the rig.<br>
So there is no need to transfer twice.<br>


###Data Assignment<br>

| Driver Source     | Constraint type | Rigify Pose Bone | 
|-------------------|-----------------|------------------|
| hip_center        | copy rotation   | torso            |
| shoulder_center   | copy rotation   | chest            | 
| left_hand_ik      | copy location   | hand_ik.R        | 
| right_hand_ik     | copy location   | hand_ik.L        | 
| left_forearm_ik   | copy location   | forearm_tweak.L  | 
| right_forearm_ik  | copy location   | forearm_tweak.R  | 
| left_index_ik     | copy location   | hand_ik.R        | 
| right_index_ik    | copy location   | hand_ik.L        |

| Hand Driver Source | Constraint type | Rigify Hand Bone |
|--------------------|-----------------|------------------|
| wrist              | copy rotation   | hand_ik          |
| thumb_cmc          | copy rotation   | thumb.01         |
| thumb_mcp          | copy rotation   | thumb.02         |
| thumb_ip           | copy rotation   | thumb.03         |
| thumb_tip          | copy rotation   | thumb.01         |
| index_finger_mcp   | copy rotation   | f_index.01       |
| index_finger_pip   | copy rotation   | f_index.02       |
| index_finger_dip   | copy rotation   | f_index.03       |
| index_finger_tip   | copy rotation   | f_index.01       |
| middle_finger_mcp  | copy rotation   | f_middle.01      |
| middle_finger_pip  | copy rotation   | f_middle.02      |
| middle_finger_dip  | copy rotation   | f_middle.03      |
| middle_finger_tip  | copy rotation   | f_middle.01      |
| ring_finger_mcp    | copy rotation   | f_ring.01        |
| ring_finger_pip    | copy rotation   | f_ring.02        |
| ring_finger_dip    | copy rotation   | f_ring.03        |
| ring_finger_tip    | copy rotation   | f_ring.01        |
| pinky_mcp          | copy rotation   | f_pinky.01       |
| pinky_pip          | copy rotation   | f_pinky.02       |
| pinky_dip          | copy rotation   | f_pinky.03       |
| pinky_tip          | copy rotation   | f_pinky.01       |

| Face Driver Source | Constraint type | Rigify Face Bone |
|--------------------|-----------------|------------------|
| head               | copy rotation   | head             |
| chin               | copy rotation   | jaw_master       |
| right_eye_t        | copy location   | lid.T.R.002      |
| right_eye_b        | copy location   | lid.B.R.002      |
| left_eye_t         | copy location   | lid.T.L.002      |
| left_eye_b         | copy location   | lid.B.L.002      |
| mouth_t            | copy location   | lip.T            |
| mouth_b            | copy location   | lip.B            |
| mouth_l            | copy location   | lips.R           |
| mouth_r            | copy location   | lips.L           |


## License
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

Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com
