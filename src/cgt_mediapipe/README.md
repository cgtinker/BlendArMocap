# Mediapipe

### Purpose<br>
Run mediapipe within blender, detect pose, hand, face or holistic features. 
Calculate rotation data based on the detection results to drive rigs.

### Setup Instructions<br>
Blender has to be started using the terminal when on mac as blenders plist doesn't contain camera permissions. 
To run mediapipe, you need to install the required dependencies [_opencv_](https://opencv.org) and [_mediapipe_](https://google.github.io/mediapipe/) via the add-ons preferences. 
Internet connection is required to install the required packages. It's recommended to disable VPN's during the installation processes. 
Also Blender may has to be restarted during the installation process. To access the webcam feed blender usually has to be started via the terminal.

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

