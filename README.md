# BlendArMocap <br>
BlendArMocap is a [Blender](https://www.blender.org/) add-on to preform Hand, Face and Pose Detection using [Googles Mediapipe](https://google.github.io/mediapipe/).
To detection requires a movie file input or a webcam connected to the computer.
The detected data can be easily transferred to [rifigy rigs](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html). <br>


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
By default, only the upper body motion of the detection results are getting transferred.<br>
_The feature is only visible, as long either 'Holistic' or 'Pose' is selected as detection type._

**Start Transfer**<br>
Transfers detection results from the selected collection to the rigify rig.<br>
Once the transfer has taken place, new recordings will be applied instantly to the rig.<br>
_There is no need to transfer twice._<br>


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
For tutorials regarding my tools may check out my [YouTube-Channel](https://www.youtube.com/user/MrSerAdos).
If you want to support me you can become a [Patreon](https://www.patreon.com/cgtinker).