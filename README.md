# BlendArMocap <br>


- Detection of [Mediapipe](https://google.github.io/mediapipe/) detection results in stream or video
- Import of [Freemocap](https://freemocap.org) mediapipe session data
- Calculation of rotations for mediapipe data
- Transfer detected data and generate new transfer configurations
  - currently, officially supports transfer to generated [rifigy rigs](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html)


# Mediapipe Detection

### Purpose<br>
Run mediapipe within blender, detect pose, hand, face or holistic features. 
Calculate rotation data based on the detection results to drive rigs.

### Setup Instructions<br>
To run mediapipe, you need to install the required dependencies [_opencv_](https://opencv.org) and [_mediapipe_](https://google.github.io/mediapipe/) via the add-ons preferences. 
Internet connection is required to install the required packages. It's recommended to disable VPN's during the installation processes. 
Blender may has to be restarted during the installation process. <br>

**Apple User**<br>
Blender has to be started using the terminal when on mac os as blenders plist doesn't contain a camera permissions request. 
To access the webcam feed blender usually has to be started via the terminal when on mac os.
Silicone mac users may need to download the intel version of blender.


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

**Model Complexity**<br>
Complexity of the landmark model: `0 or 1`.
Landmark accuracy as well as inference latency generally go up with the model complexity. 
Default to `1`. The complexity level 2 for pose landmarks is not available due to googles packaging.

**Min Detection Confidence**<br>
Minimum confidence value `[0.0, 1.0]` from the detection model for the detection to be considered successful. Default to `0.5`.

**Start Detection**<br>
When pressing the _Start Detection_ button a window will open which contains the webcam or movie feed and detection results.
The detection results are recorded in Blender at runtime. You can modify the recording starting point by changing the keyframe start in Blender.<br>
May deactivate the rig while detecting if you have transferred animation results previously.
To finish the recording press 'Q' or the "Stop Detection" button.


### Starting Blender with elevated permissions<br>

In some niche cases it might be required to run blender as admin b.e. to install the add-ons external dependencies to run mediapipe.
It shouldn't be required anymore, but if so, here how to do so:

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


# Freemocap import

[Freemocap](https://freemocap.org) session data can be saved in a folder which then can be import using BlendArMocap.
To import session data to blender, set the path to the session directory and press the import button.
There are several import options:<br>

**Import Session** <br>
Import and process data while updating blender by default.<br>

**Quickload Toggle** <br>
Imports the data in one call, faster but blender gets frozen.

**Raw Toggle** <br>
Load raw data - only available if `Quickload` has been toggled.
May not be used to animate rigs - mainly for scientific usuage.<br>

**Load synch videos**<br>
Imports session videos as image planes.<br>


# Transfer

### Concept
Mapping instructions are getting stored as object properties and can be modified in the `objects constraints` panel.
_Only valid for objects containing a specific cgt_id property._

## Transfer Motion (3D View Panel)
**Armature**<br>
Select target armature (b.e. a generated rigify rig for the default config).<br>

**Driver Collection**<br>
Select a collection containing driver objects - `cgt_Drivers` to transfer all.
In some cases you might want to just transfer pose, hands or face - in this case select a specific collection to do so.<br>

**Transfer Type**<br>
Select a transfer type - current support default type is:
- Rigify_Humanoid_DefaultFace_v0.6.1

**Load**<br>
Loads the currently selected type to the transfer objects.

**Save Config**<br>
Save a new config based on the objects in the cgt_Drivers collection.

**Transfer Animation**<br>
Load currently selected config for objects in selected collection and transfer the data.

## Setup New Configs (Object Properties Panel)

The setup process is quite unique, so lets break it down in steps. 
Objects which have been generated during detection contain an ID to display some additional properties in the `object properties panel`.
Those can be modified to either change current mapping properties or even create completely new configs.<br>
Of course, you can just modify an existing config to improve mapping results!

**Concept**<br>
````
mapping_object: object with instructions and constraints
driver_object: generated driver based on instructions
target_object: copies values from driver_object via constraints
````

### Target
Target bone or object which should be driven by constraints.
- Target Type `[Armature, Mesh, Any]`: Apply constraints to target which target driver.
- Sub Target `[Object, Bone]`: Target may be a Bone.

### Drivers
There are three core concepts to set up a mapping. In a nutshell `[Remap Drivers, IK Chain Driver, Remap by Distance Drivers]`.<br>


**Remap Drivers**<br>
Object values (especially rotations) may get remapped using a remap driver.
To do so, navigate to `Value Mapping` and select the properties you want to remap - for example `rotation x, y, z`.<br>
`From min, from max, to min, to max` is used to define slopes, similar to the `map range convertor node` in the shader editor.
Therefore, input the min and max values from the selected object and the to min and max values you want to have as result.
If necessary, you can also use the `factor` and `offset` however, slope can deliver better control one you got the hang of them.<br>
You can do so for all axis separately if necessary, press the `+` icon to do so.<br>
To get some information about the current select object, navigate to `Tools` and press the `Log Object Info` Button, you'll find min and max values from the object in the info panel.<br>

``````
# without remapping object
slope = (to_max - to_min) / (from_max - from_min)
offset = to_min - slope * from_min
f(x) = (slope * property_value + offset) * factor + offset

# with remapping object
slope = (to_max * remapping_value - to_min * remapping_value) / (from_max - from_min)
offset = to_min - slope * from_min * remapping_value
f(x) = (slope * property_value + offset) * factor + offset
``````

**IK Chain Drivers**<br>
The idea of ik chain drivers is to construct an ik chain in reverse order.<br>
The end of the ik chain neither has a parent and nor gets remapped.
The next chain link has the chain end as parent, and gets remapped by the bone length separating the targets.
Repeat this till you are at the ik start. As Example:<br>
`````
objects: shoulder_obj -> elbow_obj -> hand_obj
bones: shoulder_bone -> elbow_bone -> hand_bone

shoulder_obj(target=shoulder_bone, parent=None, remap_bone=None)
elbow_obj(target=elbow_bone, parent=shoulder_obj, remap_bone=shoulder_bone.length)
hand_obj(target=hand_bone, parent=elbow_obj, remap_bone=elbow_bone.length)

Recursivly applies:
dist = distance between parent and obj
f(x) = (dist / remap_bone_length) * (obj_location - previous_chain_obj_location)
`````
Checkout the rigify rig implementation of the arms as example setup.<br>


**Remap Drivers by Distance**<br>
When using remap drivers by distance, we aren't using any of the object values.
In this case, a distance between two objects gets used as driver value, which then gets remapped similar to a remap driver.
The single difference is that the offset gets multiplied by the remapping value, which allows to basically offset in % (which usually isn't wanted for rotations).
However, this time it makes a lot of scene to remap the value by a bone of the target armature as we are working with position and not rotation data - this makes remapping the values a lot easier.
Again, to get some information about the current select object, navigate to `Tools` and press the `Log Object Info` Button, you'll find min and max values from the object in the info panel.<br>
``````
slope = (to_max * remapping_value - to_min * remapping_value) / (from_max - from_min)
offset = to_min * remapping_value - slope * from_min
f(x) = (slope * property_value + offset) * factor + offset * remapping_value
``````

### Constraints

Finally, add constraints to the object - the constraints will get applied to the target when transferring.
As mentioned in the beginning, the target objects copies values from the driver using constraints.
You may use any constraint to do so and modify the constraint properties to your likings to adjust transfer results.


### Tools

**Transfer Selection**<br>
Run transfer only for selected objects. When transferring chains the entire chain has to be selected, not just a link.<br>

**Smooth Animation Data**<br>
Run Blenders internal smooth f-Curves for selected objects.

**Log Object Info**<br>
Log min, max values and infos about the selected object to the `info panel`.

## I/O Transfer Configuration (Topbar Import/ Export)

Transfer configurations can be imported and exported. 
If you create a new configuration and want to share it with the community let me know via hello@cgtinker.com =)


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