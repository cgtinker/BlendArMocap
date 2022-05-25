# BlendArMocap <br>
BlendArMocap is a [Blender](https://www.blender.org/) add-on to preform Hand, Face and Pose Detection using [Googles Mediapipe](https://google.github.io/mediapipe/).
To detection requires a movie file input or a webcam connected to the computer.
The detected data can be easily transferred to [rifigy rigs](https://docs.blender.org/manual/en/2.81/addons/rigging/rigify.html). <br>

<a href="http://www.youtube.com/watch?feature=player_embedded&v=pji6IHNCnAk
" target="_blank"><img src="http://img.youtube.com/vi/pji6IHNCnAk/0.jpg" 
alt="" width="240" height="180" border="10" /></a>


## Setup Instructions<br>
Blender has to be started with **elevated permissions** in order to install the required packages [_opencv_](https://opencv.org) and [_mediapipe_](https://google.github.io/mediapipe/) via the add-ons preferences. 
Internet connection is required to install the required packages. It's recommended to disable VPN's during the installation processes. 
Also Blender may has to be restarted during the installation process. To access the webcam feed blender usually has to be started with elevated permissions.<br><br>


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
BlendArMocap uses _opencv_ to access the users webcam or movie file and _mediapipe_ by google to preform **hand, face** and **pose detection** in blender.
The detected data can be used to drive a rigify rig.<br>

### Transferable data to rigify rigs
**Hands**<br>
- Hand rotation
- Finger x-angles
- Finger y-angles

**Face**<br>
- Head rotation
- Open and close Mouth
- Relative Mouth Corners
- Open and close eyes
- Eyebrow Movement

**Pose**<br>
- Hand position
- Hand orientation
- Elbow position
- Shoulder position
- Shoulder rotation
- Hip rotation
- Knee position
- Ankle position
- Foot orientation

### Detection<br>
**Type**<br>
Select the data type you want to use as input:
- Stream
- Movie

**Webcam Device Slot**<br>
If you have multiple webcam devices you may have to change the integer value until you find the device you want to use. <br>
Defaults the Webcam Device Slot should be **0**.

**File Path**<br>
Select the path to your movie file. Preferable reduce it in size before starting the detection.

**Key Step**<br>
The Key Step determines the frequency of Keyframes made in Blender.
Adjust the Keyframe Step so the detection results in Blender match the recording speed. <br>

**Target**<br>
Select the detection target:
- Hands
- Face
- Pose
- Holistic

**Start Detection**<br>
When pressing the _Start Detection_ button a window will open which contains the webcam or movie feed and detection results.
The detection results are recorded in Blender at runtime. You can modify the recording starting point by changing the keyframe start in Blender.<br>
May deactivate the rig while detecting if you have transferred animation results previously.
To finish the recording press 'Q' or the "Stop Detection" button.

### Animation Transfer<br>
The detection results can be transferred to a generated _rigify_ rig.<br>
The _new rigify face_ is **not** supported yet.<br>

**Drivers**<br>
Select the driver collection you want to transfer.<br>
You can select the parent collection, or just the collection containing the drivers of your choice.<br>
_May not change the collection names nor the empty objects names._<br>

**Rig**<br>
Select the generated rigify rig you want to transfer to.<br>
_May not change the bone names of the rigify rig._<br>

**Overwrite Drivers**<br>
When selected, drivers and constraints will be overwritten with default values.

**Leg Transfer (Experimental)**<br>
By default, only the upper body motion of the detection results are getting transferred.
_The feature is only visible, as long either 'Holistic' or 'Pose' is selected as detection type._

**Start Transfer**<br>
Transfers detection results from the selected collection to the rigify rig.<br>
Once the transfer has taken place, new recordings will be applied instantly to the rig.<br>
_There is no need to transfer twice._<br>


##How to manipulate transfer results</br>
**Manual**</br>
Translate or rotation the bone you want to offset. Make sure to create keyframes while doing so as the correction may change the entire animation. </br>
_Pose Mode > Select control bone > Object Properties_

**Constraints**</br>
The data is copied from the drivers by constraints. In some cases, it might be useful to change or remove constraints.</br>
_Pose Mode > Select control bone > Bone Constraints_

**Custom Properties**</br>
On some bones, custom properties will be added upon the transfer. 
The custom properties help to manipulate the minimum and maximum mapping values of the driver.</br>
_Pose Mode > Select control bone > Object Properties > Custom Properties_

**Offset time**</br>
If you want to change the speed of an animation.
1. Select the drivers in the collection you want to smooth, or select all.</br>
_Right click collection > Select Objects_
2. Navigate to or open the graph editor, select make sure the graphs of the objects are selected.</br>
_Timeline > 'A'_
3. Make sure your the currently selected frame is at the start of your animation (usually 0).
4. Scale the timeline to increase or decrease the offset between keyframes.</br>
_Timeline > 'S'_


**Smooth results**</br>
1. Select the drivers in the collection you want to smooth, or select all.</br>
_Right click collection > Select Objects_
2. Navigate to or open the graph editor, select make sure the graphs of the objects are selected.</br>
_Graph editor > 'A'_
3. If you used a key-step while recording, resample the curves.
_Graph editor > Key > Sample Keyframes_
4. Finally, smooth the animation. You may repeat this step till you reach your desired result.
_Graph editor > Key > Smooth Key_

| Manipulation Options | meaning          | location             |
|----------------------|------------------|----------------------|
| m                    | manual           | pose mode            |
| c                    | constraint       | bone constraint      |
| p                    | custom property  | bone custom property |



### Data Assignment<br>

| Rigify Pose Bone      | Constraint type | Driver Source    | Opts | 
|-----------------------|-----------------|------------------|------|
| torso                 | copy rotation   | hip_center       | m, c |
| chest                 | copy rotation   | shoulder_center  | m, c |
| hand_ik.R             | child of        | left_hand_ik     | m, c |
| hand_ik.L             | child of        | right_hand_ik    | m, c |
| upper_arm_ik_target.L | limit distance  | left_forearm_ik  | m, c |
| upper_arm_ik_target.R | limit distance  | right_forearm_ik | m, c |
| foot_ik.R             | child of        | left_foot_ik     | m, c |
| foot_ik.L             | child of        | right_foot_ik    | m, c |
| thigh_ik_target.L     | limit distance  | right_shin_ik    | m, c |
| thigh_ik_target.R     | limit distance  | left_shin_ik     | m, c |

| Hand Driver Source | Constraint type | Rigify Hand Bone | Opts    |
|--------------------|-----------------|------------------|---------|
| wrist              | copy rotation   | hand_ik          | m, c    |
| thumb_cmc          | copy rotation   | thumb.01         | m, c, p |
| thumb_mcp          | copy rotation   | thumb.02         | m, c, p |
| thumb_ip           | copy rotation   | thumb.03         | m, c, p |
| thumb_tip          | copy rotation   | thumb.01         | m, c, p |
| index_finger_mcp   | copy rotation   | f_index.01       | m, c, p |
| index_finger_pip   | copy rotation   | f_index.02       | m, c, p |
| index_finger_dip   | copy rotation   | f_index.03       | m, c, p |
| index_finger_tip   | copy rotation   | f_index.01       | m, c, p |
| middle_finger_mcp  | copy rotation   | f_middle.01      | m, c, p |
| middle_finger_pip  | copy rotation   | f_middle.02      | m, c, p |
| middle_finger_dip  | copy rotation   | f_middle.03      | m, c, p |
| middle_finger_tip  | copy rotation   | f_middle.01      | m, c, p |
| ring_finger_mcp    | copy rotation   | f_ring.01        | m, c, p |
| ring_finger_pip    | copy rotation   | f_ring.02        | m, c, p |
| ring_finger_dip    | copy rotation   | f_ring.03        | m, c, p |
| ring_finger_tip    | copy rotation   | f_ring.01        | m, c, p |
| pinky_mcp          | copy rotation   | f_pinky.01       | m, c, p |
| pinky_pip          | copy rotation   | f_pinky.02       | m, c, p |
| pinky_dip          | copy rotation   | f_pinky.03       | m, c, p |
| pinky_tip          | copy rotation   | f_pinky.01       | m, c, p |

| Face Driver Source | Constraint type | Rigify Face Bone | Opts    |
|--------------------|-----------------|------------------|---------|
| head               | copy rotation   | head             | m, c    |
| chin               | copy rotation   | jaw_master       | m, c    |
| right_eye_t        | copy location   | lid.T.R.002      | m, c, p |
| right_eye_b        | copy location   | lid.B.R.002      | m, c, p |
| left_eye_t         | copy location   | lid.T.L.002      | m, c, p |
| left_eye_b         | copy location   | lid.B.L.002      | m, c, p |
| mouth_t            | copy location   | lip.T            | m, c, p |
| mouth_b            | copy location   | lip.B            | m, c, p |
| mouth_l            | copy location   | lips.R           | m, c, p |
| mouth_r            | copy location   | lips.L           | m, c, p |
| eyebrow_in_l       | copy location   | brow.T.L.001     | m, c, p |
| eyebrow_out_l      | copy location   | brow.T.L.003     | m, c, p |
| eyebrow_in_r       | copy location   | brow.T.R.001     | m, c, p |
| eyebrow_out_r      | copy location   | brow.T.R.003     | m, c, p |

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


<br><br>
If you want to support the development you can either donate at [Gumroad](https://cgtinker.gumroad.com/) or become a [Patreon](https://www.patreon.com/cgtinker).
<br>Would be lovely, thanks!