# BlendArMocap <br>

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
If you have multiple webcam device you may have to change the integer value until you find the device you want to use. <br>
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
When pressing the _Start Detection_ button a window will open containing the webcam feed and detection results.
The detection results are recorded in Blender at runtime. You can modify the recording start point by changing the keyframe start in Blender.<br>
May deactivate the rig when detecting if you have transfer animation results already.

### Animation Transfer<br>
The detection results can be transferred to a generated _rigify_ rig.<br>
The _new rigify face_ is **not** supported yet.<br>

**Drivers**<br>
Select the driver collection you want to transfer.<br>
You can select the parent, or just the collection containing the drivers on your choice.<br>
_May not change the collection names not the empty objects names._<br>

**Rig**<br>
Select the generated rigify rig you want to transfer to.<br>
_May not change the bone names._<br>

**Start Transfer**<br>
Transfers detection results from the collection to the rigify rig.<br>
Once the transfer is applied, new recording will be applied instantly to the rig.<br>

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
