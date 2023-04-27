# BlendArMocap <br>

BlendArMocap is a tool preform markerless tracking within Blender using Google’s [Mediapipe](https://google.github.io/mediapipe/). The main goal of the add-on is to efficiently transfer the generated detection results to rigs.<br>

For more information, please refer to the [documentation](https://cgtinker.github.io/BlendArMocap/).


### Features
- Detection of [Mediapipe](https://google.github.io/mediapipe/) detection results in stream or video
    - Calculation of rotations for mediapipe data
- Import of [Freemocap](https://freemocap.org) mediapipe session data
- Transfer tracking data to rigs and generate new transfer configurations
  - currently, officially supports the transfer to generated [rifigy rigs](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html)
  
## Quick Start

1. Download this repository as a .zip file
2. Open Blender > Edit > Prefrences > Add-ons > Install > Point to the zip file of this repository
3. Install it and also install the dependencies, note the dependencies 'Installed' column should say 'True' for all dependencies and finally Click 'Save Prefrences'
4. Open 'BlenderAR' Panel, select 'WebCam' from the drop down and click 'Start Detection'. Make sure whatever is in the 'Target' is visible to the camera and a new window should open that will show the skeleton tracker.
5. Click 'Stop Detection' to stop the webcam anytime.

### For Mac Users:

If Blender is crashing at any point during 'Quick Start', mostly likely it is because the Blender App doesn't have the 'Camera' permissions so Apple Security system is preventing it from starting. To work around that just do the following:

- Make sure in your "Security & Privacy" settings > Camera > Terminal.app is checked on (terminal should have access to camera).
- Open Terminal and start Blender by typing it's path. e.g /Applications/Blender.app/Contents/MacOS/Blender
- Open the BlenderAR Panel and Click 'Start Detection'


### Mediapipe Detection

Run Mediapipe within Blender to detect pose, hand, face or holistic features.
BlendArMocap calculates rotation data based on the detection results at runtime to drive rigs.<br>

**Caution:** Requires external dependencies which can be installed via the add-on preferences with elevated privileges.


### Freemocap import

[Freemocap](https://freemocap.org) session data can be saved in a `session folder` which then can be imported using BlendArMocap.
To import session data to blender, set the path to the session directory and press the import button.


### Transfer

Currently there's a preset configuration to transfer detection results to generated humanoid [rifigy rigs](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html).
To transfer, just select the generated humaniod rig as transfer target and press the `Transfer` Button.
The transfer is based on mapping objects which you can modify. The modifications you can save as own configurations.<br>

You'll find the mapping objects in the collections generated while tracking such as `cgt_HANDS`.
Mapping instructions are stored as object properties and can be modified in the `object data properties` panel (where the constraints live).
Here the concept of mapping objects:

````
mapping_object: object with instructions and constraints
driver_object: generated driver based on instructions
target_object: copies values from driver_object via constraints
````

If you happen to create a configuration to support another rig, feel free to send it to me for sharing via hello@cgtinker.com.<br>


# License
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

Copyright (C) Denys Hsu - cgtinker, cgtinker.com, hello@cgtinker.com


<br><br>
For tutorials regarding my tools may check out my [YouTube-Channel](https://www.youtube.com/user/MrSerAdos).
If you want to support me you can become a [Patreon](https://www.patreon.com/cgtinker).

